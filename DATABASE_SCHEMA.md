# MediHelp Database Schema

## Overview
This document describes all database tables and their relationships for the MediHelp medical appointment queue booking system.

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────────┐
│   admins    │       │      doctors        │
└─────────────┘       └──────────┬──────────┘
                                 │
                                 │ 1:N
                                 ▼
                      ┌─────────────────────┐
                      │  doctor_schedules   │
                      └─────────────────────┘

                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         │ 1:N                   │ 1:N                   │
         ▼                       ▼                       │
┌─────────────────┐    ┌─────────────────┐              │
│    sessions     │───▶│   queue_slots   │              │
└────────┬────────┘    └────────┬────────┘              │
         │                      │                       │
         │ 1:N                  │ 1:1                   │
         ▼                      ▼                       │
┌─────────────────┐    ┌─────────────────┐              │
│    bookings     │───▶│  booking_items  │              │
└────────┬────────┘    └─────────────────┘              │
         │                                              │
         │ 1:N                                          │
         ▼                                              │
┌─────────────────┐                                     │
│  notifications  │◀────────────────────────────────────┘
└─────────────────┘
```

---

## Tables

### 1. admins
Admin users for system authentication.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Admin email |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| name | VARCHAR(100) | NOT NULL | Admin name |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

```sql
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2. doctors
Doctor profiles and information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Doctor's full name |
| specialization | VARCHAR(100) | NOT NULL | Medical specialization |
| image_url | VARCHAR(500) | NULL | Profile image URL |
| is_available | BOOLEAN | DEFAULT TRUE | Availability status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

```sql
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    image_url VARCHAR(500),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3. doctor_schedules
Weekly recurring schedules for doctors.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| doctor_id | UUID | FOREIGN KEY → doctors(id), NOT NULL | Reference to doctor |
| day_of_week | INTEGER | NOT NULL, CHECK (0-6) | Day (0=Sunday, 6=Saturday) |
| start_time | TIME | NOT NULL | Schedule start time |
| end_time | TIME | NOT NULL | Schedule end time |
| max_patients | INTEGER | DEFAULT 20 | Maximum patients per session |
| is_active | BOOLEAN | DEFAULT TRUE | Schedule active status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

```sql
CREATE TABLE doctor_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_patients INTEGER DEFAULT 20,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, day_of_week)
);
```

---

### 4. sessions
Doctor appointment sessions for specific dates.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| doctor_id | UUID | FOREIGN KEY → doctors(id), NOT NULL | Reference to doctor |
| date | DATE | NOT NULL | Session date |
| start_time | TIME | NOT NULL | Session start time |
| end_time | TIME | NOT NULL | Session end time |
| max_patients | INTEGER | NOT NULL | Maximum patient capacity |
| booked_count | INTEGER | DEFAULT 0 | Number of booked slots |
| current_queue_number | INTEGER | DEFAULT 0 | Current serving queue number |
| status | VARCHAR(20) | DEFAULT 'available' | available, few-slots, fully-booked |
| is_started | BOOLEAN | DEFAULT FALSE | Session started flag |
| is_ended | BOOLEAN | DEFAULT FALSE | Session ended flag |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_patients INTEGER NOT NULL,
    booked_count INTEGER DEFAULT 0,
    current_queue_number INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'few-slots', 'fully-booked')),
    is_started BOOLEAN DEFAULT FALSE,
    is_ended BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, date, start_time)
);
```

---

### 5. queue_slots
Individual queue slots within a session.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| session_id | UUID | FOREIGN KEY → sessions(id), NOT NULL | Reference to session |
| queue_number | INTEGER | NOT NULL | Queue position number |
| approximate_time | TIME | NOT NULL | Estimated appointment time |
| is_booked | BOOLEAN | DEFAULT FALSE | Booking status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

```sql
CREATE TABLE queue_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    queue_number INTEGER NOT NULL,
    approximate_time TIME NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, queue_number)
);
```

---

