# Enhanced authentication endpoints with better UX for email confirmation
# Add these to your main_robust.py file

# Additional endpoints to add:

@app.post("/auth/resend-confirmation")
async def resend_confirmation(request_data: dict):
    """Resend email confirmation for a user."""
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable - database not connected"
        )
    
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
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable - database not connected"
        )
    
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


# Updated login endpoint with better error handling
@app.post("/auth/login")
async def login_improved(user_data: dict):
    """Authenticate user with detailed error messages for email confirmation."""
    if not auth_service:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable - database not connected"
        )
    
    try:
        from auth.models import UserLogin
        login_data = UserLogin(**user_data)
        result = await auth_service.login(login_data.email, login_data.password)
        
        if result["success"]:
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


# Updated signup endpoint with better messaging
@app.post("/auth/signup")
async def signup_improved(user_data: dict):
    """Register a new user with clear email confirmation messaging."""
    if not auth_service:
        raise HTTPException(
            status_code=503, 
            detail="Authentication service unavailable - database not connected"
        )
    
    try:
        from auth.models import UserSignup
        signup_data = UserSignup(**user_data)
        result = await auth_service.signup(signup_data.email, signup_data.password)
        
        if result["email_confirmed"]:
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
