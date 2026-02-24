# Deployment Database Setup Guide

## Problem: "Incorrect email or password" on Fresh Deployment

When you deploy to a new environment (Render, Heroku, etc.), the database starts empty with no users. This causes login to fail.

---

## ✅ Solution Implemented: Auto-Seed Default Admin

Your app now automatically creates a default admin user on first startup if the database is empty.

### Default Credentials:
```
Email: admin@admin.com
Password: admin123
Role: admin
```

⚠️ **IMPORTANT:** Change this password immediately after first login in production!

---

## How It Works

### Startup Sequence:

```python
@app.on_event("startup")
def seed_bundles():
    # 1. Check if database is empty
    user_count = db.query(models.User).count()
    
    # 2. If no users exist, create default admin
    if user_count == 0:
        default_admin = models.User(
            email="admin@admin.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True
        )
        db.add(default_admin)
        db.commit()
        print("✓ Created default admin user")
    
    # 3. Also seed bundles if needed
    # ...
```

### What Gets Created:
1. ✅ Default admin user (admin@admin.com)
2. ✅ Basic Bundle ($10.00)
3. ✅ Pro Bundle ($50.00)

---

## Deployment Checklist

### Before Deploying:

1. ✅ **Code is updated** - main.py has auto-seed logic
2. ✅ **Environment variables set** - See below
3. ✅ **Database configured** - PostgreSQL for production
4. ✅ **CORS updated** - Add your domain to allowed origins

### After Deploying:

1. ✅ **Check logs** - Should see "Created default admin user"
2. ✅ **Test login** - Use admin@admin.com / admin123
3. ✅ **Change password** - Immediately!
4. ✅ **Create other users** - Through admin panel

---

## Environment Variables for Deployment

### Required Variables:

```bash
# Database (Render provides this automatically)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Secret (Generate a secure one!)
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe (Use production keys)
STRIPE_SECRET_KEY=sk_live_your_production_key
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret
```

### Generate Secure JWT Secret:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or online
# https://generate-secret.vercel.app/32
```

---

## Render.com Specific Setup

### 1. Set Environment Variables in Render Dashboard:

Go to your service → Environment → Add Environment Variables:

```
JWT_SECRET_KEY = [paste generated secret]
JWT_ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
STRIPE_SECRET_KEY = sk_live_...
STRIPE_WEBHOOK_SECRET = whsec_...
```

### 2. Database:

Render automatically provides `DATABASE_URL` when you add a PostgreSQL database.

### 3. Deploy:

- Push to GitHub
- Render auto-deploys
- Check logs for "Created default admin user"

### 4. First Login:

```
URL: https://your-app.onrender.com/static/login.html
Email: admin@admin.com
Password: admin123
```

---

## Diagnosing Login Issues

### Issue 1: "Incorrect email or password"

**Possible Causes:**
1. Database is empty (no users)
2. Wrong credentials
3. Database connection failed

**Diagnosis:**

Check deployment logs for:
```
✓ Created default admin user: admin@admin.com / admin123
```

If you see this, the user was created successfully.

### Issue 2: Database Connection Error

**Check:**
- DATABASE_URL is set correctly
- Database service is running
- Network connectivity

**Render Logs:**
```bash
# In Render dashboard, go to Logs tab
# Look for database connection errors
```

### Issue 3: Password Hash Mismatch

**Cause:** Different hashing algorithm or salt

**Solution:** 
- Delete user and let it recreate on restart
- Or manually reset password through admin panel

---

## Manual User Creation (If Needed)

If auto-seed doesn't work, create user manually:

### Option 1: Using Python Script

Create `create_production_admin.py`:

```python
from database import SessionLocal
from utils.security import hash_password
import models

db = SessionLocal()
try:
    # Check if admin exists
    admin = db.query(models.User).filter(
        models.User.email == "admin@admin.com"
    ).first()
    
    if not admin:
        admin = models.User(
            email="admin@admin.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("✓ Admin user created!")
    else:
        print("Admin user already exists")
finally:
    db.close()
```

Run on server:
```bash
python create_production_admin.py
```

### Option 2: Using Render Shell

In Render dashboard:
1. Go to Shell tab
2. Run:
```bash
python -c "
from database import SessionLocal
from utils.security import hash_password
import models

db = SessionLocal()
admin = models.User(
    email='admin@admin.com',
    hashed_password=hash_password('admin123'),
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
db.close()
print('Admin created!')
"
```

---

## Security Best Practices

### 1. Change Default Password Immediately

After first login:
1. Go to admin panel
2. Navigate to user management
3. Change admin@admin.com password
4. Use a strong password (12+ characters, mixed case, numbers, symbols)

### 2. Create Individual Admin Accounts

Don't share the default admin account:
1. Create separate admin accounts for each team member
2. Use real email addresses
3. Assign appropriate roles (admin, salesman, accountant, technical)

### 3. Disable Default Admin (Optional)

After creating other admins:
1. Create your personal admin account
2. Test it works
3. Disable or delete admin@admin.com

### 4. Use Environment-Specific Credentials

```
Development: admin@admin.com / admin123 (OK)
Staging: admin@staging.com / strong-password
Production: admin@company.com / very-strong-password
```

---

## Testing Deployment

### 1. Check Logs:

```
✓ Database OK: X users, Y bundles
✓ Created default admin user: admin@admin.com / admin123
✓ Seeded initial bundles
INFO: Uvicorn running on...
```

### 2. Test Login:

```bash
# Using curl
curl -X POST https://your-app.onrender.com/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@admin.com&password=admin123"

# Should return:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 3. Test in Browser:

1. Go to: `https://your-app.onrender.com/static/login.html`
2. Enter: admin@admin.com / admin123
3. Should redirect to admin panel

---

## Troubleshooting Commands

### Check if user exists:

```python
from database import SessionLocal
import models

db = SessionLocal()
users = db.query(models.User).all()
for user in users:
    print(f"Email: {user.email}, Role: {user.role}")
db.close()
```

### Reset admin password:

```python
from database import SessionLocal
from utils.security import hash_password
import models

db = SessionLocal()
admin = db.query(models.User).filter(
    models.User.email == "admin@admin.com"
).first()

if admin:
    admin.hashed_password = hash_password("new-password")
    db.commit()
    print("Password reset!")
else:
    print("Admin not found")
db.close()
```

### Count users:

```python
from database import SessionLocal
import models

db = SessionLocal()
count = db.query(models.User).count()
print(f"Total users: {count}")
db.close()
```

---

## Summary

✅ **Auto-seed implemented** - Default admin created on first startup
✅ **Default credentials** - admin@admin.com / admin123
✅ **Works on deployment** - No manual database setup needed
✅ **Secure** - Change password after first login

### Quick Start:
1. Deploy to Render
2. Check logs for "Created default admin user"
3. Login with admin@admin.com / admin123
4. Change password immediately
5. Create other users as needed

🎉 **Your deployment will now have a working admin account automatically!**
