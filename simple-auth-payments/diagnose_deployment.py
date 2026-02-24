"""
Diagnostic script to check deployment database status
Run this on your deployed server to diagnose login issues
"""

from database import SessionLocal
import models

def diagnose():
    print("=" * 60)
    print("DEPLOYMENT DATABASE DIAGNOSTIC")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Check users
        print("📊 USER STATISTICS:")
        print("-" * 60)
        user_count = db.query(models.User).count()
        print(f"Total users: {user_count}")
        
        if user_count == 0:
            print("❌ NO USERS FOUND!")
            print("   The database is empty. Auto-seed should have created admin.")
            print("   Check startup logs for errors.")
        else:
            print(f"✓ Found {user_count} user(s)")
            print()
            print("USER LIST:")
            users = db.query(models.User).all()
            for i, user in enumerate(users, 1):
                print(f"  {i}. Email: {user.email}")
                print(f"     Role: {user.role}")
                print(f"     Active: {user.is_active}")
                print(f"     Has password: {'Yes' if user.hashed_password else 'No'}")
                print()
        
        # Check for default admin
        print("-" * 60)
        print("🔍 CHECKING FOR DEFAULT ADMIN:")
        admin = db.query(models.User).filter(
            models.User.email == "admin@admin.com"
        ).first()
        
        if admin:
            print("✓ Default admin exists: admin@admin.com")
            print(f"  Role: {admin.role}")
            print(f"  Active: {admin.is_active}")
            print(f"  Has password: {'Yes' if admin.hashed_password else 'No'}")
        else:
            print("❌ Default admin NOT FOUND!")
            print("   Expected: admin@admin.com")
            print("   Action: Run create_production_admin.py")
        
        # Check bundles
        print()
        print("-" * 60)
        print("📦 BUNDLE STATISTICS:")
        bundle_count = db.query(models.Bundle).count()
        print(f"Total bundles: {bundle_count}")
        
        if bundle_count == 0:
            print("⚠ No bundles found (this is OK for login testing)")
        else:
            bundles = db.query(models.Bundle).all()
            for bundle in bundles:
                print(f"  - {bundle.name}: ${bundle.price_cents/100:.2f}")
        
        # Check contacts
        print()
        print("-" * 60)
        print("📧 CONTACT STATISTICS:")
        contact_count = db.query(models.Contact).count()
        print(f"Total contacts: {contact_count}")
        
        print()
        print("=" * 60)
        print("DIAGNOSIS COMPLETE")
        print("=" * 60)
        
        # Recommendations
        print()
        print("📋 RECOMMENDATIONS:")
        if user_count == 0:
            print("❌ CRITICAL: No users in database")
            print("   1. Check if startup event ran (check logs)")
            print("   2. Run: python create_production_admin.py")
            print("   3. Or restart the application")
        elif not admin:
            print("⚠ WARNING: Default admin not found")
            print("   1. Create admin manually")
            print("   2. Or use existing user credentials")
        else:
            print("✓ Database looks good!")
            print("   Try logging in with: admin@admin.com / admin123")
            print("   If login fails, check:")
            print("   - JWT_SECRET_KEY environment variable")
            print("   - Password hashing algorithm")
            print("   - Network connectivity")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Possible causes:")
        print("- Database not accessible")
        print("- DATABASE_URL not set correctly")
        print("- Database service not running")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
