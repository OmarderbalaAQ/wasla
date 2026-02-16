from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from utils.security import hash_password, verify_password, create_access_token, decode_access_token
from schemas import UserCreate, UserResponse, Token, UserLogin
import models

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> models.User:
    """Get current user from httpOnly cookie"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from cookie first
    token = request.cookies.get("access_token")
    
    # Fallback to Authorization header for API compatibility
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise credentials_exception
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Original function for API compatibility"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


# Role-based authorization helpers
def require_role(allowed_roles: List[str]):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: models.User = Depends(get_current_user_from_cookie)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def require_admin(current_user: models.User = Depends(get_current_user_from_cookie)):
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required"
        )
    return current_user


def require_admin_or_accountant(current_user: models.User = Depends(get_current_user_from_cookie)):
    """Require admin or accountant role"""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or accountant role required"
        )
    return current_user


def require_admin_or_technical(current_user: models.User = Depends(get_current_user_from_cookie)):
    """Require admin or technical role"""
    if current_user.role not in ["admin", "technical"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or technical role required"
        )
    return current_user


def require_lead_access(current_user: models.User = Depends(get_current_user_from_cookie)):
    """Require admin, accountant, or salesman role (lead access)"""
    if current_user.role not in ["admin", "accountant", "salesman"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin, accountant, or salesman role required"
        )
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = models.User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False,
        role="user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user by email (username field in OAuth2 form)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Set httpOnly cookie (secure against XSS)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access
        secure=False,   # Set to True for HTTPS in production
        samesite="lax", # Changed from "strict" for better compatibility
        max_age=1800,   # 30 minutes (same as JWT expiry)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: models.User = Depends(get_current_user_from_cookie)):
    return current_user


@router.get("/me/subscription")
def get_my_subscription(current_user: models.User = Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    """Get current user's active subscription and dashboard access"""
    from datetime import datetime
    
    # Check if admin granted access without subscription
    if current_user.allow_access_without_subscription:
        dashboard = db.query(models.Dashboard).filter(models.Dashboard.user_id == current_user.id).first()
        return {
            "has_access": True,
            "has_active_subscription": False,
            "admin_override": True,
            "dashboard_url": dashboard.looker_studio_url if dashboard else None,
            "subscription_end_date": None,
            "bundle_name": None
        }
    
    # Find the most recent active subscription
    active_sub = db.query(models.Subscription).filter(
        models.Subscription.user_id == current_user.id,
        models.Subscription.is_active == True,
        models.Subscription.end_date > datetime.utcnow()
    ).order_by(models.Subscription.end_date.desc()).first()
    
    if active_sub:
        dashboard = db.query(models.Dashboard).filter(models.Dashboard.user_id == current_user.id).first()
        bundle = db.query(models.Bundle).filter(models.Bundle.id == active_sub.bundle_id).first()
        
        return {
            "has_access": True,
            "has_active_subscription": True,
            "admin_override": False,
            "dashboard_url": dashboard.looker_studio_url if dashboard else None,
            "subscription_end_date": active_sub.end_date.isoformat(),
            "bundle_name": bundle.name if bundle else None
        }
    
    return {
        "has_access": False,
        "has_active_subscription": False,
        "admin_override": False,
        "dashboard_url": None,
        "subscription_end_date": None,
        "bundle_name": None
    }


@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing the httpOnly cookie"""
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # Set to True for HTTPS in production
        samesite="lax"
    )
    return {"message": "Successfully logged out"}
