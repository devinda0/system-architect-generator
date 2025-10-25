"""
Authentication Middleware

JWT-based authentication for API endpoints.
"""

from datetime import datetime, timedelta
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import logging
import os

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


class TokenData(BaseModel):
    """Token data schema."""
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


class Token(BaseModel):
    """Access token schema."""
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    """Current user schema from JWT."""
    id: str
    username: str
    email: str
    role: str = "user"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode a JWT access token.
    
    Args:
        token: JWT token
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        email: str = payload.get("email")
        
        if user_id is None:
            return None
        
        return TokenData(user_id=user_id, username=username, email=email)
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]
) -> CurrentUser:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP bearer credentials
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = decode_access_token(token)
        
        if token_data is None or token_data.user_id is None:
            raise credentials_exception
        
        # In production, fetch user from database
        # For now, return the token data as CurrentUser
        return CurrentUser(
            id=token_data.user_id,
            username=token_data.username or "user",
            email=token_data.email or "user@example.com",
            role="user"
        )
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise credentials_exception


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme)
) -> Optional[CurrentUser]:
    """
    Get current user from JWT token (optional, no error if missing).
    
    Args:
        token: JWT token from OAuth2 scheme
        
    Returns:
        Current user information or None
    """
    if not token:
        return None
    
    try:
        token_data = decode_access_token(token)
        
        if token_data is None or token_data.user_id is None:
            return None
        
        return CurrentUser(
            id=token_data.user_id,
            username=token_data.username or "user",
            email=token_data.email or "user@example.com",
            role="user"
        )
    except Exception as e:
        logger.warning(f"Error getting optional user: {e}")
        return None


async def get_current_active_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CurrentUser:
    """
    Get current active user (requires authentication).
    
    Args:
        current_user: Current user from JWT
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    # In production, check if user is active in database
    return current_user


# Type aliases for dependencies
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_active_user)]
OptionalUserDep = Annotated[Optional[CurrentUser], Depends(get_current_user_optional)]
