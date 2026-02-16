# Testing Guide

## Server is Running! 🎉

Your FastAPI server is now running at: **http://localhost:8000**

## Test the Application

### Option 1: Use the Web Interface

Open these URLs in your browser:

1. **Login Page**: http://localhost:8000/static/login.html
2. **Register Page**: http://localhost:8000/static/register.html
3. **Dashboard**: http://localhost:8000/static/dashboard.html (after login)

### Option 2: Use API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing Flow

1. **Register a new user**:
   - Go to http://localhost:8000/static/register.html
   - Enter your details (email, password, full name)
   - Click "Create Account"

2. **Login**:
   - Go to http://localhost:8000/static/login.html
   - Enter your email and password
   - Click "Continue"

3. **View Dashboard**:
   - After login, you'll be redirected to the dashboard
   - You'll see two bundles: Basic Bundle ($10) and Pro Bundle ($50)
   - Click "Purchase" to test payment intent creation

### Test with cURL (Command Line)

```bash
# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\",\"full_name\":\"Test User\"}"

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Get bundles
curl "http://localhost:8000/payments/bundles"
```

## Notes

- The database file `dev.db` is created automatically
- Two bundles are pre-seeded: Basic ($10) and Pro ($50)
- JWT tokens are stored in browser localStorage
- For real Stripe payments, update `.env` with your Stripe keys

## Troubleshooting

If you see errors:
1. Make sure the server is running (check terminal)
2. Check browser console for JavaScript errors (F12)
3. Verify `.env` file has correct settings
4. Make sure port 8000 is not blocked by firewall
