"""
Fix passwords on production Railway deployment
Run this script to reset production passwords after database restore
"""
import os
import sys

# This script should be run on Railway or with Railway CLI
# It will reset all user passwords to a known value

print("=" * 70)
print("FIX PRODUCTION PASSWORDS ON RAILWAY")
print("=" * 70)

print("\n⚠️  IMPORTANT: This script must be run ON the Railway server")
print("   or using Railway CLI with database access.")
print("\nOptions to fix production passwords:")
print()
print("OPTION 1: Run via Railway CLI (Recommended)")
print("-" * 70)
print("1. Install Railway CLI: npm install -g @railway/cli")
print("2. Login: railway login")
print("3. Link project: railway link")
print("4. Run this script: railway run python fix_production_passwords.py")
print()
print("OPTION 2: Run via Railway Shell")
print("-" * 70)
print("1. Go to Railway dashboard")
print("2. Open your project")
print("3. Click on your service")
print("4. Go to 'Settings' tab")
print("5. Scroll to 'Service Settings'")
print("6. Click 'Open Shell' or use the terminal")
print("7. Run: python fix_production_passwords.py")
print()
print("OPTION 3: Deploy this script")
print("-" * 70)
print("1. Create a one-time endpoint in main.py:")
print("   @app.post('/admin/reset-all-passwords-emergency')")
print("2. Call it from your browser or curl")
print("3. Remove the endpoint after use")
print()

# Check if we're in production environment
if os.getenv('RAILWAY_ENVIRONMENT'):
    print("\n✓ Detected Railway environment")
    print("  Proceeding with password reset...")
    
    try:
        from database import SessionLocal
        import models
        from utils.security import hash_password
        
        db = SessionLocal()
        
        # New password for all users
        new_password = "TempRailway2026!"
        new_hash = hash_password(new_password)
        
        users = db.query(models.User).all()
        
        print(f"\n✓ Found {len(users)} users")
        print(f"  Setting all passwords to: {new_password}")
        print()
        
        for user in users:
            user.hashed_password = new_hash
            print(f"  ✓ Reset: {user.email} ({user.role})")
        
        db.commit()
        db.close()
        
        print("\n" + "=" * 70)
        print("✓ ALL PASSWORDS RESET SUCCESSFULLY")
        print("=" * 70)
        print(f"\nNew password for ALL users: {new_password}")
        print("\n⚠️  CHANGE THESE PASSWORDS IMMEDIATELY AFTER LOGGING IN!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print("\n⚠️  NOT running in Railway environment")
    print("   This script should be run on the production server.")
    print("\n   To test locally, run: python fix_restored_database_passwords.py")
    sys.exit(1)