### 6. bookings
Main booking records (can contain multiple patients/items).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| reference_number | VARCHAR(20) | UNIQUE, NOT NULL | Booking reference (BK-XXXXXXXX) |
| session_id | UUID | FOREIGN KEY → sessions(id), NOT NULL | Reference to session |
| doctor_id | UUID | FOREIGN KEY → doctors(id), NOT NULL | Reference to doctor |
| date | DATE | NOT NULL | Booking date |
| status | VARCHAR(20) | DEFAULT 'confirmed' | confirmed, cancelled, completed |
| payment_status | VARCHAR(20) | DEFAULT 'pending' | pending, paid |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_number VARCHAR(20) UNIQUE NOT NULL,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE RESTRICT,
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE RESTRICT,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled', 'completed')),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_reference ON bookings(reference_number);
CREATE INDEX idx_bookings_date ON bookings(date);
CREATE INDEX idx_bookings_session ON bookings(session_id);
```

---

### 7. booking_items
Individual patient entries within a booking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| booking_id | UUID | FOREIGN KEY → bookings(id), NOT NULL | Reference to booking |
| slot_id | UUID | FOREIGN KEY → queue_slots(id), NOT NULL | Reference to queue slot |
| queue_number | INTEGER | NOT NULL | Queue position |
| approximate_time | TIME | NOT NULL | Estimated time |
| patient_name | VARCHAR(100) | NOT NULL | Patient's full name |
| patient_phone | VARCHAR(20) | NOT NULL | Patient's phone number |
| patient_email | VARCHAR(255) | NULL | Patient's email |
| patient_age | INTEGER | NULL | Patient's age |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

```sql
CREATE TABLE booking_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    slot_id UUID NOT NULL REFERENCES queue_slots(id) ON DELETE RESTRICT,
    queue_number INTEGER NOT NULL,
    approximate_time TIME NOT NULL,
    patient_name VARCHAR(100) NOT NULL,
    patient_phone VARCHAR(20) NOT NULL,
    patient_email VARCHAR(255),
    patient_age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(slot_id)
);

CREATE INDEX idx_booking_items_booking ON booking_items(booking_id);
```

---

### 8. notifications
Notification history and logs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| session_id | UUID | FOREIGN KEY → sessions(id), NULL | Related session |
| doctor_id | UUID | FOREIGN KEY → doctors(id), NULL | Related doctor |
| type | VARCHAR(50) | NOT NULL | doctor_arrived, queue_update, session_started, custom |
| title | VARCHAR(200) | NOT NULL | Notification title |
| message | TEXT | NOT NULL | Notification content |
| status | VARCHAR(20) | DEFAULT 'sent' | sent, pending, failed |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    doctor_id UUID REFERENCES doctors(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'pending', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_session ON notifications(session_id);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);
```

---

## Relationships Summary

| Parent Table | Child Table | Relationship | ON DELETE |
|--------------|-------------|--------------|-----------|
| doctors | doctor_schedules | 1:N | CASCADE |
| doctors | sessions | 1:N | CASCADE |
| doctors | bookings | 1:N | RESTRICT |
| doctors | notifications | 1:N | SET NULL |
| sessions | queue_slots | 1:N | CASCADE |
| sessions | bookings | 1:N | RESTRICT |
| sessions | notifications | 1:N | SET NULL |
| bookings | booking_items | 1:N | CASCADE |
| queue_slots | booking_items | 1:1 | RESTRICT |

---

## Required PostgreSQL Extensions

```sql
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## Initial Setup Script

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create all tables in order (respecting foreign key dependencies)
-- 1. admins (no dependencies)
-- 2. doctors (no dependencies)
-- 3. doctor_schedules (depends on doctors)
-- 4. sessions (depends on doctors)
-- 5. queue_slots (depends on sessions)
-- 6. bookings (depends on sessions, doctors)
-- 7. booking_items (depends on bookings, queue_slots)
-- 8. notifications (depends on sessions, doctors)

-- Insert default admin user (password: admin123)
INSERT INTO admins (email, password_hash, name) VALUES
('admin@medihelp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qzGk6u7qzq1Hqe', 'Admin User');
```

---

## Notes

1. **UUID Primary Keys**: All tables use UUID for primary keys for better security and distributed systems support.

2. **Soft Delete**: Consider adding `deleted_at` column for soft deletes if needed in the future.

3. **Timestamps**: All tables include `created_at`, and mutable tables include `updated_at`.

4. **Indexes**: Key indexes are created for frequently queried columns (reference_number, date, session_id).

5. **Constraints**: Check constraints ensure data integrity for status fields and day_of_week values.

6. **Cascade Rules**:
   - CASCADE: Child records deleted when parent is deleted (schedules, slots, booking_items)
   - RESTRICT: Prevent deletion if child records exist (bookings reference doctors/sessions)
   - SET NULL: Set to NULL if parent is deleted (notifications)
