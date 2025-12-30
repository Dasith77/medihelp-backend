from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.models.models import Admin
from app.schemas.schemas import AdminCreate, AdminLogin, AdminResponse, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    credentials: AdminLogin,
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate admin and return JWT token.

    Args:
        credentials: Username and password
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find admin by username
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if admin is active
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    # Create access token
    access_token = create_access_token(subject=admin.username)

    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def register(
    admin_data: AdminCreate,
    db: Session = Depends(get_db),
) -> Admin:
    """
    Register a new admin account.

    Args:
        admin_data: Admin registration data
        db: Database session

    Returns:
        Created admin details

    Raises:
        HTTPException 400: If username or email already exists
    """
    # Check if username already exists
    existing_username = db.query(Admin).filter(Admin.username == admin_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = db.query(Admin).filter(Admin.email == admin_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new admin
    new_admin = Admin(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=get_password_hash(admin_data.password),
        full_name=admin_data.full_name,
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin
