from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import os

from config import settings
from auth.auth_service import AuthService
from auth.models import UserSignup, UserLogin, UserResponse
from database.database import Database

# AI Orchestrator import
from ai.orchestrator import AIOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

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
    description="Backend API for Aterges AI Platform - Phase 1 with AI Orchestrator",
    version="1.2.0",
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


# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    ai_status = "available" if ai_orchestrator else "unavailable"
    config_status = "complete" if settings.validate_google_cloud_config() else "incomplete"
    
    return {
        "status": "healthy", 
        "message": "Aterges AI Backend is running",
        "version": "1.2.0 - Phase 1",
        "ai_orchestrator": ai_status,
        "google_cloud_config": config_status,
        "project_id": settings.google_cloud_project or "not configured",
        "ga4_configured": bool(settings.ga4_property_id),
        "cors_origins": settings.get_cors_origins_list()
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
@app.post("/auth/signup", response_model=UserResponse)
async def signup(user_data: UserSignup):
    """Register a new user."""
    try:
        result = await auth_service.signup(user_data.email, user_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/login", response_model=UserResponse)
async def login(user_data: UserLogin):
    """Authenticate user and return JWT token."""
    try:
        result = await auth_service.login(user_data.email, user_data.password)
        if not result:
            raise HTTPException(
                status_code=401, 
                detail="Invalid email or password"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/logout")
async def logout():
    """Logout endpoint (client-side token removal)."""
    return {"message": "Successfully logged out"}


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
