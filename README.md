# MediHelp Backend

FastAPI backend for the MediHelp healthcare appointment booking system.

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy 2.0.25
- **Authentication**: JWT (python-jose) with password hashing (passlib)
- **Email**: FastAPI-mail
- **Validation**: Pydantic
- **Environment**: python-dotenv
- **Language**: Python 3.8+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and setup
│   ├── models/              # SQLAlchemy database models
│   │   ├── admin.py
│   │   ├── doctor.py
│   │   ├── doctor_schedule.py
│   │   ├── booking.py
│   │   ├── booking_item.py
│   │   ├── session.py
│   │   ├── queue_slot.py
│   │   └── notification.py
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   ├── bookings.py
│   │   ├── sessions.py
│   │   ├── slots.py
│   │   ├── queue.py
│   │   ├── dashboard.py
│   │   └── notifications.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── doctor.py
│   │   ├── booking.py
│   │   ├── session.py
│   │   ├── queue_slot.py
│   │   ├── queue.py
│   │   ├── dashboard.py
│   │   └── notification.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── doctor_service.py
│   │   ├── booking_service.py
│   │   ├── session_service.py
│   │   ├── queue_service.py
│   │   ├── notification_service.py
│   │   └── email_service.py
│   ├── utils/               # Utility functions
│   │   ├── security.py
│   │   └── helpers.py
│   └── templates/
│       └── email/           # Email templates
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Environment variables (create this)
└── DATABASE_SCHEMA.md      # Database schema documentation
```

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

### 2. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
```

Required environment variables in `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/medihelp

# JWT Secret Key (generate a secure random key)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (optional for development)
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=noreply@medihelp.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=MediHelp
```

### 5. Set Up Database

```bash
# Create PostgreSQL database
createdb medihelp

# The application will create tables automatically on first run
# using SQLAlchemy models
```

### 6. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/login` - Admin login
- `POST /api/auth/register` - Admin registration

### Doctors
- `GET /api/doctors` - List all doctors
- `GET /api/doctors/{id}` - Get doctor details
- `POST /api/doctors` - Create doctor (admin)
- `PUT /api/doctors/{id}` - Update doctor (admin)
- `DELETE /api/doctors/{id}` - Delete doctor (admin)

### Sessions
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `POST /api/sessions` - Create session (admin)
- `PUT /api/sessions/{id}` - Update session (admin)
- `DELETE /api/sessions/{id}` - Delete session (admin)

### Bookings
- `GET /api/bookings` - List all bookings
- `GET /api/bookings/{id}` - Get booking details
- `POST /api/bookings` - Create booking
- `PUT /api/bookings/{id}` - Update booking (admin)
- `DELETE /api/bookings/{id}` - Cancel booking

### Queue Management
- `GET /api/queue` - Get queue status
- `POST /api/queue/next` - Call next patient (admin)
- `PUT /api/queue/{id}/status` - Update queue status (admin)

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics (admin)

### Notifications
- `GET /api/notifications` - List notifications (admin)
- `POST /api/notifications` - Create notification (admin)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style

```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Database Schema

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for detailed database structure and relationships.

## Dependencies

Key dependencies (see `requirements.txt` for complete list):

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
fastapi-mail==1.4.1
```

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Verify DATABASE_URL in `.env` is correct
- Check PostgreSQL user permissions

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Email Not Sending

- Verify email credentials in `.env`
- For Gmail, enable "App Passwords"
- Check firewall/network settings

## License

All rights reserved.
