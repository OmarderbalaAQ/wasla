"""
Reset admin password
Use this if you forgot the admin password or need to reset it
"""

from database import SessionLocal
from utils.security import hash_password
import models
import sys

def reset_password(email, new_password):
    """Reset user password"""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(models.User).filter(
            models.User.email == email
        ).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            print()
            print("Available users:")
            all_users = db.query(models.User).all()
            if all_users:
                for u in all_users:
                    print(f"  - {u.email} ({u.role})")
            else:
                print("  No users in database!")
            return False
        
        # Reset password
        print(f"Resetting password for: {email}")
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        print("=" * 60)
        print("✓ PASSWORD RESET SUCCESSFUL!")
        print("=" * 60)
        print()
        print("New credentials:")
        print(f"  Email: {email}")
        print(f"  Password: {new_password}")
        print(f"  Role: {user.role}")
        print()
        print("You can now login with the new password.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function"""
    print("=" * 60)
    print("PASSWORD RESET SCRIPT")
    print("=" * 60)
    print()
    
    # Get email and password from command line or prompt
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        new_password = sys.argv[2]
    else:
        print("Usage: python reset_admin_password.py <email> <new_password>")
        print()
        print("Example:")
        print("  python reset_admin_password.py admin@admin.com newpassword123")
        print()
        
        # Interactive mode
        try:
            email = input("Enter email: ").strip()
            new_password = input("Enter new password: ").strip()
            
            if not email or not new_password:
                print("❌ Email and password are required!")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            sys.exit(0)
    
    print(f"Resetting password for: {email}")
    print()
    
    success = reset_password(email, new_password)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
