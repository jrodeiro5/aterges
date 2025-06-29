import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from supabase import create_client, Client
import logging

from config import settings

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, database):
        self.database = database
        self.supabase: Client = create_client(
            settings.supabase_url, 
            settings.supabase_key
        )
    
    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except jwt.PyJWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    async def signup(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user using Supabase Auth with better UX response."""
        try:
            logger.info(f"Attempting signup for email: {email}")
            
            # Use Supabase's built-in authentication
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            logger.info(f"Supabase signup response: user={response.user is not None}, session={response.session is not None}")
            
            if response.user is None:
                logger.error("Supabase returned None user in signup response")
                raise ValueError("Failed to create user account")
            
            user = response.user
            logger.info(f"User created: id={user.id}, email={user.email}, confirmed_at={user.email_confirmed_at}")
            
            # Check if email confirmation is required
            email_confirmed = user.email_confirmed_at is not None
            
            if email_confirmed:
                # User is already confirmed, create token
                token_data = {"sub": user.id, "email": user.email}
                access_token = self._create_access_token(token_data)
                
                return {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.user_metadata.get("name")
                    },
                    "token": access_token,
                    "email_confirmed": True,
                    "message": "Account created and you're now logged in!"
                }
            else:
                # Email confirmation required
                return {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.user_metadata.get("name")
                    },
                    "token": None,
                    "email_confirmed": False,
                    "message": "Account created! Please check your email and click the confirmation link to complete your registration.",
                    "next_step": "confirm_email"
                }
            
        except Exception as e:
            logger.error(f"Signup error for {email}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            
            # Check if it's a duplicate email error
            error_msg = str(e).lower()
            if "already registered" in error_msg or "already exists" in error_msg or "duplicate" in error_msg:
                raise ValueError("This email is already registered. Try logging in instead.")
            elif "invalid email" in error_msg or "email" in error_msg and "invalid" in error_msg:
                raise ValueError("Please enter a valid email address.")
            elif "password" in error_msg and ("weak" in error_msg or "short" in error_msg):
                raise ValueError("Password must be at least 6 characters long.")
            else:
                raise ValueError(f"Failed to create user account: {str(e)}")
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with detailed error handling for email confirmation."""
        try:
            logger.info(f"Attempting login for email: {email}")
            
            # Use Supabase's built-in authentication
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            logger.info(f"Supabase login response: user={response.user is not None}, session={response.session is not None}")
            
            if response.user is None:
                logger.warning(f"Login failed for {email} - no user returned")
                # Check if user exists but isn't confirmed
                user_status = await self.check_user_status(email)
                if user_status["exists"] and not user_status["confirmed"]:
                    return {
                        "success": False,
                        "error": "email_not_confirmed",
                        "message": "Please check your email and click the confirmation link before logging in.",
                        "user_email": email,
                        "can_resend": True
                    }
                else:
                    return {
                        "success": False,
                        "error": "invalid_credentials",
                        "message": "Invalid email or password. Please check your credentials and try again."
                    }
            
            user = response.user
            logger.info(f"Login successful for {email}: user_id={user.id}")
            
            # Create our own access token for API access
            token_data = {"sub": user.id, "email": user.email}
            access_token = self._create_access_token(token_data)
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.user_metadata.get("name")
                },
                "token": access_token,
                "message": "Login successful! Welcome back."
            }
            
        except Exception as e:
            logger.error(f"Login error for {email}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            
            error_msg = str(e).lower()
            
            # Handle specific error cases
            if "email not confirmed" in error_msg:
                return {
                    "success": False,
                    "error": "email_not_confirmed",
                    "message": "Please check your email and click the confirmation link before logging in.",
                    "user_email": email,
                    "can_resend": True
                }
            elif "invalid" in error_msg and ("password" in error_msg or "credentials" in error_msg):
                return {
                    "success": False,
                    "error": "invalid_credentials", 
                    "message": "Invalid email or password. Please check your credentials and try again."
                }
            else:
                return {
                    "success": False,
                    "error": "login_failed",
                    "message": "Login failed. Please try again or contact support if the problem persists."
                }
    
    async def check_user_status(self, email: str) -> Dict[str, Any]:
        """Check if user exists and their email confirmation status."""
        try:
            # Query the auth.users table directly (if we have service role access)
            # For now, we'll use a simple approach
            response = self.supabase.table('profiles').select('*').eq('email', email).execute()
            
            if response.data:
                return {"exists": True, "confirmed": True}  # Profile exists means confirmed
            else:
                # User might exist but not confirmed (no profile created yet)
                return {"exists": False, "confirmed": False}
        except Exception as e:
            logger.error(f"Error checking user status: {e}")
            return {"exists": False, "confirmed": False}
    
    async def resend_confirmation(self, email: str) -> Dict[str, Any]:
        """Resend email confirmation."""
        try:
            response = self.supabase.auth.resend({
                "type": "signup",
                "email": email
            })
            
            return {
                "success": True,
                "message": f"Confirmation email sent to {email}. Please check your inbox and spam folder."
            }
            
        except Exception as e:
            logger.error(f"Resend confirmation error: {e}")
            return {
                "success": False,
                "message": "Failed to resend confirmation email. Please try again later."
            }
    
    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user from token."""
        try:
            payload = self._verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Get user profile from our profiles table
            response = self.supabase.table('profiles').select('*').eq('id', user_id).execute()
            
            if not response.data:
                # If profile doesn't exist, try to get from auth.users
                try:
                    auth_response = self.supabase.auth.get_user(token)
                    if auth_response.user:
                        return {
                            "id": auth_response.user.id,
                            "email": auth_response.user.email,
                            "name": auth_response.user.user_metadata.get("name")
                        }
                except:
                    pass
                return None
            
            profile = response.data[0]
            return {
                "id": profile["id"],
                "email": profile["email"],
                "name": profile.get("name")
            }
            
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            return None
