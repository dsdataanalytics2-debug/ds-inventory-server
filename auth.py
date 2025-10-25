from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Password hashing - using pbkdf2_sha256 to avoid bcrypt issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Token scheme
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user credentials"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: list):
    """Decorator to require specific roles"""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Permission helpers
def can_add_edit(user: models.User) -> bool:
    """Check if user can add or edit"""
    return user.role.value in ["superadmin", "admin", "editor"]

def can_delete(user: models.User) -> bool:
    """Check if user can delete"""
    return user.role.value in ["superadmin", "admin"]

def can_view(user: models.User) -> bool:
    """Check if user can view (all users can view)"""
    return True

def can_manage_users(user: models.User) -> bool:
    """Check if user can manage other users (superadmin and admin)"""
    return user.role.value in ["superadmin", "admin"]

def can_create_all_roles(user: models.User) -> bool:
    """Check if user can create all roles including superadmin"""
    return user.role.value == "superadmin"

def create_superadmin(db: Session):
    """Create default superadmin user if none exists"""
    # Check by username first (more reliable)
    existing_superadmin = db.query(models.User).filter(
        models.User.username == "superadmin"
    ).first()
    
    if not existing_superadmin:
        superadmin_user = models.User(
            username="superadmin",
            password_hash=get_password_hash("admin123"),
            role=models.UserRole.superadmin
        )
        db.add(superadmin_user)
        db.commit()
        print("Created default superadmin user: username='superadmin', password='admin123'")
    else:
        print("Superadmin user already exists")
