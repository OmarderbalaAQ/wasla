# Project Architecture Documentation

## Project Overview

**Wasla - Subscription Management Platform**

A full-stack web application for managing subscription-based services with multi-language support, payment processing, and analytics dashboard access. The platform allows users to purchase subscription bundles, access personalized dashboards, and manage their accounts through an intuitive interface.

---

## Technology Stack

### Backend Technologies

#### Core Framework
- **FastAPI** (Python 3.x)
  - Modern, fast web framework for building APIs
  - Automatic API documentation (Swagger/OpenAPI)
  - Async support for high performance
  - Built-in data validation with Pydantic

#### Database
- **SQLAlchemy** (ORM)
  - Object-Relational Mapping for database operations
  - Database-agnostic (currently using SQLite)
  - Migration support via Alembic
  
- **SQLite** (Development)
  - File-based database (`dev.db`)
  - Easy setup for development
  - Can be migrated to PostgreSQL/MySQL for production

#### Authentication & Security
- **OAuth2 with JWT (JSON Web Tokens)**
  - Token-based authentication
  - Secure password hashing with bcrypt
  - Role-based access control (User/Admin)
  
- **python-jose** - JWT token creation and validation
- **passlib[bcrypt]** - Password hashing and verification

#### Payment Processing
- **Stripe API**
  - Payment intent creation
  - Webhook handling for payment events
  - Subscription management
  - Multi-month discount support

#### Configuration Management
- **Pydantic Settings**
  - Environment variable management
  - Type-safe configuration
  - `.env` file support

### Frontend Technologies

#### Core Technologies
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with animations
- **Vanilla JavaScript** - No framework dependencies

#### Internationalization (i18n)
- **Custom i18n System**
  - JSON-based translations (English/Arabic)
  - Dynamic content translation
  - Language persistence via localStorage
  - Browser language detection
  - Smooth loading with FOUC prevention

#### UI/UX Features
- **Responsive Design** - Mobile-first approach
- **Custom CSS Framework** - `dd.css` with modern styling
- **Loading States** - Smooth transitions and spinners
- **Language Switcher** - Real-time language switching

#### Fonts & Icons
- **Google Fonts** - Inter font family
- **Emoji Icons** - Native emoji support for features
- **SVG Icons** - Custom tier badges (Silver, Gold, Platinum)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Browser    │  │   Mobile     │  │   Tablet     │      │
│  │  (Desktop)   │  │   Browser    │  │   Browser    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Static File Server                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Static Files Middleware                     │   │
│  │  - HTML Pages                                        │   │
│  │  - CSS Stylesheets                                   │   │
│  │  - JavaScript Files                                  │   │
│  │  - i18n JSON Files                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     Auth     │  │   Payments   │  │    Admin     │      │
│  │    Router    │  │    Router    │  │    Router    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Middleware Layer                          │   │
│  │  - CORS Middleware                                   │   │
│  │  - Authentication Middleware (OAuth2)                │   │
│  │  - Error Handling                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer (SQLite)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Users     │  │   Bundles    │  │   Payments   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Subscriptions │  │  Dashboards  │  │   Discount   │      │
│  │              │  │              │  │    Rules     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ External API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Stripe Payment Gateway                              │   │
│  │  - Payment Intents                                   │   │
│  │  - Webhooks                                          │   │
│  │  - Subscription Management                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend Architecture

### Project Structure

```
simple-auth-payments/
│
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── database.py             # Database connection and session
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic schemas for validation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
│
├── routers/                # API route handlers
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   ├── payments.py        # Payment and subscription endpoints
│   └── admin.py           # Admin management endpoints
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── security.py        # Password hashing, JWT tokens
│   └── bundle_helpers.py  # Bundle-related utilities
│
├── services/               # Business logic layer
│   └── (future service modules)
│
└── static/                 # Frontend files
    ├── *.html             # HTML pages
    ├── dd.css             # Main stylesheet
    ├── js/                # JavaScript files
    └── i18n/              # Translation files
```

### Core Components

#### 1. Main Application (`main.py`)

**Responsibilities:**
- FastAPI application initialization
- CORS middleware configuration
- Static file serving
- Router registration
- Database table creation
- Initial data seeding

**Key Features:**
```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(payments.router)
app.include_router(admin.router)
```

