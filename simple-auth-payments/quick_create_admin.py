"""
Quick script to create admin - no prompts, just run it!
"""
from database import SessionLocal, Base, engine
import models
from utils.security import hash_password

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # Check if admin exists
    existing = db.query(models.User).filter(models.User.email == "admin@admin.com").first()
    
    if existing:
        print(f"✓ Admin user already exists: admin@admin.com")
        print(f"  Role: {existing.role}")
        if existing.role != "admin":
            existing.role = "admin"
            db.commit()
            print("  ✓ Promoted to admin!")
    else:
        # Create admin
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
        print("✓ Admin user created successfully!")
        print("\n" + "="*50)
        print("  Email: admin@admin.com")
        print("  Password: admin123")
        print("="*50)
        print("\nLogin at: http://localhost:8000/static/login.html")
        print("Then go to: http://localhost:8000/static/admin.html")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
