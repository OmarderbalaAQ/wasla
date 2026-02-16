from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models
from routers import auth, payments, admin, contacts
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi import Request
import time

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Simple Auth Payments API")

# Add rate limiter to app state
app.state.limiter = limiter

# Custom rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error messages based on endpoint"""
    path = request.url.path
    
    if "/auth/login" in path:
        return JSONResponse(
            status_code=429,
            content={
                "error": "too_many_login_attempts",
                "message": "Too many login attempts. Please wait 1 minute before trying again.",
                "retry_after": 60,
                "attempts_allowed": 5,
                "time_window": "1 minute"
            }
        )
    elif "/auth/register" in path:
        return JSONResponse(
            status_code=429,
            content={
                "error": "too_many_registration_attempts", 
                "message": "Too many registration attempts. Please wait 1 minute before trying again.",
                "retry_after": 60,
                "attempts_allowed": 5,
                "time_window": "1 minute"
            }
        )
    elif "/payments/" in path:
        return JSONResponse(
            status_code=429,
            content={
                "error": "too_many_payment_attempts",
                "message": "Too many payment attempts. Please wait 1 minute before trying again.",
                "retry_after": 60,
                "attempts_allowed": 10,
                "time_window": "1 minute",
                "suggestion": "If you're having payment issues, please contact support."
            }
        )
    else:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please wait before trying again.",
                "retry_after": 60
            }
        )

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # XSS Protection (legacy but still useful)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Content Security Policy - More permissive for development
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' js.stripe.com; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
        "font-src 'self' fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' localhost:8000 127.0.0.1:8000; "
        "frame-ancestors 'none'"
    )
    
    # HSTS (only add in production with HTTPS)
    # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# CORS Configuration - MUST be before mounting static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # Development
        "http://127.0.0.1:8000",  # Development
        "https://wasla.example.com",  # TODO: Replace with actual domain
        "https://api.wasla.example.com",  # TODO: Replace with actual API domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files AFTER CORS
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def seed_bundles():
    """Seed initial bundles if they don't exist"""
    db = SessionLocal()
    try:
        bundle_count = db.query(models.Bundle).count()
        if bundle_count == 0:
            basic_bundle = models.Bundle(
                name="Basic Bundle",
                price_cents=1000,
                currency="usd",
                is_active=True
            )
            pro_bundle = models.Bundle(
                name="Pro Bundle",
                price_cents=5000,
                currency="usd",
                is_active=True
            )
            db.add(basic_bundle)
            db.add(pro_bundle)
            db.commit()
            print("✓ Seeded initial bundles")
    finally:
        db.close()


# Include routers with rate limiting
app.include_router(auth.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(contacts.router)

# Apply rate limiting to specific endpoints
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to specific endpoints"""
    path = request.url.path
    method = request.method
    
    # Get client IP
    client_ip = get_remote_address(request)
    
    # Define rate limits for different endpoints
    rate_limits = {
        ("POST", "/auth/login"): ("5/minute", "too_many_login_attempts", "Too many login attempts. Please wait 1 minute before trying again."),
        ("POST", "/auth/register"): ("5/minute", "too_many_registration_attempts", "Too many registration attempts. Please wait 1 minute before trying again."),
        ("POST", "/payments/create-payment-intent"): ("10/minute", "too_many_payment_attempts", "Too many payment attempts. Please wait 1 minute before trying again."),
        ("POST", "/contacts/submit"): ("3/5minutes", "too_many_contact_submissions", "You can only submit the contact form 3 times per 5 minutes. Please try again later."),
    }
    
    # Check if this endpoint needs rate limiting
    endpoint_key = (method, path)
    if endpoint_key in rate_limits:
        limit_str, error_code, error_message = rate_limits[endpoint_key]
        
        # Parse limit (e.g., "5/minute" -> 5 requests per 60 seconds, "3/5minutes" -> 3 requests per 300 seconds)
        limit_parts = limit_str.split("/")
        max_requests = int(limit_parts[0])
        
        # Determine time window
        if limit_parts[1] == "minute":
            time_window = 60
        elif limit_parts[1] == "hour":
            time_window = 3600
        elif limit_parts[1].endswith("minutes"):
            # Extract number from "5minutes" -> 5
            minutes = int(limit_parts[1].replace("minutes", ""))
            time_window = minutes * 60
        else:
            time_window = 60  # default to 1 minute
        
        # Simple in-memory rate limiting (for production, use Redis)
        if not hasattr(app.state, 'rate_limit_storage'):
            app.state.rate_limit_storage = {}
        
        storage = app.state.rate_limit_storage
        key = f"{client_ip}:{path}"
        current_time = time.time()
        
        # Clean old entries
        if key in storage:
            storage[key] = [timestamp for timestamp in storage[key] if current_time - timestamp < time_window]
        else:
            storage[key] = []
        
        # Check if limit exceeded
        if len(storage[key]) >= max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": error_code,
                    "message": error_message,
                    "retry_after": 60,
                    "attempts_allowed": max_requests,
                    "time_window": "1 minute"
                }
            )
        
        # Add current request
        storage[key].append(current_time)
    
    response = await call_next(request)
    return response


@app.get("/")
def root():
    return {"message": "Simple Auth Payments API"}
