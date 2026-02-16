# Admin Dashboard Setup Guide

## ✅ Server is Running!

Your FastAPI server is now running at: **http://localhost:8000**

## Quick Setup Steps

### Step 1: Create Your First Account

1. Go to: **http://localhost:8000/static/register.html**
2. Register with your email and password
3. This will be your admin account

### Step 2: Make Yourself Admin

Run this command in a NEW terminal (keep the server running):

```bash
cd simple-auth-payments
python create_admin.py
```

Choose option 2 to promote your existing user to admin.

### Step 3: Access Admin Dashboard

1. Go to: **http://localhost:8000/static/login.html**
2. Login with your credentials
3. Click "Admin Dashboard" link at the bottom
4. Or go directly to: **http://localhost:8000/static/admin.html**

## Admin Dashboard Features

### 📊 Statistics Dashboard
- Total users count
- Active users count
- Total payments
- Successful payments
- Total revenue in USD

### 👥 User Management
- View all users
- Promote users to admin / demote to regular user
- Activate / Deactivate user accounts
- Delete users
- See user roles and status

### 💳 Payment History
- View all payments
- See payment status (pending/succeeded)
- Track which user bought which bundle
- View Stripe payment intent IDs
- See payment dates and amounts

### 📦 Bundle Management
- View all bundles (active and inactive)
- Create new bundles
- Activate / Deactivate bundles
- See bundle prices and currency

## Testing the System

### Test as Regular User:
1. Register at `/static/register.html`
2. Login at `/static/login.html`
3. View bundles at `/static/dashboard.html`
4. Try purchasing a bundle

### Test as Admin:
1. Login with admin account
2. Go to `/static/admin.html`
3. View statistics
4. Manage users, payments, and bundles

## API Endpoints

### Admin Endpoints (Require Admin Role):
- `GET /admin/stats` - Get system statistics
- `GET /admin/users` - List all users
- `PUT /admin/users/{id}/role` - Change user role
- `PUT /admin/users/{id}/status` - Activate/deactivate user
- `DELETE /admin/users/{id}` - Delete user
- `GET /admin/payments` - List all payments
- `GET /admin/bundles` - List all bundles
- `POST /admin/bundles` - Create new bundle
- `PUT /admin/bundles/{id}` - Update bundle

## Troubleshooting

### "Network error" when registering:
- Make sure the server is running (check terminal)
- Server should be at http://localhost:8000
- Check browser console (F12) for errors

### Can't access admin dashboard:
- Make sure you ran `create_admin.py` to promote your user
- Check that you're logged in with an admin account
- Regular users will be redirected to normal dashboard

### CORS errors:
- The server is configured to allow all origins
- Make sure you're accessing via http://localhost:8000
- Don't use file:// protocol

## Default Bundles

Two bundles are pre-seeded:
- **Basic Bundle**: $10.00 USD
- **Pro Bundle**: $50.00 USD

You can create more bundles from the admin dashboard!
