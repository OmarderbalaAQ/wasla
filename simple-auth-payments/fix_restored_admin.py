"""
Fix Admin Password After Database Restore
Resets admin password with correct bcrypt hashing after backup restore
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.security import hash_password
import models
from database import SQLALCHEMY_DATABASE_URL

def fix_admin_password():
    """Reset admin password after database restore"""
    
    print("\n" + "="*60)
    print("FIX ADMIN PASSWORD AFTER RESTORE")
    print("="*60)
    
    # Create engine and session
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find admin user
        admin = db.query(models.User).filter(models.User.email == "admin@wasla.com").first()
        
        if not admin:
            print("\n❌ Admin user not found!")
            print("   Email: admin@wasla.com")
            print("\n💡 Create admin first:")
            print("   python create_production_admin.py")
            return False
        
        print(f"\n✓ Found admin user: {admin.email}")
        print(f"  Role: {admin.role}")
        print(f"  Active: {admin.is_active}")
        
        # Reset password with correct bcrypt hashing
        new_password = "Admin@123"
        admin.hashed_password = hash_password(new_password)
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ ADMIN PASSWORD RESET SUCCESSFUL")
        print("="*60)
        print(f"\nEmail: admin@wasla.com")
        print(f"Password: {new_password}")
        print("\n⚠️  IMPORTANT: Change this password after first login!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = fix_admin_password()
    exit(0 if success else 1)
