from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import os
import traceback

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Global variables for dependencies - initialized as None
auth_service = None
database = None
ai_orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with graceful error handling."""
    global auth_service, database, ai_orchestrator
    
    # Startup
    logger.info("Starting Aterges AI Backend...")
    logger.info(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
    
    # Initialize database with error handling
    try:
        from database.database import Database
        database = Database()
        await database.connect()
        logger.info("✅ Database connected successfully")
        
        # Initialize auth service only if database works
        from auth.auth_service import AuthService
        auth_service = AuthService(database)
        logger.info("✅ Auth service initialized")
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.warning("🟡 App will start without database functionality")
    
    # Initialize AI Orchestrator with error handling
    try:
        if settings.validate_google_cloud_config():
            from ai.orchestrator import AIOrchestrator
            ai_orchestrator = AIOrchestrator(
                project_id=settings.google_cloud_project,
                location=settings.google_cloud_location
            )
            logger.info("✅ AI Orchestrator initialized successfully")
        else:
            logger.warning("🟡 Google Cloud configuration incomplete - AI features disabled")
            
    except Exception as e:
        logger.error(f"❌ AI Orchestrator initialization failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.warning("🟡 App will start without AI functionality")
    
    logger.info("🚀 Backend initialization complete - Server starting...")
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend...")
    if database:
        try:
            await database.disconnect()
            logger.info("✅ Database disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting database: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend API for Aterges AI Platform - Phase 1 with Error Recovery",
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


# Dependency to get current user with error handling
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable - database not connected"
        )
    
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


# Health check endpoint - always works
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    services_status = {
        "database": "connected" if database else "disconnected",
        "auth_service": "available" if auth_service else "unavailable", 
        "ai_orchestrator": "available" if ai_orchestrator else "unavailable",
    }
    
    return {
        "status": "healthy", 
        "message": "Aterges AI Backend is running",
        "version": "1.3.0 - Error Recovery",
        "port": os.environ.get("PORT", "8000"),
        "services": services_status,
        "cors_origins": settings.get_cors_origins_list(),
        "environment_check": {
            "SUPABASE_URL": "set" if settings.supabase_url else "missing",
            "DATABASE_URL": "set" if settings.database_url else "missing", 
            "SECRET_KEY": "set" if settings.secret_key else "missing",
            "SUPABASE_JWT_SECRET": "set" if os.environ.get("SUPABASE_JWT_SECRET") else "missing",
            "GOOGLE_CLOUD_PROJECT": settings.google_cloud_project or "missing",
            "GA4_PROPERTY_ID": "set" if settings.ga4_property_id else "missing"
        }
    }


# Simple root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Aterges AI Backend API",
        "version": "1.3.0",
        "docs": "/docs",
        "health": "/health"
    }


# AI status endpoint with error handling
@app.get("/api/ai/status")
async def ai_status():
    """Get AI system status - no auth required for testing."""
    if not ai_orchestrator:
        return {
            "status": "unavailable", 
            "message": "AI Orchestrator not initialized",
            "google_cloud_config": settings.validate_google_cloud_config(),
            "project_id": settings.google_cloud_project or "not set"
        }
    
    try:
        status = ai_orchestrator.get_agent_status()
        return {"status": "available", "details": status}
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        return {"status": "error", "message": str(e)}


# Authentication endpoints with error handling
@app.post("/auth/signup")
async def signup(user_data: dict):
    """Register a new user."""
    if not auth_service:
        raise HTTPException(
            status_code=503, 
            detail="Authentication service unavailable - database not connected"
        )
    
    try:
        from auth.models import UserSignup
        signup_data = UserSignup(**user_data)
        result = await auth_service.signup(signup_data.email, signup_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/login")
async def login(user_data: dict):
    """Authenticate user and return JWT token."""
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable - database not connected"
        )
    
    try:
        from auth.models import UserLogin
        login_data = UserLogin(**user_data)
        result = await auth_service.login(login_data.email, login_data.password)
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


# Protected endpoints
@app.get("/api/me")
async def get_me(current_user = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user.get("name")
    }


# AI Query endpoint with error handling
@app.post("/api/query")
async def query_ai(query_data: dict, current_user = Depends(get_current_user)):
    """Process AI query using the AI Orchestrator."""
    prompt = query_data.get("prompt", "")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    if not ai_orchestrator:
        return {
            "response": "I apologize, but the AI system is currently unavailable. The Google Cloud configuration may be incomplete or the AI Orchestrator failed to initialize. Please check the server logs or contact support.",
            "status": "ai_unavailable"
        }
    
    try:
        user_context = {
            "email": current_user.get("email"),
            "user_id": current_user.get("id"),
            "name": current_user.get("name")
        }
        
        logger.info(f"Processing AI query for user {user_context['email']}: {prompt[:100]}...")
        
        # Process the query through the AI Orchestrator
        response = await ai_orchestrator.process_query(
            user_query=prompt,
            user_context=user_context
        )
        
        logger.info(f"AI query processed successfully for user {user_context['email']}")
        
        return {
            "response": response,
            "status": "success",
            "timestamp": "2025-07-07T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error processing AI query: {e}")
        return {
            "response": f"I encountered an error while processing your request: {str(e)[:200]}. This appears to be a technical issue with my AI system. Please try again with a simpler question or contact support.",
            "status": "error"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.port))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(
        "main_robust:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level="info"
    )