#### 2. Database Models (`models.py`)

**Database Schema:**

**User Model:**
- `id` - Primary key
- `email` - Unique, indexed
- `hashed_password` - Bcrypt hashed
- `full_name` - Optional
- `is_active` - Boolean flag
- `is_verified` - Email verification status
- `role` - "user" or "admin"
- `allow_access_without_subscription` - Admin override

**Bundle Model:**
- `id` - Primary key
- `name` - Bundle name
- `price_cents` - Price in cents (avoid float issues)
- `currency` - Currency code (default: "usd")
- `is_active` - Availability flag
- `tier_level` - 1=Silver, 2=Gold, 3=Platinum
- `logo_type` - Visual tier indicator
- `description` - Short description
- `main_description` - Detailed description

**Payment Model:**
- `id` - Primary key
- `user_id` - Foreign key to User
- `bundle_id` - Foreign key to Bundle
- `stripe_pi_id` - Stripe Payment Intent ID
- `amount_cents` - Final amount paid
- `currency` - Payment currency
- `status` - Payment status
- `created_at` - Timestamp
- `subscription_end_date` - Subscription expiry
- `months_purchased` - Subscription duration
- `discount_percentage` - Applied discount

**Subscription Model:**
- `id` - Primary key
- `user_id` - Foreign key to User
- `bundle_id` - Foreign key to Bundle
- `start_date` - Subscription start
- `end_date` - Subscription end
- `is_active` - Active status
- `auto_renew` - Auto-renewal flag

**Dashboard Model:**
- `id` - Primary key
- `user_id` - Foreign key to User (unique)
- `looker_studio_url` - Dashboard URL
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**DiscountRule Model:**
- `id` - Primary key
- `name` - Rule name
- `min_months` - Minimum months for discount
- `max_months` - Maximum months (nullable)
- `discount_percentage` - Discount amount
- `is_active` - Rule status

#### 3. API Routers

**Authentication Router (`routers/auth.py`)**

Endpoints:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT)
- `GET /auth/me` - Get current user info
- `GET /auth/me/subscription` - Get user's subscription status

**Payments Router (`routers/payments.py`)**

Endpoints:
- `GET /payments/bundles` - List available bundles
- `POST /payments/create-payment-intent` - Create Stripe payment
- `GET /payments/discount-options` - Get available discounts
- `POST /payments/webhook` - Stripe webhook handler

**Admin Router (`routers/admin.py`)**

Endpoints:
- `GET /admin/users` - List all users
- `GET /admin/payments` - List all payments
- `GET /admin/subscriptions` - List all subscriptions
- `GET /admin/bundles` - List all bundles
- `POST /admin/bundles` - Create new bundle
- `PUT /admin/bundles/{id}` - Update bundle
- `DELETE /admin/bundles/{id}` - Delete bundle
- `GET /admin/discount-rules` - List discount rules
- `POST /admin/discount-rules` - Create discount rule
- `PUT /admin/discount-rules/{id}` - Update discount rule
- `DELETE /admin/discount-rules/{id}` - Delete discount rule
- `POST /admin/users/{id}/grant-access` - Grant dashboard access
- `POST /admin/users/{id}/revoke-access` - Revoke dashboard access

#### 4. Security (`utils/security.py`)

**Features:**
- Password hashing with bcrypt
- JWT token generation
- JWT token validation
- Token expiration handling

**JWT Configuration:**
- Algorithm: HS256
- Expiration: 30 minutes (configurable)
- Secret key: From environment variables

#### 5. Configuration (`config.py`)

**Environment Variables:**
```python
DATABASE_URL              # Database connection string
JWT_SECRET_KEY           # Secret for JWT signing
JWT_ALGORITHM            # JWT algorithm (HS256)
ACCESS_TOKEN_EXPIRE_MINUTES  # Token expiration
STRIPE_SECRET_KEY        # Stripe API key
STRIPE_WEBHOOK_SECRET    # Stripe webhook secret
```

---

## Frontend Architecture

### Page Structure

**Public Pages:**
- `index.html` - Landing page
- `login.html` - User login
- `register.html` - User registration
- `solutions.html` - Solutions showcase
- `FAQ.html` - Frequently asked questions
- `form.html` - Contact form
- `pricing-non registered.html` - Public pricing page

