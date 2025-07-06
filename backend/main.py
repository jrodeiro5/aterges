from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import os
from typing import Dict, Any, Optional

# Supabase imports for authentication
from supabase import create_client, Client
from gotrue.errors import AuthError

from config import settings
from auth.auth_service_improved import AuthService
from auth.models import UserSignup, UserLogin, UserResponse
from database.database import Database

# AI Orchestrator import
from ai.orchestrator import AIOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize Supabase client for authentication
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    logger.error("Supabase configuration missing. SUPABASE_URL and SUPABASE_KEY are required.")
    supabase_auth_client: Optional[Client] = None
else:
    try:
        supabase_auth_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase auth client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase auth client: {e}")
        supabase_auth_client = None

# Global variables for dependencies
auth_service: AuthService = None
database: Database = None
ai_orchestrator: AIOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global auth_service, database, ai_orchestrator
    
    # Startup
    logger.info("Starting Aterges AI Backend...")
    
    # Initialize database
    database = Database()
    await database.connect()
    
    # Initialize auth service
    auth_service = AuthService(database)
    
    # Initialize AI Orchestrator (Phase 1)
    try:
        # Validate Google Cloud configuration
        if not settings.validate_google_cloud_config():
            logger.warning("Google Cloud configuration incomplete:")
            logger.warning(f"  - Project ID: {'✓' if settings.google_cloud_project else '✗'}")
            logger.warning(f"  - Credentials file: {'✓' if settings.google_application_credentials else '✗'}")
            logger.warning(f"  - File exists: {'✓' if settings.google_application_credentials and os.path.exists(settings.google_application_credentials) else '✗'}")
            logger.warning("AI features will be unavailable until configuration is complete")
            logger.warning("See ATERGES_INDEPENDENT_SETUP.md for setup instructions")
        else:
            ai_orchestrator = AIOrchestrator(
                project_id=settings.google_cloud_project,
                location=settings.google_cloud_location
            )
            logger.info("AI Orchestrator initialized successfully")
            logger.info(f"Using Google Cloud project: {settings.google_cloud_project}")
            logger.info(f"GA4 Property ID: {settings.ga4_property_id or 'Not configured'}")
            
    except Exception as e:
        logger.error(f"Failed to initialize AI Orchestrator: {e}")
        logger.warning("AI features will be unavailable")
        logger.warning("Check your Google Cloud credentials and configuration")
    
    logger.info("Backend initialization complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend...")
    if database:
        await database.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for Aterges AI Platform - AI Orchestrator with Google Analytics Integration",
    version="1.3.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Dependency to get current user using Supabase authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from Supabase token.
    """
    try:
        if not supabase_auth_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        # Verify the token with Supabase
        try:
            user_response = supabase_auth_client.auth.get_user(token)
            
            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Return user data in the expected format
            return {
                "id": user_response.user.id,
                "email": user_response.user.email,
                "name": user_response.user.user_metadata.get("name") if user_response.user.user_metadata else None
            }
            
        except AuthError as e:
            logger.warning(f"Supabase auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication system error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system error",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    ai_status = "available" if ai_orchestrator else "unavailable"
    config_status = "complete" if settings.validate_google_cloud_config() else "incomplete"
    
    # Get the actual port from environment (Cloud Run sets this automatically)
    current_port = os.environ.get("PORT", "8000")
    
    return {
        "status": "healthy", 
        "message": "Aterges AI Backend is running",
        "version": "1.3.0 - AI Orchestrator Fixed",
        "port": current_port,
        "services": {
            "database": "connected" if database else "disconnected",
            "auth_service": "available" if auth_service else "unavailable",
            "ai_orchestrator": ai_status
        },
        "cors_origins": settings.get_cors_origins_list(),
        "environment_check": {
            "SUPABASE_URL": "set" if os.environ.get("SUPABASE_URL") else "missing",
            "DATABASE_URL": "set" if os.environ.get("DATABASE_URL") else "missing",
            "SECRET_KEY": "set" if os.environ.get("SECRET_KEY") else "missing",
            "GOOGLE_CLOUD_PROJECT": settings.google_cloud_project or "not set",
            "GA4_PROPERTY_ID": "set" if settings.ga4_property_id else "not set"
        }
    }


# AI status endpoint
@app.get("/api/ai/status")
async def ai_status(current_user = Depends(get_current_user)):
    """Get AI system status."""
    if not ai_orchestrator:
        config_issues = []
        if not settings.google_cloud_project:
            config_issues.append("GOOGLE_CLOUD_PROJECT not set")
        if not settings.google_application_credentials:
            config_issues.append("GOOGLE_APPLICATION_CREDENTIALS not set")
        elif not os.path.exists(settings.google_application_credentials):
            config_issues.append("Service account file not found")
        
        return {
            "status": "unavailable", 
            "message": "AI Orchestrator not initialized",
            "configuration_issues": config_issues,
            "setup_guide": "See ATERGES_INDEPENDENT_SETUP.md"
        }
    
    try:
        status = ai_orchestrator.get_agent_status()
        return {"status": "available", "details": status}
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        return {"status": "error", "message": str(e)}


# Authentication endpoints
@app.post("/auth/signup")
async def signup(user_data: UserSignup):
    """Register a new user with clear email confirmation messaging."""
    try:
        result = await auth_service.signup(user_data.email, user_data.password)
        
        if result.get("email_confirmed", False):
            # User can login immediately
            return {
                "user": result["user"],
                "token": result["token"],
                "message": result["message"],
                "next_step": "dashboard"
            }
        else:
            # Email confirmation required
            return {
                "user": result["user"],
                "message": result["message"],
                "email_confirmed": False,
                "next_step": "confirm_email",
                "help": "Check your email (including spam folder) and click the confirmation link."
            }
            
    except ValueError as e:
        error_msg = str(e)
        if "already registered" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "email_exists",
                    "message": error_msg,
                    "help": "Try logging in instead, or use 'Forgot Password' if you can't remember your password."
                }
            )
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/login")
async def login(user_data: UserLogin):
    """Authenticate user with detailed error messages for email confirmation."""
    try:
        result = await auth_service.login(user_data.email, user_data.password)
        
        if result.get("success", False):
            return {
                "user": result["user"],
                "token": result["token"],
                "message": result["message"]
            }
        else:
            # Return specific error information
            if result["error"] == "email_not_confirmed":
                raise HTTPException(
                    status_code=400,  # Use 400 instead of 401 for better UX
                    detail={
                        "error": "email_not_confirmed",
                        "message": result["message"],
                        "user_email": result.get("user_email"),
                        "can_resend": result.get("can_resend", False),
                        "help": "Click 'Resend confirmation email' if you didn't receive it."
                    }
                )
            elif result["error"] == "invalid_credentials":
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "invalid_credentials",
                        "message": result["message"],
                        "help": "Double-check your email and password."
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": result["error"],
                        "message": result["message"]
                    }
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/logout")
async def logout():
    """Logout endpoint (client-side token removal)."""
    return {"message": "Successfully logged out"}


@app.post("/auth/resend-confirmation")
async def resend_confirmation(request_data: dict):
    """Resend email confirmation for a user."""
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Use the improved auth service method
        result = await auth_service.resend_confirmation(email)
        
        if result["success"]:
            return {
                "message": result["message"],
                "success": True
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend confirmation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/check-status")
async def check_user_status(request_data: dict):
    """Check if user exists and their confirmation status."""
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        status = await auth_service.check_user_status(email)
        return {
            "email": email,
            "exists": status["exists"],
            "confirmed": status["confirmed"]
        }
        
    except Exception as e:
        logger.error(f"Check user status error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Protected endpoints
@app.get("/api/me", response_model=dict)
async def get_me(current_user = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user.get("name")
    }


# AI Query endpoint - Phase 1 Implementation
@app.post("/api/query")
async def query_ai(
    query_data: dict,
    current_user = Depends(get_current_user)
):
    """Process AI query using the AI Orchestrator."""
    prompt = query_data.get("prompt", "")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    if not ai_orchestrator:
        return {
            "response": "I apologize, but the AI system is currently unavailable. Please ensure your Google Cloud configuration is complete. Check the server logs or visit /api/ai/status for more details.",
            "status": "ai_unavailable",
            "help": "See ATERGES_INDEPENDENT_SETUP.md for configuration instructions"
        }
    
    try:
        # Prepare user context for the AI
        user_context = {
            "email": current_user.get("email"),
            "user_id": current_user.get("id"),
            "name": current_user.get("name")
        }
        
        # Process the query through the AI Orchestrator
        logger.info(f"Processing AI query for user {user_context['email']}: {prompt[:100]}...")
        
        response = await ai_orchestrator.process_query(
            user_query=prompt,
            user_context=user_context
        )
        
        logger.info(f"AI query processed successfully for user {user_context['email']}")
        
        return {
            "response": response,
            "status": "success",
            "timestamp": "2025-06-28T00:00:00Z"  # Current timestamp
        }
        
    except Exception as e:
        logger.error(f"Error processing AI query for user {current_user.get('email')}: {e}")
        return {
            "response": f"I encountered an error while processing your request: {str(e)}. Please try again or contact support if the issue persists.",
            "status": "error"
        }


# Agent health check endpoint
@app.get("/api/agents/health")
async def agents_health_check(current_user = Depends(get_current_user)):
    """Check health of all data agents."""
    if not ai_orchestrator:
        return {
            "status": "unavailable", 
            "message": "AI Orchestrator not initialized",
            "help": "See ATERGES_INDEPENDENT_SETUP.md for configuration instructions"
        }
    
    try:
        health_results = {}
        
        for agent_name, agent in ai_orchestrator.agents.items():
            health_results[agent_name] = await agent.health_check()
        
        return {
            "status": "checked",
            "agents": health_results,
            "total_agents": len(health_results)
        }
        
    except Exception as e:
        logger.error(f"Error checking agent health: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable for Cloud Run, default to 8000 for local development
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug
    )
