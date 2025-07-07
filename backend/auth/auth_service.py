import jwt
import os
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
        """Verify JWT token using Supabase JWT secret."""
        try:
            # Get the Supabase JWT secret from environment
            jwt_secret = os.environ.get("SUPABASE_JWT_SECRET")
            
            if jwt_secret:
                # Use Supabase JWT secret for proper verification
                payload = jwt.decode(
                    token, 
                    jwt_secret, 
                    algorithms=["HS256"],
                    options={"verify_aud": True, "verify_exp": True},
                    audience="authenticated"  # Supabase uses "authenticated" as audience
                )
                logger.info(f"JWT verified with Supabase secret for user: {payload.get('email')}")
                return payload
            else:
                # Fallback to original method if no Supabase secret
                logger.warning("No SUPABASE_JWT_SECRET found, using fallback verification")
                payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
                return payload
                
        except jwt.PyJWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    async def signup(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user using Supabase Auth."""
        try:
            # Use Supabase's built-in authentication
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user is None:
                raise ValueError("Failed to create user account")
            
            user = response.user
            
            # Create our own access token for API access
            token_data = {"sub": user.id, "email": user.email}
            access_token = self._create_access_token(token_data)
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.user_metadata.get("name")
                },
                "token": access_token
            }
            
        except Exception as e:
            logger.error(f"Signup error: {e}")
            raise ValueError(f"Failed to create user account: {str(e)}")
    
    async def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user using Supabase Auth."""
        try:
            # Use Supabase's built-in authentication
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user is None:
                return None
            
            user = response.user
            
            # Create our own access token for API access
            token_data = {"sub": user.id, "email": user.email}
            access_token = self._create_access_token(token_data)
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.user_metadata.get("name")
                },
                "token": access_token
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return None
    
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
