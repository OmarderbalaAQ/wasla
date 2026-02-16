from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=72)  # bcrypt limit
    full_name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=72)  # bcrypt limit


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class BundleResponse(BaseModel):
    id: int
    name: str = Field(..., max_length=255)
    price_cents: int
    currency: str = Field(..., max_length=10)
    is_active: bool
    tier_level: Optional[int] = 1
    logo_type: Optional[str] = Field("silver", max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    main_description: Optional[str] = Field(None, max_length=1000)

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    bundle_id: int = Field(..., gt=0)  # Must be positive
    months: int = Field(1, ge=1, le=24)  # 1-24 months limit


# Contact Form Schemas

class ContactRequestCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., max_length=255)
    phone: str = Field(..., min_length=1, max_length=20, pattern=r'^[0-9\s\-\+\(\)]+$')
    country_code: str = Field(..., min_length=2, max_length=10, pattern=r'^\+[0-9]+$')
    country: str = Field(..., min_length=1, max_length=100)
    business_name: str = Field(..., min_length=1, max_length=255)
    num_locations: str = Field(..., pattern=r'^(1|2-5|6-10|11-25|25-50|\+50)$')
    referral_source: str = Field(..., pattern=r'^(social|search|referral|other)$')
    marketing_consent: bool = False
    language_preference: str = Field(default="en", pattern=r'^(en|ar)$')


class ContactRequestResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    country_code: str
    country: str
    business_name: str
    num_locations: str
    referral_source: str
    marketing_consent: bool
    language_preference: str
    status: str
    created_at: datetime
    updated_at: datetime
    notes_count: Optional[int] = 0
    assigned_to: Optional[dict] = None  # {id, email, full_name}

    class Config:
        from_attributes = True


class ContactNoteCreate(BaseModel):
    note_text: str = Field(..., min_length=1, max_length=2000)


class ContactNoteResponse(BaseModel):
    id: int
    contact_request_id: int
    note_text: str
    admin_email: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContactStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r'^(new|contacted|qualified|converted|not_interested)$')


# Lead Assignment Schemas

class LeadAssignmentCreate(BaseModel):
    salesman_id: int = Field(..., gt=0)


class LeadAssignmentResponse(BaseModel):
    id: int
    contact_request_id: int
    salesman_id: int
    salesman_email: str
    salesman_name: Optional[str]
    assigned_by_id: int
    assigned_at: datetime
    
    class Config:
        from_attributes = True
