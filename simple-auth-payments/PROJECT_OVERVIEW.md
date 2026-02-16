# 📋 Project Overview - Simple Auth Payments System

## 🎯 Project Purpose
A complete FastAPI-based subscription management system with:
- User authentication (JWT)
- Stripe payment integration
- Multi-tier subscription plans
- Admin dashboard for management
- Client dashboard for accessing Looker Studio reports

---

## 🏗️ Current Architecture

### Backend (FastAPI)
- **Framework:** FastAPI + Uvicorn
- **Database:** SQLite (dev.db)
- **Authentication:** JWT tokens with OAuth2
- **Payment:** Stripe API integration
- **ORM:** SQLAlchemy

### Frontend (HTML/CSS/JS)
- **Style:** Custom CSS (static/style.css)
- **Pages:** Login, Register, Client Home, Admin Dashboard, Bundles
- **Framework:** Vanilla JavaScript (no framework)

---

## 📊 Database Schema

### Tables:
1. **users** - User accounts
   - id, email, hashed_password, full_name
   - is_active, is_verified, role
   - allow_access_without_subscription (admin override)

2. **bundles** - Subscription plans
   - id, name, price_cents, currency
   - is_active, tier_level (1=Basic, 2=Pro, 3=Premium)

3. **subscriptions** - Active subscriptions
   - id, user_id, bundle_id
   - start_date, end_date, is_active
   - auto_renew

4. **payments** - Payment transactions
   - id, user_id, bundle_id, stripe_pi_id
   - amount_cents, currency, status
   - months_purchased, discount_percentage
   - created_at

5. **dashboards** - Looker Studio links
   - id, user_id, looker_studio_url
   - created_at, updated_at

---

## 🔑 Key Features Implemented

### Authentication & Authorization
- ✅ User registration with password hashing (bcrypt)
- ✅ JWT token-based authentication
- ✅ Role-based access (admin/user)
- ✅ Protected routes with OAuth2

### Subscription Management
- ✅ Multi-tier plans (Basic, Pro, Premium)
- ✅ Multi-month discounts (6mo=10%, 12mo=20%)
- ✅ Tier-based logic (lower tier waits for higher tier to expire)
- ✅ Subscription tracking with expiry dates
- ✅ Admin override for free access

### Payment Processing
- ✅ Stripe PaymentIntent creation
- ✅ Webhook handling for payment confirmation
- ✅ Discount calculation
- ✅ Payment history tracking

### Admin Dashboard
- ✅ User management (create, edit, delete)
- ✅ Subscription viewing
- ✅ Dashboard link management
- ✅ Payment history
- ✅ Bundle management
- ✅ Access override controls

### Client Experience
- ✅ Smart login redirects based on role/subscription
- ✅ Client home page with dashboard access
- ✅ Subscription status display
- ✅ Bundle purchase flow

---

## 📁 Project Structure

```
simple-auth-payments/
├── main.py                 # FastAPI app entry point
├── config.py               # Settings (pydantic-settings)
├── database.py             # SQLAlchemy setup
├── models.py               # Database models
├── schemas.py              # Pydantic schemas
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
│
├── routers/
│   ├── auth.py            # Authentication endpoints
│   ├── payments.py        # Payment & subscription endpoints
│   └── admin.py           # Admin management endpoints
│
├── services/
│   └── stripe_service.py  # Stripe API wrapper
│
├── utils/
│   └── security.py        # Password hashing & JWT
│
└── static/
    ├── style.css          # Main stylesheet
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── client_home.html   # Client landing page
    ├── dashboard.html     # Bundles/plans page
    └── admin.html         # Admin dashboard
```

---

## 🔗 API Endpoints

### Authentication
- `POST /auth/register` - Create new user
- `POST /auth/login` - Login (returns JWT)
- `GET /auth/me` - Get current user
- `GET /auth/me/subscription` - Get subscription status

### Payments
- `GET /payments/bundles` - List available plans
- `POST /payments/create-payment-intent` - Create payment
- `POST /payments/webhook` - Stripe webhook handler

### Admin
- `GET /admin/users` - List all users
- `POST /admin/users/create` - Create user
- `PUT /admin/users/{id}/role` - Change role
- `PUT /admin/users/{id}/status` - Activate/deactivate
- `PUT /admin/users/{id}/access-override` - Grant/remove access
- `DELETE /admin/users/{id}` - Delete user
- `GET /admin/subscriptions` - List all subscriptions
- `GET /admin/dashboards` - List all dashboards
- `POST /admin/dashboards` - Create/update dashboard
- `GET /admin/payments` - List all payments
- `GET /admin/bundles` - List all bundles
- `POST /admin/bundles` - Create bundle
- `GET /admin/stats` - Get statistics

---

## 🧪 Test Accounts

1. **Admin:** admin@admin.com / admin123
2. **Client with subscription:** client@test.com / client123
3. **User without subscription:** user@test.com / user123
4. **User with admin override:** override@test.com / override123

---

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Access at: http://localhost:8000
```

---

## 📝 Current Status

### ✅ Completed:
- Backend API fully functional
- Database schema complete
- Authentication system working
- Payment integration ready
- Admin dashboard functional
- Client pages working
- Subscription logic implemented

### 🔄 Remaining Tasks:
1. Redesign admin page with consistent CSS
2. Redesign dashboard page with consistent CSS
3. Connect page links properly
4. Add i18n support (internationalization)
5. Add language switcher in navbar
6. Create translation JSON files
7. Final backend integration testing

---

## 🎨 Design System

### Current CSS Variables (style.css):
- Primary color: #667eea (purple)
- Secondary: #764ba2 (darker purple)
- Success: #28a745 (green)
- Danger: #dc3545 (red)
- Warning: #ffc107 (yellow)

### Typography:
- Font: Inter (Google Fonts)
- Weights: 400, 500, 600, 700, 900

### Components:
- Cards with border-radius: 12px
- Buttons with hover effects
- Tables with alternating rows
- Badges for status indicators
- Tabs for navigation

---

## 🔐 Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- CORS enabled for development
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- Protected admin routes

---

## 💾 Database Location

- **File:** `dev.db` (SQLite)
- **Created automatically** on first run
- **Pre-seeded** with test data

---

## 📚 Documentation Files

- `PROJECT_OVERVIEW.md` - This file
- `COMPLETE_SYSTEM_GUIDE.md` - Full feature guide
- `ADMIN_DASHBOARD_GUIDE.md` - Admin features
- `TEST_ALL_FEATURES.txt` - Testing checklist
- `CLEAR_CACHE_INSTRUCTIONS.txt` - Browser cache fix

---

## 🌐 URLs

- Login: http://localhost:8000/static/login.html
- Register: http://localhost:8000/static/register.html
- Client Home: http://localhost:8000/static/client_home.html
- Bundles: http://localhost:8000/static/dashboard.html
- Admin: http://localhost:8000/static/admin.html
- API Docs: http://localhost:8000/docs

---

This project is ready for the next phase: UI redesign and i18n implementation.
