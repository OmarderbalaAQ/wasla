"""
Complete system setup with all features
"""
from database import SessionLocal, Base, engine
import models
from utils.security import hash_password
from datetime import datetime, timedelta

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    print("\n" + "="*70)
    print("  COMPLETE SYSTEM SETUP")
    print("="*70)
    
    # 1. Create admin user
    admin = db.query(models.User).filter(models.User.email == "admin@admin.com").first()
    if not admin:
        admin = models.User(
            email="admin@admin.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            is_active=True,
            is_verified=True,
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("\n✓ Admin user created")
    else:
        print("\n✓ Admin user exists")
    
    # 2. Create bundles with tier levels
    bundles_data = [
        {"name": "Basic Plan", "price_cents": 1000, "tier_level": 1},
        {"name": "Pro Plan", "price_cents": 3000, "tier_level": 2},
        {"name": "Premium Plan", "price_cents": 5000, "tier_level": 3}
    ]
    
    for bundle_data in bundles_data:
        existing = db.query(models.Bundle).filter(models.Bundle.name == bundle_data["name"]).first()
        if not existing:
            bundle = models.Bundle(**bundle_data, currency="usd", is_active=True)
            db.add(bundle)
    
    db.commit()
    print("✓ Bundles created (Basic, Pro, Premium)")
    
    # 3. Create test client with subscription
    client = db.query(models.User).filter(models.User.email == "client@test.com").first()
    if not client:
        client = models.User(
            email="client@test.com",
            hashed_password=hash_password("client123"),
            full_name="Test Client",
            is_active=True,
            is_verified=True,
            role="user"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        print("✓ Test client created")
    else:
        print("✓ Test client exists")
    
    # 4. Create subscription for test client
    basic_bundle = db.query(models.Bundle).filter(models.Bundle.name == "Basic Plan").first()
    existing_sub = db.query(models.Subscription).filter(
        models.Subscription.user_id == client.id
    ).first()
    
    if not existing_sub and basic_bundle:
        subscription = models.Subscription(
            user_id=client.id,
            bundle_id=basic_bundle.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        db.add(subscription)
        db.commit()
        print("✓ Subscription created for test client")
    else:
        print("✓ Subscription exists for test client")
    
    # 5. Create dashboard for test client
    dashboard = db.query(models.Dashboard).filter(models.Dashboard.user_id == client.id).first()
    if not dashboard:
        dashboard = models.Dashboard(
            user_id=client.id,
            looker_studio_url="https://lookerstudio.google.com/u/0/reporting/e4a41bad-55c4-4ab7-8b90-af796224d452"
        )
        db.add(dashboard)
        db.commit()
        print("✓ Dashboard created for test client")
    else:
        print("✓ Dashboard exists for test client")
    
    # 6. Create test user without subscription
    user_no_sub = db.query(models.User).filter(models.User.email == "user@test.com").first()
    if not user_no_sub:
        user_no_sub = models.User(
            email="user@test.com",
            hashed_password=hash_password("user123"),
            full_name="Test User No Sub",
            is_active=True,
            is_verified=True,
            role="user"
        )
        db.add(user_no_sub)
        db.commit()
        print("✓ Test user (no subscription) created")
    else:
        print("✓ Test user (no subscription) exists")
    
    # 7. Create test user with admin override
    user_override = db.query(models.User).filter(models.User.email == "override@test.com").first()
    if not user_override:
        user_override = models.User(
            email="override@test.com",
            hashed_password=hash_password("override123"),
            full_name="Test User Override",
            is_active=True,
            is_verified=True,
            role="user",
            allow_access_without_subscription=True
        )
        db.add(user_override)
        db.commit()
        db.refresh(user_override)
        
        # Create dashboard for override user
        dashboard_override = models.Dashboard(
            user_id=user_override.id,
            looker_studio_url="https://lookerstudio.google.com/u/0/reporting/override-dashboard"
        )
        db.add(dashboard_override)
        db.commit()
        print("✓ Test user (admin override) created with dashboard")
    else:
        print("✓ Test user (admin override) exists")
    
    print("\n" + "="*70)
    print("  SETUP COMPLETE!")
    print("="*70)
    
    print("\n📋 TEST ACCOUNTS:")
    print("-" * 70)
    print("\n1. ADMIN ACCOUNT:")
    print("   Email: admin@admin.com")
    print("   Password: admin123")
    print("   → Goes to: Admin Dashboard")
    
    print("\n2. CLIENT WITH SUBSCRIPTION:")
    print("   Email: client@test.com")
    print("   Password: client123")
    print("   → Goes to: Client Home (can access dashboard)")
    
    print("\n3. USER WITHOUT SUBSCRIPTION:")
    print("   Email: user@test.com")
    print("   Password: user123")
    print("   → Goes to: Bundles Page (must purchase)")
    
    print("\n4. USER WITH ADMIN OVERRIDE:")
    print("   Email: override@test.com")
    print("   Password: override123")
    print("   → Goes to: Client Home (access granted by admin)")
    
    print("\n" + "="*70)
    print("  FEATURES IMPLEMENTED:")
    print("="*70)
    print("✓ Subscriptions table with tier management")
    print("✓ Dashboards table with Looker Studio links")
    print("✓ Multi-month discounts (6mo=10%, 12mo=20%)")
    print("✓ Tier-based subscription logic")
    print("✓ Admin override for access without subscription")
    print("✓ Client home page with dashboard access")
    print("✓ Smart login redirects")
    
    print("\n🌐 LOGIN AT: http://localhost:8000/static/login.html")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
