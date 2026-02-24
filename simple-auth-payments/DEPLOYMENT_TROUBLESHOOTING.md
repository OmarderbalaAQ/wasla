# Deployment Troubleshooting Guide

## Issue: "Network error. Please make sure the API server is running"

This error occurs when the frontend cannot connect to the backend API. Here are the solutions:

---

## ✅ FIXES APPLIED

### 1. Fixed Hardcoded API URLs
Changed all frontend files from hardcoded `http://localhost:8000` to dynamic `window.location.origin`:
- ✓ `static/login.html`
- ✓ `static/register.html`
- ✓ `static/admin.html`
- ✓ `static/client_home.html`
- ✓ `static/dashboard.html` (already correct)

This allows your app to work on any domain/port automatically.

---

## 🔍 TROUBLESHOOTING STEPS

### Step 1: Verify Server is Running

```bash
# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Test API Endpoint Directly

Open a new terminal and test:
```bash
curl http://localhost:8000/
```

Or visit in browser: `http://localhost:8000/`

You should see your index.html page.

### Step 3: Test Login Endpoint

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

### Step 4: Check Browser Console

1. Open your browser's Developer Tools (F12)
2. Go to the Console tab
3. Try to login
4. Look for error messages

Common errors:
- **CORS error**: Check CORS configuration in `main.py`
- **404 Not Found**: API endpoint doesn't exist
- **Connection refused**: Server not running
- **Mixed content**: Using HTTP on HTTPS page

---

## 🌐 DEPLOYMENT SCENARIOS

### Local Development (localhost)
```bash
# Start server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Access at
http://localhost:8000
```

### Network Access (LAN)
```bash
# Start server accessible from network
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access at
http://YOUR_IP:8000
# Example: http://192.168.1.100:8000
```

### Production Deployment

#### Option 1: Using Gunicorn (Recommended)
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Option 2: Using Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🔒 CORS Configuration

If deploying to a different domain, update CORS in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://yourdomain.com",  # Add your domain
        "https://www.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 🔐 Environment Variables

Ensure your `.env` file has valid values:

```env
DATABASE_URL=sqlite:///./dev.db
JWT_SECRET_KEY=your-actual-secret-key-here  # Change this!
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
STRIPE_SECRET_KEY=sk_test_your_actual_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret
```

Generate a secure JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🧪 QUICK TEST SCRIPT

Run this to test your setup:

```bash
python test_env_config.py
```

---

## 📱 TESTING ON MOBILE/OTHER DEVICES

1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. Start server with `0.0.0.0`:
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Access from mobile:
   ```
   http://YOUR_IP:8000
   ```

4. Make sure firewall allows port 8000

---

## 🚀 RENDER.COM DEPLOYMENT

If deploying to Render:

1. Ensure `render.yaml` is configured
2. Set environment variables in Render dashboard
3. Use the Render URL in CORS configuration
4. Frontend will automatically use `window.location.origin`

---

## ❓ COMMON ISSUES

### Issue: "Failed to fetch"
**Solution**: Server not running or wrong URL
- Check server is running
- Check browser console for actual URL being called
- Verify no typos in endpoint paths

### Issue: CORS Error
**Solution**: Add your domain to CORS allowed origins in `main.py`

### Issue: 404 on static files
**Solution**: Verify static files are mounted correctly in `main.py`
```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Issue: JWT errors
**Solution**: Generate a proper secret key in `.env`

---

## 📞 NEED MORE HELP?

1. Check server logs for errors
2. Check browser console for frontend errors
3. Test API endpoints with curl or Postman
4. Verify environment variables are loaded
5. Check firewall/network settings
