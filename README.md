# 💰 Finance Dashboard API

A production-grade backend for a finance dashboard system built with **FastAPI**, featuring role-based access control, financial record management, and analytics endpoints.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
├─────────────────────────────────────────────────────────────────┤
│  Middleware Layer   │ CORS │ Request ID │ Rate Limiting          │
├─────────────────────────────────────────────────────────────────┤
│  Router Layer       │ Auth │ Users │ Records │ Dashboard         │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer      │ Business Logic & Validation                │
├─────────────────────────────────────────────────────────────────┤
│  Repository Layer   │ Data Access & Query Building               │
├─────────────────────────────────────────────────────────────────┤
│  Database           │ SQLAlchemy 2.0 + SQLite                    │
└─────────────────────────────────────────────────────────────────┘
```

**Design Principles:**
- **Layered Architecture** — Router → Service → Repository → Database
- **Separation of Concerns** — Each layer has a single responsibility
- **Dependency Injection** — FastAPI's `Depends()` for clean DI
- **Soft Deletes** — Records are never permanently removed (`deleted_at` timestamp)
- **Fail-Fast Config** — Missing environment variables cause immediate startup failure

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/VatsalRaina01/Backend_Assignment_Vastal
cd Backend_Assignment_Vastal

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set a secure JWT_SECRET_KEY
```

### 3. Seed Database (Optional)

```bash
python -m app.seed
```

This creates:
- **3 demo users** (admin, analyst, viewer)
- **200+ financial records** across 8 categories spanning 12 months

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔐 Authentication & Authorization

### Auth Flow
1. **Register** → `POST /api/v1/auth/register` — Get a JWT token
2. **Login** → `POST /api/v1/auth/login` — Authenticate and get a token
3. **Use Token** → Add `Authorization: Bearer <token>` header to all requests

### Role-Based Access Control (RBAC)

| Feature              | Viewer | Analyst | Admin |
|:---------------------|:------:|:-------:|:-----:|
| View records         |   ✅   |   ✅    |  ✅   |
| Dashboard analytics  |   ❌   |   ✅    |  ✅   |
| Create/Edit records  |   ❌   |   ❌    |  ✅   |
| Delete records       |   ❌   |   ❌    |  ✅   |
| Manage users         |   ❌   |   ❌    |  ✅   |

### Demo Credentials

| Role    | Email                  | Password      |
|:--------|:-----------------------|:--------------|
| Admin   | admin@example.com      | admin123456   |
| Analyst | analyst@example.com    | analyst123456 |
| Viewer  | viewer@example.com     | viewer123456  |

---

## 📋 API Endpoints

### Auth (`/api/v1/auth`)
| Method | Endpoint    | Description           | Access       |
|:-------|:------------|:----------------------|:-------------|
| POST   | `/register` | Register new user     | Public       |
| POST   | `/login`    | Login & get token     | Public       |
| GET    | `/me`       | Get current profile   | Authenticated|

### Users (`/api/v1/users`) — Admin Only
| Method | Endpoint     | Description        |
|:-------|:-------------|:-------------------|
| GET    | `/`          | List users (paginated, filterable) |
| GET    | `/{user_id}` | Get user by ID     |
| PATCH  | `/{user_id}` | Update user role/status |
| DELETE | `/{user_id}` | Soft-delete user   |

### Financial Records (`/api/v1/records`)
| Method | Endpoint       | Description                    | Access      |
|:-------|:---------------|:-------------------------------|:------------|
| GET    | `/`            | List records (filter, search, paginate) | All roles |
| GET    | `/{record_id}` | Get single record              | All roles   |
| POST   | `/`            | Create a record                | Admin only  |
| PATCH  | `/{record_id}` | Update a record                | Admin only  |
| DELETE | `/{record_id}` | Soft-delete a record           | Admin only  |

**Query Parameters for listing:**
- `type` — Filter by `income` or `expense`
- `category` — Filter by category name
- `start_date` / `end_date` — Date range filter (YYYY-MM-DD)
- `search` — Full-text search in descriptions
- `sort_by` — Sort by `date`, `amount`, `created_at`, or `category`
- `sort_order` — `asc` or `desc`
- `page` / `limit` — Pagination (max 100 per page)

