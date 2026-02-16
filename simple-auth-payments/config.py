from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # Email Configuration (Optional - for future use)
    # These are loaded by utils/email.py directly from environment
    # but can be accessed here if needed
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = "Wasla Notifications"
    ADMIN_EMAILS: Optional[str] = None
    ADMIN_PANEL_URL: Optional[str] = "http://localhost:8000/admin.html"
    ENABLE_EMAIL_NOTIFICATIONS: Optional[bool] = False

    class Config:
        env_file = ".env"


settings = Settings()
