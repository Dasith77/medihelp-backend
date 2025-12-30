# MediHelp Dispensary API

A FastAPI backend for a medical dispensary queue management system. Enables patients to book appointments, track queue status in real-time, and allows administrators to manage doctors, sessions, and queues.

## Features

- **Admin Management**: Secure JWT authentication for administrators
- **Doctor Management**: CRUD operations for doctor profiles
- **Session Scheduling**: Create and manage doctor consultation sessions
- **Queue System**: Automated queue slot generation with estimated wait times
- **Patient Booking**: Public booking system with email confirmations
- **Real-time Tracking**: Patients can track their queue position via secure links

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) with bcrypt password hashing
- **Validation**: Pydantic v2
- **Email**: SMTP with HTML templates

## Project Structure

```
medihelp-backend/
├── app/
│   ├── api/
│   │   ├── endpoints/      # API route handlers
│   │   ├── dependencies.py # Auth dependencies
│   │   └── router.py       # Main API router
│   ├── core/
│   │   ├── config.py       # Settings management
│   │   └── security.py     # JWT & password utils
│   ├── db/
│   │   └── database.py     # Database connection
│   ├── models/
│   │   └── models.py       # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py      # Pydantic schemas
│   ├── services/
│   │   └── email_service.py
│   └── main.py             # Application entry point
├── alembic/                # Database migrations
├── scripts/                # Utility scripts
├── requirements.txt
└── .env.example
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 13+

### Setup

1. **Clone and navigate to project**
   ```bash
   cd medihelp-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE medihelp_db;
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

7. **Seed sample data (optional)**
   ```bash
   python -m scripts.seed_data
   ```

## Configuration

Create a `.env` file with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/medihelp_db` |
| `SECRET_KEY` | JWT signing key (use strong random string) | `your-256-bit-secret` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |
| `SMTP_HOST` | Email server host | `smtp.gmail.com` |
| `SMTP_PORT` | Email server port | `587` |
| `SMTP_USER` | Email username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | Email password/app password | `your-app-password` |
| `SMTP_FROM` | Sender email address | `noreply@medihelp.com` |
| `PATIENT_WEB_URL` | Patient frontend URL | `http://localhost:3000` |
| `ADMIN_WEB_URL` | Admin frontend URL | `http://localhost:3001` |

## Running the Application

### Development

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Points

- **API**: http://localhost:8000/api/v1
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints Summary

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/admin/auth/login` | Admin login |
| POST | `/api/v1/admin/auth/register` | Register admin |

### Doctors
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/doctors/` | - | List doctors |
| GET | `/api/v1/doctors/{id}` | - | Get doctor |
| POST | `/api/v1/doctors/` | Admin | Create doctor |
| PUT | `/api/v1/doctors/{id}` | Admin | Update doctor |
| DELETE | `/api/v1/doctors/{id}` | Admin | Delete doctor |

### Sessions
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/sessions/search` | - | Search sessions |
| GET | `/api/v1/sessions/{id}` | - | Get session |
| GET | `/api/v1/sessions/{id}/queues` | - | Get queue slots |
| POST | `/api/v1/sessions/` | Admin | Create session |
| PUT | `/api/v1/sessions/{id}` | Admin | Update session |
| POST | `/api/v1/sessions/{id}/start` | Admin | Start session |
| POST | `/api/v1/sessions/{id}/queue` | Admin | Update queue |
| POST | `/api/v1/sessions/{id}/end` | Admin | End session |
| DELETE | `/api/v1/sessions/{id}` | Admin | Delete session |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/bookings/` | Create booking |
| GET | `/api/v1/bookings/{token}` | Track booking |
| GET | `/api/v1/bookings/reference/{ref}` | Get by reference |

## Scripts

```bash
# Create admin interactively
python -m scripts.create_admin

# Seed sample data
python -m scripts.seed_data
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

- Set `SECRET_KEY` to a strong random value
- Configure proper `DATABASE_URL` for production database
- Set up proper SMTP credentials
- Update `PATIENT_WEB_URL` and `ADMIN_WEB_URL` to production URLs
- Consider using environment-specific `.env` files

### Reverse Proxy (Nginx)

```nginx
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## License

MIT License
