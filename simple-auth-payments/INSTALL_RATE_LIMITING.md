# Quick Start: Rate Limiting Installation

## Step 1: Install Dependencies

```bash
pip install slowapi
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

---

## Step 2: Restart the Server

Stop the current server (Ctrl+C) and restart:

```bash
uvicorn main:app --reload
```

You should see the server start without errors.

---

## Step 3: Test Rate Limiting

### Option A: Run the Test Script

```bash
python test_rate_limiting.py
```

**Expected Output:**
```
🔒 Rate Limiting Test Suite
============================================================
✅ Server is running

Testing Login Rate Limiting (5 attempts per minute)
============================================================

Sending 7 login requests rapidly...
------------------------------------------------------------
[10:30:15.123] Request 1: ✅ ALLOWED (401 - wrong password)
[10:30:15.234] Request 2: ✅ ALLOWED (401 - wrong password)
[10:30:15.345] Request 3: ✅ ALLOWED (401 - wrong password)
[10:30:15.456] Request 4: ✅ ALLOWED (401 - wrong password)
[10:30:15.567] Request 5: ✅ ALLOWED (401 - wrong password)
[10:30:15.678] Request 6: ❌ RATE LIMITED (429)
[10:30:15.789] Request 7: ❌ RATE LIMITED (429)
------------------------------------------------------------

📊 Results:
  ✅ Allowed requests: 5
  ❌ Rate limited requests: 2

✅ PASS: Rate limiting working correctly!
   First 5 requests allowed, next 2 blocked.
```

### Option B: Manual Testing with Browser

1. Open the API docs: http://localhost:8000/docs
2. Go to POST /auth/login
3. Click "Try it out"
4. Enter any credentials
5. Click "Execute" 6 times rapidly
6. The 6th request should return 429 (Too Many Requests)

### Option C: Test with curl

```bash
# Run this command 6 times
curl -X POST http://localhost:8000/auth/login \
  -d "username=test@example.com&password=test" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

First 5 requests: Status 401 (Unauthorized)
6th request: Status 429 (Too Many Requests)

---

## Step 4: Verify Implementation

Check that these files were updated:

1. ✅ `requirements.txt` - slowapi added
2. ✅ `main.py` - limiter initialized
3. ✅ `routers/auth.py` - rate limits on login/register
4. ✅ `routers/payments.py` - rate limit on payment creation

---

## What's Protected?

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| POST /auth/login | 5/minute | Prevent brute force attacks |
| POST /auth/register | 5/minute | Prevent spam registrations |
| POST /payments/create-payment-intent | 10/minute | Prevent payment spam |

---

## Troubleshooting

### Error: "No module named 'slowapi'"

**Solution:**
```bash
pip install slowapi
```

### Error: Rate limiting not working

**Check:**
1. Server restarted after code changes?
2. SlowAPI installed?
3. Test script shows rate limiting?

### Error: Too restrictive for testing

**Temporary solution:**
Change limits in code:
```python
@limiter.limit("100/minute")  # More permissive for testing
```

---

## Next Steps

1. ✅ Test rate limiting works
2. ✅ Monitor logs for rate limit violations
3. ✅ Adjust limits based on usage patterns
4. 🔄 Consider Redis backend for production (multi-server)
5. 🔄 Add monitoring/alerting for abuse attempts

---

## Success Criteria

✅ Rate limiting is working if:
- First 5 login attempts succeed (or fail with 401)
- 6th login attempt returns 429 (Too Many Requests)
- After 60 seconds, requests work again

---

**For detailed documentation, see:** `RATE_LIMITING_IMPLEMENTATION.md`