**Authenticated Pages:**
- `dashboard.html` - Subscription plans (requires login)
- `client_home.html` - User dashboard
- `admin.html` - Admin panel (requires admin role)

### JavaScript Architecture

**Core Modules:**

1. **i18n.js** - Internationalization system
   - Language detection
   - Translation loading
   - Language switching
   - localStorage persistence

2. **i18n-preload.js** - FOUC prevention
   - Immediate loading state
   - Content hiding until translated

3. **page-translator.js** - Content translation
   - DOM element translation
   - Dynamic content handling
   - Page-specific translations

4. **language-switcher.js** - UI language switcher
   - Button event handling
   - Dropdown management
   - Visual state updates

5. **dynamic-content-i18n.js** - Dynamic content translation
   - API response translation
   - Form handling
   - Modal translations

### i18n System Architecture

**Translation Flow:**
```
1. Page loads → i18n-preload.js adds 'i18n-loading' class
2. Content hidden (CSS)
3. i18n.js initializes
4. Checks localStorage for saved language
5. If not found, detects browser language
6. Loads translation JSON file
7. Dispatches 'i18nReady' event
8. page-translator.js translates all elements
9. Removes 'i18n-loading' class
10. Content fades in (already translated)
```

**Translation Files:**
- `static/i18n/en.json` - English translations
- `static/i18n/ar.json` - Arabic translations

**Translation Structure:**
```json
{
  "common": { ... },
  "navigation": { ... },
  "footer": { ... },
  "pricingFeatures": { ... },
  "dashboard": { ... },
  "plans": { ... },
  "login": { ... },
  "register": { ... },
  "faq": { ... }
}
```

---

## Data Flow

### User Registration Flow

```
1. User fills registration form
2. Frontend sends POST /auth/register
3. Backend validates email uniqueness
4. Password hashed with bcrypt
5. User created in database
6. Success response returned
7. User redirected to login
```

### Authentication Flow

```
1. User submits login credentials
2. Frontend sends POST /auth/login
3. Backend verifies email and password
4. JWT token generated
5. Token returned to frontend
6. Token stored in localStorage
7. Token included in subsequent requests (Authorization header)
```

### Payment Flow

```
1. User selects bundle and duration
2. Frontend calculates price with discounts
3. POST /payments/create-payment-intent
4. Backend:
   - Validates bundle
   - Applies discount rules
   - Creates Stripe Payment Intent
   - Returns client_secret
5. Frontend would integrate Stripe Elements (not implemented)
6. Payment confirmed via webhook
7. Subscription created
8. Dashboard access granted
```

### Subscription Access Flow

```
1. User navigates to client_home.html
2. Frontend sends GET /auth/me/subscription
3. Backend checks:
   - Admin override (allow_access_without_subscription)
   - Active subscription (end_date > now)
4. Returns:
   - has_access: boolean
   - subscription_end_date: datetime
   - bundle_name: string
   - dashboard_url: string
5. Frontend shows/hides dashboard access
```

---

## Security Features

### Authentication Security
- **Password Hashing:** Bcrypt with salt
- **JWT Tokens:** Signed with secret key
- **Token Expiration:** 30-minute default
- **HTTPS Required:** For production

### Authorization
- **Role-Based Access Control (RBAC)**
  - User role: Standard access
  - Admin role: Full system access
- **Endpoint Protection:** OAuth2 dependency
- **Admin-Only Endpoints:** Role verification

### Data Security
- **SQL Injection Prevention:** SQLAlchemy ORM
- **XSS Prevention:** Content sanitization
- **CORS Configuration:** Controlled origins
- **Environment Variables:** Sensitive data protection

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐         ┌─────────────┐
│    User     │         │   Bundle    │
├─────────────┤         ├─────────────┤
│ id (PK)     │         │ id (PK)     │
│ email       │         │ name        │
│ password    │         │ price_cents │
│ full_name   │         │ tier_level  │
│ role        │         │ is_active   │
└─────────────┘         └─────────────┘
       │                       │
       │                       │
       │    ┌──────────────────┘
       │    │
       ▼    ▼
┌─────────────────┐
│    Payment      │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ bundle_id (FK)  │
│ stripe_pi_id    │
│ amount_cents    │
│ months_purchased│
│ discount_%      │
└─────────────────┘
       │
       │
       ▼
