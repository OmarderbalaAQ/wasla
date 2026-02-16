# 🚀 Render Deployment Guide for Wasla

## Quick Setup (5 minutes)

### 1. Prepare Your Repository

Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (easiest option)
3. Authorize Render to access your repositories

### 3. Deploy Your App

#### Option A: Using render.yaml (Recommended)
1. Click "New +" → "Blueprint"
2. Connect your GitHub repository
3. Render will auto-detect `render.yaml`
4. Click "Apply"

#### Option B: Manual Setup
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - Name: `wasla-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: `Free`

### 4. Configure Environment Variables

In Render Dashboard → Environment:

**Required:**
```
DATABASE_URL=sqlite:///./prod.db
JWT_SECRET_KEY=<generate-strong-random-key>
STRIPE_SECRET_KEY=sk_live_your_actual_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

**Optional (Email):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@wasla.com
ADMIN_EMAILS=admin@wasla.com
ENABLE_EMAIL_NOTIFICATIONS=true
```

**Generate JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Update CORS Settings

After deployment, update `main.py` with your Render URL:

```python
allow_origins=[
    "https://your-app-name.onrender.com",  # Your Render URL
    "https://www.yourdomain.com",  # Your custom domain (if any)
]
```

Commit and push to trigger redeployment.

### 6. Get Your Live URL

After deployment completes (2-3 minutes):
- Your API: `https://your-app-name.onrender.com`
- Test it: `https://your-app-name.onrender.com/`

---

## Important Notes

### Free Tier Limitations
- **Sleeps after 15 min inactivity** → First request takes 30-50 seconds
- **750 hours/month** (enough for one service)
- **Limited CPU/RAM** → Good for small traffic
- **No persistent disk** → Use PostgreSQL for production data

### Database Considerations

**Current Setup (SQLite):**
- ✅ Works for testing
- ❌ Data lost on service restart
- ❌ Not suitable for production

**Recommended: PostgreSQL (Free on Render)**
1. Create PostgreSQL database in Render
2. Update `DATABASE_URL` to PostgreSQL connection string
3. Update `requirements.txt`:
```
psycopg2-binary
```

### Custom Domain Setup

1. In Render Dashboard → Settings → Custom Domain
2. Add your domain: `www.yourdomain.com`
3. Update DNS records (Render provides instructions)
4. Free SSL certificate auto-generated

### Monitoring

- View logs: Dashboard → Logs
- Check metrics: Dashboard → Metrics
- Set up alerts: Dashboard → Notifications

---

## Troubleshooting

### Service Won't Start
- Check logs in Render Dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` is complete

### Database Errors
- SQLite limitations on Render
- Consider upgrading to PostgreSQL

### CORS Errors
- Update `allow_origins` in `main.py`
- Include your Render URL
- Redeploy after changes

### Slow First Request
- Normal for free tier (cold start)
- Consider paid plan ($7/month) for always-on

---

## Upgrade to PostgreSQL (Recommended)

### 1. Create Database
```
Render Dashboard → New + → PostgreSQL
Name: wasla-db
Plan: Free
```

### 2. Update Code

`requirements.txt`:
```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary  # Add this
alembic
passlib[bcrypt]
python-jose[cryptography]
python-dotenv
stripe
pydantic
pydantic-settings
python-multipart
slowapi
hypothesis
pytest
```

### 3. Update Environment Variable
Copy the "Internal Database URL" from PostgreSQL dashboard and set as `DATABASE_URL`

### 4. Redeploy
Render will automatically redeploy with new database.

---

## Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong JWT_SECRET_KEY
- [ ] Use Stripe live keys (not test keys)
- [ ] Update CORS origins with actual domain
- [ ] Enable HSTS in production (uncomment in main.py)
- [ ] Set up custom domain
- [ ] Configure email notifications
- [ ] Test all endpoints
- [ ] Set up monitoring/alerts
- [ ] Create first admin user

---

## Cost Breakdown

**Free Tier:**
- Web Service: Free (with limitations)
- PostgreSQL: Free (256MB storage)
- SSL Certificate: Free
- Total: $0/month

**Paid Tier (Recommended for Production):**
- Web Service: $7/month (always-on, better performance)
- PostgreSQL: $7/month (1GB storage)
- Total: $14/month

---

## Next Steps

1. Deploy to Render using this guide
2. Test your live API
3. Update frontend to use Render URL
4. Set up PostgreSQL for production
5. Configure custom domain
6. Enable email notifications

Need help? Check Render docs: https://render.com/docs
