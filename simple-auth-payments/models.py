from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")
    allow_access_without_subscription = Column(Boolean, default=False)  # Admin override

    payments = relationship("Payment", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    dashboard = relationship("Dashboard", back_populates="user", uselist=False)


class Bundle(Base):
    __tablename__ = "bundles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String, default="usd")
    is_active = Column(Boolean, default=True)
    tier_level = Column(Integer, default=1)  # 1=basic, 2=pro, 3=premium
    logo_type = Column(String, default="silver")  # silver, gold, diamond
    description = Column(String, nullable=True)  # Custom or predefined description
    main_description = Column(String, nullable=True)  # Custom main description

    payments = relationship("Payment", back_populates="bundle")
    subscriptions = relationship("Subscription", back_populates="bundle")


class DiscountRule(Base):
    __tablename__ = "discount_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "6-Month Discount"
    min_months = Column(Integer, nullable=False)  # Minimum months (e.g., 6)
    max_months = Column(Integer, nullable=True)   # Maximum months (e.g., 12, or NULL for unlimited)
    discount_percentage = Column(Integer, nullable=False)  # Discount percentage (e.g., 10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bundle_id = Column(Integer, ForeignKey("bundles.id"), nullable=False)
    stripe_pi_id = Column(String, unique=True, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="usd")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription_end_date = Column(DateTime, nullable=True)  # 30 days from payment
    looker_studio_url = Column(String, nullable=True)  # Custom Looker Studio link
    months_purchased = Column(Integer, default=1)  # Number of months purchased
    discount_percentage = Column(Integer, default=0)  # Discount applied

    user = relationship("User", back_populates="payments")
    bundle = relationship("Bundle", back_populates="payments")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bundle_id = Column(Integer, ForeignKey("bundles.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")
    bundle = relationship("Bundle", back_populates="subscriptions")


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    looker_studio_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="dashboard")


class ContactRequest(Base):
    __tablename__ = "contact_requests"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    country_code = Column(String(10), nullable=False)
    country = Column(String(100), nullable=False)
    business_name = Column(String(255), nullable=False)
    num_locations = Column(String(20), nullable=False)
    referral_source = Column(String(100), nullable=False)
    marketing_consent = Column(Boolean, default=False)
    language_preference = Column(String(10), default="en")
    status = Column(String(50), default="new")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notes = relationship("ContactNote", back_populates="contact_request", cascade="all, delete-orphan")
    assignment = relationship("LeadAssignment", back_populates="contact_request", uselist=False)


class ContactNote(Base):
    __tablename__ = "contact_notes"

    id = Column(Integer, primary_key=True, index=True)
    contact_request_id = Column(Integer, ForeignKey("contact_requests.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note_text = Column(String(2000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    contact_request = relationship("ContactRequest", back_populates="notes")
    admin = relationship("User")


class LeadAssignment(Base):
    __tablename__ = "lead_assignments"

    id = Column(Integer, primary_key=True, index=True)
    contact_request_id = Column(Integer, ForeignKey("contact_requests.id"), nullable=False, unique=True)
    salesman_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contact_request = relationship("ContactRequest", back_populates="assignment")
    salesman = relationship("User", foreign_keys=[salesman_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])

