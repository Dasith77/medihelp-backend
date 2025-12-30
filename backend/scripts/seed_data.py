"""
Seed database with sample data for development.

Creates:
- Default admin user
- Sample doctors
- Sessions for next 7 days
- Queue slots for each session

Run with: python -m scripts.seed_data
"""

import sys
from datetime import date, time, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.models.models import Admin, Doctor, DoctorSession, QueueSlot


def create_admin(db) -> Admin | None:
    """Create default admin user."""
    existing = db.query(Admin).filter(Admin.username == "admin").first()
    if existing:
        print("  [SKIP] Admin 'admin' already exists")
        return existing

    admin = Admin(
        username="admin",
        email="admin@medihelp.com",
        hashed_password=get_password_hash("admin123"),
        full_name="System Administrator",
    )
    db.add(admin)
    print("  [CREATE] Admin 'admin' (password: admin123)")
    return admin


def create_doctors(db) -> list[Doctor]:
    """Create sample doctors."""
    doctors_data = [
        {"name": "Dr. Sarah Johnson", "specialization": "General Medicine"},
        {"name": "Dr. Michael Chen", "specialization": "Pediatrics"},
        {"name": "Dr. Emily Williams", "specialization": "Dermatology"},
        {"name": "Dr. James Anderson", "specialization": "Orthopedics"},
    ]

    doctors = []
    for data in doctors_data:
        existing = db.query(Doctor).filter(Doctor.name == data["name"]).first()
        if existing:
            print(f"  [SKIP] Doctor '{data['name']}' already exists")
            doctors.append(existing)
            continue

        doctor = Doctor(**data)
        db.add(doctor)
        doctors.append(doctor)
        print(f"  [CREATE] Doctor '{data['name']}' - {data['specialization']}")

    return doctors


def create_sessions(db, doctors: list[Doctor]) -> list[DoctorSession]:
    """Create sessions for next 7 days."""
    sessions = []
    today = date.today()

    # Session time slots
    time_slots = [
        {"start": time(9, 0), "end": time(12, 0), "max_patients": 20},
        {"start": time(14, 0), "end": time(17, 0), "max_patients": 15},
    ]

    for day_offset in range(7):
        session_date = today + timedelta(days=day_offset)

        for doctor in doctors:
            for slot in time_slots:
                # Check if session already exists
                existing = (
                    db.query(DoctorSession)
                    .filter(
                        DoctorSession.doctor_id == doctor.id,
                        DoctorSession.date == session_date,
                        DoctorSession.start_time == slot["start"],
                    )
                    .first()
                )

                if existing:
                    sessions.append(existing)
                    continue

                session = DoctorSession(
                    doctor_id=doctor.id,
                    date=session_date,
                    start_time=slot["start"],
                    end_time=slot["end"],
                    max_patients=slot["max_patients"],
                    avg_minutes_per_patient=10,
                )
                db.add(session)
                sessions.append(session)

    return sessions


def create_queue_slots(db, sessions: list[DoctorSession]) -> int:
    """Create queue slots for each session."""
    created_count = 0

    for session in sessions:
        # Check if slots already exist
        existing_count = (
            db.query(QueueSlot)
            .filter(QueueSlot.session_id == session.id)
            .count()
        )

        if existing_count > 0:
            continue

        # Create queue slots
        for queue_number in range(1, session.max_patients + 1):
            slot = QueueSlot(
                session_id=session.id,
                queue_number=queue_number,
                is_booked=False,
            )
            db.add(slot)
            created_count += 1

    return created_count


def main():
    print("\n" + "=" * 50)
    print("  MediHelp Database Seeder")
    print("=" * 50 + "\n")

    db = SessionLocal()

    try:
        # Create admin
        print("Creating admin user...")
        create_admin(db)
        db.flush()

        # Create doctors
        print("\nCreating doctors...")
        doctors = create_doctors(db)
        db.flush()

        # Create sessions
        print("\nCreating sessions for next 7 days...")
        sessions = create_sessions(db, doctors)
        db.flush()

        # Create queue slots
        print("\nCreating queue slots...")
        slots_created = create_queue_slots(db, sessions)

        # Commit all changes
        db.commit()

        # Summary
        print("\n" + "-" * 50)
        print("Seed Data Summary:")
        print(f"  Doctors:       {len(doctors)}")
        print(f"  Sessions:      {len(sessions)}")
        print(f"  Queue Slots:   {slots_created} created")
        print("-" * 50)
        print("\nDatabase seeded successfully!")
        print("\nDefault admin credentials:")
        print("  Username: admin")
        print("  Password: admin123")

    except Exception as e:
        print(f"\nError seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
