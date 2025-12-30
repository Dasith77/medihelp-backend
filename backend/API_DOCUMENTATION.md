# MediHelp API Documentation

**Base URL**: `http://localhost:8000/api/v1`

## Authentication

Protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via the login endpoint and expire after 30 minutes (configurable).

---

## Authentication Endpoints

### POST /admin/auth/login

Authenticate admin and receive JWT token.

**Request**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account inactive

---

### POST /admin/auth/register

Register a new admin account.

**Request**
```json
{
  "username": "newadmin",
  "email": "newadmin@example.com",
  "password": "securepass123",
  "full_name": "John Doe"
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "username": "newadmin",
  "email": "newadmin@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

**Errors**
- `400 Bad Request` - Username or email already exists

---

## Doctor Endpoints

### GET /doctors/

List all doctors with optional filtering.

**Query Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `skip` | int | Offset (default: 0) |
| `limit` | int | Max results (default: 100, max: 100) |
| `status` | string | Filter by "active" or "inactive" |

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Dr. Sarah Johnson",
    "specialization": "General Medicine",
    "status": "active",
    "created_at": "2024-01-15T10:00:00"
  }
]
```

---

### GET /doctors/{doctor_id}

Get a specific doctor.

**Response** `200 OK`
```json
{
  "id": 1,
  "name": "Dr. Sarah Johnson",
  "specialization": "General Medicine",
  "status": "active",
  "created_at": "2024-01-15T10:00:00"
}
```

**Errors**
- `404 Not Found` - Doctor not found

---

### POST /doctors/ (Admin)

Create a new doctor.

**Headers**: `Authorization: Bearer <token>`

**Request**
```json
{
  "name": "Dr. Emily Williams",
  "specialization": "Dermatology"
}
```

**Response** `201 Created`
```json
{
  "id": 3,
  "name": "Dr. Emily Williams",
  "specialization": "Dermatology",
  "status": "active",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### PUT /doctors/{doctor_id} (Admin)

Update a doctor.

**Headers**: `Authorization: Bearer <token>`

**Request** (all fields optional)
```json
{
  "name": "Dr. Emily W. Johnson",
  "specialization": "Dermatology & Cosmetics",
  "status": "inactive"
}
```

**Response** `200 OK`
```json
{
  "id": 3,
  "name": "Dr. Emily W. Johnson",
  "specialization": "Dermatology & Cosmetics",
  "status": "inactive",
  "created_at": "2024-01-15T10:30:00"
}
```

---

### DELETE /doctors/{doctor_id} (Admin)

Delete a doctor.

**Headers**: `Authorization: Bearer <token>`

**Response** `204 No Content`

---

## Session Endpoints

### POST /sessions/search

Search for available sessions.

**Request**
```json
{
  "doctor_id": 1,
  "date": "2024-01-20"
}
```

Both fields are optional. Returns sessions with status "scheduled" or "ongoing".

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "doctor_id": 1,
    "date": "2024-01-20",
    "start_time": "09:00:00",
    "end_time": "12:00:00",
    "max_patients": 20,
    "avg_minutes_per_patient": 10,
    "current_queue": 0,
    "status": "scheduled",
    "created_at": "2024-01-15T10:00:00",
    "doctor": {
      "id": 1,
      "name": "Dr. Sarah Johnson",
      "specialization": "General Medicine",
      "status": "active",
      "created_at": "2024-01-15T10:00:00"
    }
  }
]
```

---

### GET /sessions/{session_id}

Get a specific session.

**Response** `200 OK`
```json
{
  "id": 1,
  "doctor_id": 1,
  "date": "2024-01-20",
  "start_time": "09:00:00",
  "end_time": "12:00:00",
  "max_patients": 20,
  "avg_minutes_per_patient": 10,
  "current_queue": 5,
  "status": "ongoing",
  "created_at": "2024-01-15T10:00:00",
  "doctor": { ... }
}
```

---

### GET /sessions/{session_id}/queues

Get queue slots with estimated times.

**Response** `200 OK`
```json
[
  {
    "queue_number": 1,
    "is_booked": true,
    "estimated_time": "09:00:00"
  },
  {
    "queue_number": 2,
    "is_booked": true,
    "estimated_time": "09:10:00"
  },
  {
    "queue_number": 3,
    "is_booked": false,
    "estimated_time": "09:20:00"
  }
]
```

---

### POST /sessions/ (Admin)

Create a new session with auto-generated queue slots.

**Headers**: `Authorization: Bearer <token>`

**Request**
```json
{
  "doctor_id": 1,
  "date": "2024-01-25",
  "start_time": "09:00:00",
  "end_time": "12:00:00",
  "max_patients": 20,
  "avg_minutes_per_patient": 10
}
```

**Response** `201 Created`
```json
{
  "id": 5,
  "doctor_id": 1,
  "date": "2024-01-25",
  "start_time": "09:00:00",
  "end_time": "12:00:00",
  "max_patients": 20,
  "avg_minutes_per_patient": 10,
  "current_queue": 0,
  "status": "scheduled",
  "created_at": "2024-01-15T11:00:00",
  "doctor": { ... }
}
```

