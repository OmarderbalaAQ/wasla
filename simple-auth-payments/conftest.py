"""
Shared pytest configuration for multi-role access control tests.

This module provides shared fixtures and configuration to ensure proper
database isolation when running multiple test files together.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app
from models import User, ContactRequest, LeadAssignment
from utils.security import hash_password
import time


# Use in-memory SQLite database for all tests
# StaticPool ensures the same connection is reused across all tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine with StaticPool to share in-memory database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Critical: keeps the in-memory database alive
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency once for all tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create database tables once for the entire test session.
    This runs before any tests and tears down after all tests complete.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize rate limiting storage
    if not hasattr(app.state, 'rate_limit_storage'):
        app.state.rate_limit_storage = {}
    
    yield
    
    # Drop all tables after all tests complete
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def cleanup_database():
    """
    Clean up database between each test to ensure isolation.
    This runs before and after each individual test.
    """
    # Clear rate limiting storage before each test
    if hasattr(app.state, 'rate_limit_storage'):
        app.state.rate_limit_storage.clear()
    
    yield
    
    # Clean up all data after each test
    db = TestingSessionLocal()
    try:
        # Import ContactNote model
        from models import ContactNote
        
        # Delete in correct order to respect foreign key constraints
        db.query(ContactNote).delete()
        db.query(LeadAssignment).delete()
        db.query(ContactRequest).delete()
        db.query(User).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error cleaning up database: {e}")
    finally:
        db.close()


@pytest.fixture
def db_session():
    """Provide a database session for tests that need direct DB access"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Provide a test client for making HTTP requests"""
    return TestClient(app, raise_server_exceptions=False)


# Helper functions available to all tests
def create_test_user(email: str, password: str, role: str = "user", full_name: str = None):
    """Helper to create a test user"""
    db = TestingSessionLocal()
    try:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name or email.split("@")[0],
            is_active=True,
            is_verified=True,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def create_test_contact(db_session: Session = None):
    """Helper to create a test contact request"""
    should_close = False
    if db_session is None:
        db_session = TestingSessionLocal()
        should_close = True
    
    try:
        contact = ContactRequest(
            first_name="Test",
            last_name="Contact",
            email="test@example.com",
            phone="1234567890",
            country_code="+1",
            country="US",
            business_name="Test Business",
            num_locations=1,
            referral_source="website",
            marketing_consent=True,
            language_preference="en",
            status="new"
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)
        return contact
    finally:
        if should_close:
            db_session.close()


def create_lead_assignment(db_session: Session, contact_id: int, salesman_id: int, assigned_by_id: int):
    """Helper to create a lead assignment"""
    assignment = LeadAssignment(
        contact_request_id=contact_id,
        salesman_id=salesman_id,
        assigned_by_id=assigned_by_id
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)
    return assignment


def login_user(client: TestClient, email: str, password: str):
    """Helper to login and get auth cookie"""
    # Add small delay to avoid rate limiting
    time.sleep(0.5)
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    if response.status_code == 429:
        # If rate limited, wait and retry once
        time.sleep(2)
        response = client.post(
            "/auth/login",
            data={"username": email, "password": password}
        )
    assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.json()}"
    return response.cookies
