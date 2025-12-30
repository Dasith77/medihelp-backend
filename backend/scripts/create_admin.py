"""
Interactive script to create admin users.

Run with: python -m scripts.create_admin
"""

import re
import sys
from getpass import getpass
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.models.models import Admin


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username (3-50 chars, alphanumeric and underscores)."""
    pattern = r"^[a-zA-Z0-9_]{3,50}$"
    return bool(re.match(pattern, username))


def get_input(prompt: str, validator=None, error_msg: str = "Invalid input") -> str:
    """Get validated input from user."""
    while True:
        value = input(prompt).strip()
        if not value:
            print("This field is required.")
            continue
        if validator and not validator(value):
            print(error_msg)
            continue
        return value


def get_password() -> str:
    """Get and confirm password from user."""
    while True:
        password = getpass("Password (min 6 chars): ")
        if len(password) < 6:
            print("Password must be at least 6 characters.")
            continue

        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.")
            continue

        return password


def main():
    print("\n" + "=" * 50)
    print("  MediHelp Admin User Creation")
    print("=" * 50 + "\n")

    db = SessionLocal()

    try:
        # Get username
        username = get_input(
            "Username (3-50 chars, alphanumeric): ",
            validate_username,
            "Invalid username. Use 3-50 alphanumeric characters or underscores.",
        )

        # Check if username exists
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            print(f"\nError: Username '{username}' already exists.")
            sys.exit(1)

        # Get email
        email = get_input(
            "Email: ",
            validate_email,
            "Invalid email format.",
        )

        # Check if email exists
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"\nError: Email '{email}' already registered.")
            sys.exit(1)

        # Get password
        password = get_password()

        # Get full name (optional)
        full_name = input("Full name (optional, press Enter to skip): ").strip() or None

        # Confirm creation
        print("\n" + "-" * 50)
        print("Admin Details:")
        print(f"  Username:  {username}")
        print(f"  Email:     {email}")
        print(f"  Full Name: {full_name or '(not set)'}")
        print("-" * 50)

        confirm = input("\nCreate this admin? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            sys.exit(0)

        # Create admin
        admin = Admin(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
        )

        db.add(admin)
        db.commit()

        print(f"\nAdmin '{username}' created successfully!")

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError creating admin: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
