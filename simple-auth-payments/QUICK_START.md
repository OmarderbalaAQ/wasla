# 🚀 Quick Start Guide

## ✅ Your Server is Running!

The FastAPI server is running at: **http://localhost:8000**

---

## 📋 Step-by-Step Setup

### 1️⃣ Register Your Account

Open your browser and go to:
```
http://localhost:8000/static/register.html
```

Fill in:
- Full Name
- Email
- Password (minimum 6 characters)

Click **"Create Account"**

---

### 2️⃣ Make Yourself Admin

**Open a NEW terminal** (keep the server running in the first one) and run:

```bash
cd D:\back\simple-auth-payments
python create_admin.py
```

When prompted:
1. Choose option **2** (Promote existing user to admin)
2. Select your user number
3. Confirm

You should see: `✓ User [your-email] promoted to admin`

---

### 3️⃣ Login and Access Admin Dashboard

Go to:
```
http://localhost:8000/static/login.html
```

Login with your credentials, then:

**Option A:** Click "Admin Dashboard" link at the bottom of the login page

**Option B:** Go directly to:
```
http://localhost:8000/static/admin.html
```

---

## 🎯 What You Can Do

### As Admin:

**📊 View Statistics:**
- Total users
- Active users  
- Total payments
- Revenue tracking

**👥 Manage Users:**
- View all registered users
- Promote users to admin or demote to regular user
- Activate/Deactivate accounts
- Delete users

**💳 View Payments:**
- See all payment transactions
- Track payment status
- View Stripe payment IDs
- See which user bought which bundle

**📦 Manage Bundles:**
- View all bundles
- Create new bundles
- Activate/Deactivate bundles
- Set prices

### As Regular User:

**🛍️ Browse & Purchase:**
- View available bundles
- Purchase bundles (creates Stripe payment intent)
- See your account info

---

## 🔗 Important URLs

| Page | URL |
|------|-----|
| **API Root** | http://localhost:8000 |
| **Register** | http://localhost:8000/static/register.html |
| **Login** | http://localhost:8000/static/login.html |
| **User Dashboard** | http://localhost:8000/static/dashboard.html |
| **Admin Dashboard** | http://localhost:8000/static/admin.html |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |

---

## 🐛 Troubleshooting

### "Network error" when registering:

**Solution:** The server is running correctly. This might be a browser cache issue.

1. Open browser DevTools (Press F12)
2. Go to Console tab
3. Try registering again
4. Check for any error messages

If you see CORS errors:
- Make sure you're using `http://localhost:8000` (not `file://`)
- Clear browser cache and try again

### Can't access admin dashboard:

1. Make sure you ran `python create_admin.py`
2. Verify you're logged in with an admin account
3. Check browser console for errors

### Server not responding:

Check if the server is still running in your terminal. You should see:
```
INFO:     Application startup complete.
```

If not, restart it:
```bash
cd D:\back\simple-auth-payments
uvicorn main:app --reload
```

---

## 📝 Pre-Seeded Data

Your database comes with 2 bundles:
- **Basic Bundle** - $10.00 USD
- **Pro Bundle** - $50.00 USD

You can add more from the admin dashboard!

---

## 🔐 Security Notes

- JWT tokens are stored in browser localStorage
- Passwords are hashed with bcrypt
- Admin routes require admin role
- CORS is enabled for development (adjust for production)

---

## 🎉 You're All Set!

Start by:
1. ✅ Registering your account
2. ✅ Making yourself admin
3. ✅ Exploring the admin dashboard
4. ✅ Creating test users and bundles

Enjoy your new authentication & payment system! 🚀