**Errors**
- `404 Not Found` - Doctor not found
- `400 Bad Request` - End time before start time

---

### PUT /sessions/{session_id} (Admin)

Update session details.

**Headers**: `Authorization: Bearer <token>`

**Request** (all fields optional)
```json
{
  "max_patients": 25,
  "avg_minutes_per_patient": 15,
  "status": "cancelled"
}
```

---

### POST /sessions/{session_id}/start (Admin)

Start a session. Sets status to "ongoing" and current_queue to 1.

**Headers**: `Authorization: Bearer <token>`

**Response** `200 OK`
```json
{
  "id": 1,
  "status": "ongoing",
  "current_queue": 1,
  ...
}
```

**Errors**
- `400 Bad Request` - Session not in "scheduled" status

---

### POST /sessions/{session_id}/queue (Admin)

Update the current queue number.

**Headers**: `Authorization: Bearer <token>`

**Request - Next patient**
```json
{
  "action": "next"
}
```

**Request - Set specific number**
```json
{
  "action": "set",
  "queue_number": 10
}
```

**Response** `200 OK`
```json
{
  "id": 1,
  "current_queue": 10,
  ...
}
```

**Errors**
- `400 Bad Request` - Session not ongoing
- `400 Bad Request` - Already at last queue number
- `400 Bad Request` - Queue number exceeds max_patients

---

### POST /sessions/{session_id}/end (Admin)

End a session. Sets status to "completed".

**Headers**: `Authorization: Bearer <token>`

**Errors**
- `400 Bad Request` - Session not in "ongoing" status

---

### DELETE /sessions/{session_id} (Admin)

Delete a session and all associated queue slots.

**Headers**: `Authorization: Bearer <token>`

**Response** `204 No Content`

---

## Booking Endpoints

### POST /bookings/

Create a new booking (public endpoint).

**Request**
```json
{
  "email": "patient@example.com",
  "session_id": 1,
  "patients": [
    {
      "name": "John Doe",
      "age": 35,
      "phone": "0771234567",
      "queue_number": 5
    },
    {
      "name": "Jane Doe",
      "age": 32,
      "phone": "0779876543",
      "queue_number": 6
    }
  ]
}
```

**Response** `201 Created`
```json
{
  "id": 1,
  "booking_reference": "BK202401158a3f2c1d",
  "email": "patient@example.com",
  "session_id": 1,
  "queue_numbers": [5, 6],
  "booking_status": "confirmed",
  "secure_token": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T14:30:00",
  "patients": [
    {
      "id": 1,
      "name": "John Doe",
      "age": 35,
      "phone": "0771234567",
      "queue_number": 5
    },
    {
      "id": 2,
      "name": "Jane Doe",
      "age": 32,
      "phone": "0779876543",
      "queue_number": 6
    }
  ],
  "session": { ... }
}
```

**Errors**
- `404 Not Found` - Session not found
- `400 Bad Request` - Session not available (wrong status)
- `400 Bad Request` - Queue number out of range
- `400 Bad Request` - Queue slots already booked
- `400 Bad Request` - Duplicate queue numbers in request

---

### GET /bookings/{secure_token}

Track booking by secure token. Used for patient tracking page.

**Response** `200 OK`
```json
{
  "booking_reference": "BK202401158a3f2c1d",
  "email": "patient@example.com",
  "booking_status": "confirmed",
  "session": {
    "id": 1,
    "current_queue": 3,
    "status": "ongoing",
    ...
  },
  "patients": [
    {
      "id": 1,
      "name": "John Doe",
      "age": 35,
      "phone": "0771234567",
      "queue_number": 5
    }
  ],
  "current_queue": 3
}
```

---

### GET /bookings/reference/{booking_reference}

Get booking by reference number.

**Response** `200 OK`
```json
{
  "id": 1,
  "booking_reference": "BK202401158a3f2c1d",
  "email": "patient@example.com",
  "session_id": 1,
  "queue_numbers": [5, 6],
  "booking_status": "confirmed",
  "secure_token": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T14:30:00",
  "patients": [ ... ],
  "session": { ... }
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `204` | No Content (successful deletion) |
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Invalid/missing token |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource doesn't exist |
| `422` | Validation Error - Invalid request body |

### Validation Error Response

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Data Models

### Session Status Values
- `scheduled` - Not yet started
- `ongoing` - Currently active
- `completed` - Finished
- `cancelled` - Cancelled

### Doctor Status Values
- `active` - Available for sessions
- `inactive` - Not available

### Booking Status Values
- `confirmed` - Active booking
- `cancelled` - Cancelled by user/admin
- `completed` - Appointment completed

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding rate limiting middleware.

## Pagination

List endpoints support pagination via `skip` and `limit` query parameters:

```
GET /api/v1/doctors/?skip=10&limit=20
```
