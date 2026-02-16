# 🎯 Simple Auth Payments - Subscription Management System

A complete FastAPI-based subscription management system with authentication, payment processing, and admin dashboard.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd simple-auth-payments
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file:
```env
DATABASE_URL=sqlite:///./dev.db
JWT_SECRET_KEY=your-secret-key-here
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 3. Run Server
```bash
uvicorn main:app --reload
```

Server starts at: **http://localhost:8000**

### 4. Access Application
- **Login:** http://localhost:8000/static/login.html
- **Admin:** http://localhost:8000/static/admin.html
- **API Docs:** http://localhost:8000/docs

---

## 🔑 Test Accounts

| Role | Email | Password | Access |
|------|-------|----------|--------|
| Admin | admin@admin.com | admin123 | Full admin access |
| Client | client@test.com | client123 | Active subscription |
| User | user@test.com | user123 | No subscription |
| Override | override@test.com | override123 | Admin-granted access |

---

## ✨ Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (admin/user)
- Password hashing with bcrypt
- OAuth2 password flow

### Subscription Management
- Multi-tier plans (Basic, Pro, Premium)
- Multi-month discounts (6mo=10%, 12mo=20%)
- Tier-based subscription logic
- Automatic expiry tracking
- Admin override for free access

### Payment Processing
- Stripe integration
- PaymentIntent creation
- Webhook handling
- Discount calculation
- Payment history

### Admin Dashboard
- User management
- Subscription tracking
- Dashboard link management
- Payment history
- Bundle management
- System statistics

### Client Experience
- Smart login redirects
- Subscription status display
- Dashboard access control
- Bundle purchase flow

---

## 📁 Project Structure

```
simple-auth-payments/
├── main.py                 # FastAPI app
├── config.py               # Settings
├── database.py             # Database setup
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
│
├── routers/
│   ├── auth.py            # Authentication
│   ├── payments.py        # Payments & subscriptions
│   └── admin.py           # Admin management
│
├── services/
│   └── stripe_service.py  # Stripe integration
│
├── utils/
│   └── security.py        # Security utilities
│
└── static/
    ├── style.css          # Styles
    ├── login.html         # Login page
    ├── register.html      # Registration
    ├── client_home.html   # Client landing
    ├── dashboard.html     # Plans/bundles
    └── admin.html         # Admin dashboard
```

---

## 🗄️ Database Schema

### Tables
- **users** - User accounts with roles
- **bundles** - Subscription plans with tiers
- **subscriptions** - Active subscriptions
- **payments** - Payment transactions
- **dashboards** - Looker Studio links

---

## 🔗 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (returns JWT)
- `GET /auth/me` - Get current user
- `GET /auth/me/subscription` - Get subscription status

### Payments
- `GET /payments/bundles` - List plans
- `POST /payments/create-payment-intent` - Create payment
- `POST /payments/webhook` - Stripe webhook

### Admin (Protected)
- `GET /admin/users` - List users
- `POST /admin/users/create` - Create user
- `GET /admin/subscriptions` - List subscriptions
- `GET /admin/dashboards` - List dashboards
- `POST /admin/dashboards` - Create/update dashboard
- `GET /admin/payments` - List payments
- `GET /admin/stats` - Get statistics

Full API documentation: http://localhost:8000/docs

---

## 🧪 Testing

### Test Complete Flow
1. Register new user
2. Login
3. View available plans
4. Purchase subscription (test multi-month discounts)
5. Access client dashboard
6. Login as admin
7. View all admin tabs
8. Manage users and subscriptions

### Test Admin Features
1. Create new user
2. Grant access override
3. Create dashboard link
4. View subscription status
5. Check payment history

---

## 📚 Documentation

- **PROJECT_OVERVIEW.md** - Complete architecture guide
- **COMPLETE_SYSTEM_GUIDE.md** - Feature documentation
- **ADMIN_DASHBOARD_GUIDE.md** - Admin features
- **NEXT_PHASE_GUIDE.md** - Next development steps
- **TEST_ALL_FEATURES.txt** - Testing checklist

---

## 🔐 Security

- Password hashing with bcrypt
- JWT tokens with expiration
- Protected admin routes
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- CORS configuration

---

## 🛠️ Development

### Setup Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload

# Run migrations (if needed)
python migrate_full.py

# Setup test data
python setup_complete_system.py
```

### Database Management
```bash
# Create admin user
python quick_create_admin.py

# Migrate database
python migrate_full.py

# Setup complete system
python setup_complete_system.py
```

---

## 🌐 Deployment

### Environment Variables
Set these in production:
- `DATABASE_URL` - Production database URL
- `JWT_SECRET_KEY` - Strong random secret
- `STRIPE_SECRET_KEY` - Production Stripe key
- `STRIPE_WEBHOOK_SECRET` - Production webhook secret

### CORS Configuration
Update `main.py` to restrict origins in production:
```python
allow_origins=["https://yourdomain.com"]
```

---

## 📝 Next Steps

See `NEXT_PHASE_GUIDE.md` for:
1. UI redesign instructions
2. i18n implementation guide
3. Navigation improvements
4. Language switcher setup

---

## 🐛 Troubleshooting

### Browser Shows Old Content
**Solution:** Clear browser cache
- Press `Ctrl + Shift + R` (hard refresh)
- Or clear cache in browser settings

### Database Errors
**Solution:** Run migration
```bash
python migrate_full.py
```

### Import Errors
**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

---

## 📄 License

This project is for educational/commercial use.

---

## 🤝 Support

For issues or questions:
1. Check documentation files
2. Review API docs at `/docs`
3. Test with provided test accounts

---

## 🎉 Credits

Built with:
- FastAPI
- SQLAlchemy
- Stripe
- JWT
- Bcrypt

---

**Ready to use!** Start the server and login with test accounts. 🚀
