"""
Fix password hashes after database restore
This script resets passwords for all users to a known password
so you can log in and then change them.
"""
from database import SessionLocal
import models
from utils.security import hash_password
import sys

def fix_passwords():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("FIX RESTORED DATABASE PASSWORDS")
        print("=" * 70)
        
        # Default password for all users
        default_password = "TempPassword123!"
        
        print(f"\n⚠ WARNING: This will reset ALL user passwords!")
        print(f"  New password for all users: {default_password}")
        print(f"\n  You should change passwords after logging in.")
        
        response = input("\nContinue? (yes/no): ").strip().lower()
        
        if response != "yes":
            print("Cancelled.")
            return False
        
        users = db.query(models.User).all()
        
        if not users:
            print("\n✗ No users found in database!")
            return False
        
        print(f"\n✓ Found {len(users)} users")
        print("\nResetting passwords...")
        print("-" * 70)
        
        # Generate new hash with current settings (12 rounds)
        new_hash = hash_password(default_password)
        print(f"\nNew hash generated: {new_hash[:50]}...")
        rounds = int(new_hash.split('$')[2])
        print(f"Using {rounds} rounds (secure)")
        
        updated_count = 0
        
        for user in users:
            try:
                old_hash = user.hashed_password[:50]
                user.hashed_password = new_hash
                print(f"\n✓ {user.email}")
                print(f"  Role: {user.role}")
                print(f"  Old hash: {old_hash}...")
                print(f"  New hash: {new_hash[:50]}...")
                updated_count += 1
            except Exception as e:
                print(f"\n✗ Failed to update {user.email}: {e}")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 70)
        print(f"✓ PASSWORDS RESET FOR {updated_count} USERS")
        print("=" * 70)
        
        print("\n📋 LOGIN CREDENTIALS:")
        print("-" * 70)
        for user in users:
            print(f"  Email: {user.email}")
            print(f"  Password: {default_password}")
            print(f"  Role: {user.role}")
            print()
        
        print("=" * 70)
        print("⚠ IMPORTANT: Change these passwords after logging in!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = fix_passwords()
    sys.exit(0 if success else 1)