┌─────────────────┐
│  Subscription   │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ bundle_id (FK)  │
│ start_date      │
│ end_date        │
│ is_active       │
└─────────────────┘

┌─────────────────┐
│  Dashboard      │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ looker_url      │
└─────────────────┘

┌─────────────────┐
│ DiscountRule    │
├─────────────────┤
│ id (PK)         │
│ name            │
│ min_months      │
│ max_months      │
│ discount_%      │
│ is_active       │
└─────────────────┘
```

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

### Automatic Documentation
FastAPI provides automatic interactive API documentation:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Deployment Considerations

### Production Checklist

**Backend:**
- [ ] Change DATABASE_URL to PostgreSQL/MySQL
- [ ] Set strong JWT_SECRET_KEY
- [ ] Configure production Stripe keys
- [ ] Enable HTTPS
- [ ] Set proper CORS origins
- [ ] Configure logging
- [ ] Set up database backups
- [ ] Use production WSGI server (Gunicorn/Uvicorn)

**Frontend:**
- [ ] Minify JavaScript and CSS
- [ ] Optimize images
- [ ] Enable CDN for static files
- [ ] Configure caching headers
- [ ] Test on multiple browsers
- [ ] Mobile responsiveness testing

**Security:**
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure firewall rules
- [ ] Regular security audits
- [ ] Keep dependencies updated

---

## Development Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation Steps

1. **Clone repository**
```bash
git clone <repository-url>
cd simple-auth-payments
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
# Tables are created automatically on first run
```

6. **Start development server**
```bash
uvicorn main:app --reload
```

7. **Access application**
- Frontend: `http://localhost:8000/static/index.html`
- API Docs: `http://localhost:8000/docs`

---

## Testing

### Test Files
- `test_admin_api.py` - Admin endpoint tests
- `test_bundle_api.py` - Bundle management tests
- `test_dashboard_api.py` - Dashboard access tests
- `test_discount_system.py` - Discount calculation tests
- `test_database_models.py` - Model validation tests

### Running Tests
```bash
pytest
```

---

## Future Enhancements

### Planned Features
- [ ] Email verification system
- [ ] Password reset functionality
- [ ] Two-factor authentication (2FA)
- [ ] Subscription auto-renewal
- [ ] Invoice generation
- [ ] Usage analytics
- [ ] Multi-currency support
- [ ] Webhook retry mechanism
- [ ] Admin dashboard analytics
- [ ] User profile management

### Scalability Improvements
- [ ] Redis caching layer
- [ ] Message queue (Celery)
- [ ] Database read replicas
- [ ] CDN integration
- [ ] Microservices architecture
- [ ] Kubernetes deployment

---

## Support & Maintenance

### Logging
- Application logs: Console output
- Error tracking: (To be implemented)
- Performance monitoring: (To be implemented)

### Monitoring
- Health check endpoint: `/`
- Database connection monitoring
- API response time tracking

### Backup Strategy
- Database: Daily automated backups
- Configuration: Version controlled
- Static files: CDN backup

---

## License & Credits

**Project:** Wasla - Subscription Management Platform
**Version:** 1.0.0
**Last Updated:** 2025

**Technologies Used:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- Stripe - Payment processing
- JWT - Authentication
- Custom i18n - Internationalization

---

## Contact & Documentation

For more information, refer to:
- **Security Architecture:** `SECURITY_ARCHITECTURE.md` - Comprehensive security analysis with API sequences
- API Documentation: `/docs`
- i18n Guide: `LANGUAGE_PERSISTENCE_GUIDE.md`
- Smooth Loading: `SMOOTH_LOADING_IMPLEMENTATION.md`
- Dashboard i18n: `DASHBOARD_I18N_COMPLETE.md`

---

## Security Documentation

For detailed security analysis, API endpoint documentation, threat modeling, and security best practices, see:

**📄 [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md)**

This comprehensive security document includes:
- Complete API endpoint documentation with request/response examples
- Detailed security flow diagrams for all major operations
- Threat model with 10 threat categories and mitigations
- Security best practices and recommendations
- Production security checklist
- Incident response plan
- Compliance considerations (GDPR, PCI DSS)

---

**End of Architecture Documentation**