### Dashboard Analytics (`/api/v1/dashboard`) — Analyst & Admin
| Method | Endpoint              | Description                           |
|:-------|:----------------------|:--------------------------------------|
| GET    | `/summary`            | Total income, expenses, net balance   |
| GET    | `/category-breakdown` | Per-category income/expense breakdown |
| GET    | `/trends`             | Monthly income/expense trend data     |
| GET    | `/recent-activity`    | Most recent financial transactions    |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_auth.py -v
```

**Test Coverage:**
- **46 tests** across 4 test modules
- Auth: registration, login, profile, validation, error handling
- Users: RBAC enforcement, CRUD operations, self-delete prevention
- Records: CRUD, filtering, pagination, search, soft delete, RBAC
- Dashboard: analytics accuracy, response shapes, RBAC enforcement

---

## 📁 Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # App factory (lifespan, middleware, routers)
│   ├── config.py               # Pydantic Settings (env var management)
│   ├── database.py             # SQLAlchemy engine, session, init_db()
│   ├── dependencies.py         # FastAPI DI (auth, db session, RBAC)
│   ├── seed.py                 # Database seeder with realistic demo data
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py             # User model (roles, soft delete)
│   │   └── record.py           # FinancialRecord model (Decimal precision)
│   │
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── auth.py             # Register, Login, Token, Profile
│   │   ├── user.py             # UserResponse, UpdateUser, ListParams
│   │   ├── record.py           # CreateRecord, UpdateRecord, ListParams
│   │   └── dashboard.py        # Summary, CategoryBreakdown, Trends
│   │
│   ├── repositories/           # Data access layer (query builders)
│   │   ├── user_repository.py
│   │   ├── record_repository.py
│   │   └── dashboard_repository.py
│   │
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── record_service.py
│   │   └── dashboard_service.py
│   │
│   ├── routers/                # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── records.py
│   │   └── dashboard.py
│   │
│   ├── middleware/
│   │   └── request_id.py       # X-Request-ID tracing middleware
│   │
│   └── utils/
│       ├── security.py         # JWT + bcrypt password hashing
│       ├── exceptions.py       # Custom exception hierarchy
│       ├── exception_handlers.py # Global error handlers
│       └── response.py         # Standardized JSON response helpers
│
├── tests/
│   ├── conftest.py             # Fixtures (in-memory DB, test client, users)
│   ├── test_auth.py            # Auth endpoint tests (11 tests)
│   ├── test_users.py           # User management tests (8 tests)
│   ├── test_records.py         # Record CRUD tests (17 tests)
│   └── test_dashboard.py       # Dashboard analytics tests (10 tests)
│
├── .env.example                # Environment variable template
├── .gitignore
├── requirements.txt            # Pinned dependencies
└── README.md
```

---

## 🔧 Technical Decisions

| Decision | Rationale |
|:---------|:----------|
| **SQLite default** | Zero-setup for demos; swappable to PostgreSQL via `DATABASE_URL` |
| **Sync SQLAlchemy** | Simplicity over async for a demo — easier debugging |
| **bcrypt (direct)** | `passlib` is unmaintained and incompatible with bcrypt ≥4.1 |
| **No Alembic** | `Base.metadata.create_all()` for demo; Alembic recommended for production |
| **UUID primary keys** | Globally unique, safe for distributed systems |
| **Soft deletes** | Audit trail preservation — `deleted_at` instead of hard deletes |
| **Numeric(12,2)** | Financial precision — avoids floating-point rounding errors |
| **Standardized responses** | All endpoints return `{success, data, message, meta}` envelope |

---

## 🛡️ Security Features

- **JWT Authentication** — Stateless, token-based auth with configurable expiration
- **bcrypt Password Hashing** — Industry-standard, salted password hashing
- **Role-Based Access Control** — Declarative RBAC via `RoleChecker` dependency
- **Input Validation** — Pydantic v2 schemas validate all inputs
- **Rate Limiting** — `slowapi` prevents brute-force attacks
- **CORS Middleware** — Configurable cross-origin resource sharing
- **Request ID Tracing** — UUID per request for log correlation
- **No Password Leaks** — Passwords are never included in API responses

---

## 📊 Response Format

All endpoints return a consistent JSON envelope:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

Paginated responses include metadata:

```json
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Financial record with id 'abc' not found"
  }
}
```

---

## 🔄 Production Considerations

For a production deployment, the following would be added:

- **PostgreSQL** — Replace SQLite via `DATABASE_URL`
- **Alembic Migrations** — Schema versioning and safe migrations
- **Redis** — Rate limiting backend and session caching
- **Docker** — Containerized deployment with `docker-compose`
- **CI/CD** — GitHub Actions pipeline for lint, test, deploy
- **Logging** — Structured JSON logging to stdout (12-factor app)
- **Monitoring** — Prometheus metrics + Sentry error tracking
- **API Versioning** — Already prefixed under `/api/v1/`

---

## 📄 License

This project was built as an assignment submission.
