# Troubleshooting Guide

## Issue: ModuleNotFoundError: No module named 'slowapi'

**Solution:**
```bash
pip install slowapi
```

## Issue: Server won't start

**Check:**
1. All dependencies installed: `pip install -r requirements.txt`
2. Environment file exists: `.env` with required variables
3. Python imports work: `python -c "import main"`

## Issue: Secure cookies not working in development

**Fixed:** Changed cookie settings for development:
- `secure=False` (for HTTP)
- `samesite="lax"` (for better compatibility)

## Issue: Missing Stripe service

**Fixed:** `services/stripe_service.py` exists with required functions

## Quick Fix

Run: `fix_dependencies.bat`

This will:
- Install slowapi
- Verify all dependencies
- Test imports
- Test server startup

## Manual Steps

1. **Install slowapi:**
   ```bash
   pip install slowapi
   ```

2. **Install all requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test imports:**
   ```bash
   python -c "import main; print('Success')"
   ```

4. **Start server:**
   ```bash
   uvicorn main:app --reload
   ```

## Environment Variables Required

In `.env` file:
```
DATABASE_URL=sqlite:///./dev.db
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## Testing

After fixing:
- Test security headers: `python test_security_headers.py`
- Test rate limiting: `python test_rate_limiting.py`
- Test secure auth: Visit `http://localhost:8000/static/test_secure_auth.html`