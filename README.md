# MediHelp Dispensary API

A robust backend API for a Medical Dispensary Queue Management System built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- **Admin Authentication** - Secure JWT-based authentication for admin users
- **Doctor Management** - CRUD operations for managing doctors and their specializations
- **Session Management** - Create and manage doctor consultation sessions with time slots
- **Queue Management** - Smart queue system with automatic slot allocation
- **Booking System** - Patient booking with email confirmations and secure tracking
- **Email Notifications** - SMTP-based booking confirmation emails

## Tech Stack

- **Framework:** FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0 ORM
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose) with bcrypt password hashing
- **Validation:** Pydantic v2
- **Email:** SMTP support (Gmail compatible)

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/
│   │   ├── endpoints/    # API route handlers
│   │   │   ├── auth.py       # Admin authentication
│   │   │   ├── bookings.py   # Patient bookings
│   │   │   ├── doctors.py    # Doctor management
│   │   │   └── sessions.py   # Session management
│   │   ├── dependencies.py   # Dependency injection
│   │   └── router.py         # API router configuration
│   ├── core/
│   │   └── config.py     # Application settings
│   ├── db/
│   │   └── database.py   # Database connection
│   ├── models/
│   │   └── models.py     # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py    # Pydantic schemas
│   ├── services/
│   │   └── email_service.py  # Email functionality
│   └── main.py           # Application entry point
├── scripts/
│   ├── create_admin.py   # Admin user creation script
│   └── seed_data.py      # Database seeding script
├── .env.example          # Environment variables template
├── alembic.ini           # Alembic configuration
└── requirements.txt      # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medihelp-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update the following:
   - `DATABASE_URL` - Your PostgreSQL connection string
   - `SECRET_KEY` - A secure random key for JWT signing
   - `SMTP_*` - Email configuration (optional, for booking confirmations)

5. **Create the database**
   ```bash
   # Connect to PostgreSQL and create the database
   psql -U postgres
   CREATE DATABASE medihelp_db;
   \q
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Create an admin user**
   ```bash
   python -m scripts.create_admin
   ```

### Running the Application

**Development mode:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### API Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/auth/login` | POST | Admin login |
| `/api/v1/doctors` | GET, POST | List/Create doctors |
| `/api/v1/doctors/{id}` | GET, PUT, DELETE | Get/Update/Delete doctor |
| `/api/v1/sessions` | GET, POST | List/Create sessions |
| `/api/v1/sessions/{id}` | GET, PUT, DELETE | Get/Update/Delete session |
| `/api/v1/bookings` | POST | Create a booking |
| `/api/v1/bookings/{reference}` | GET | Get booking by reference |
| `/health` | GET | Health check |

## Database Models

- **Admin** - System administrators
- **Doctor** - Medical practitioners with specializations
- **DoctorSession** - Scheduled consultation sessions
- **QueueSlot** - Individual queue positions within sessions
- **Booking** - Patient booking records
- **Patient** - Patient information linked to bookings

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing secret | Required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username | Required for email |
| `SMTP_PASSWORD` | SMTP password | Required for email |
| `SMTP_FROM` | Sender email address | Required for email |
| `PATIENT_WEB_URL` | Frontend URL for patients | `http://localhost:3000` |
| `ADMIN_WEB_URL` | Frontend URL for admin | `http://localhost:3001` |

## Development

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Seeding Test Data

```bash
python -m scripts.seed_data
```

## License

This project is licensed under the MIT License.
