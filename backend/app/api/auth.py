"""
Authentication API Endpoints

REST API endpoints for user authentication and session management.
"""

from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.schemas.user import User, UserCreate, UserUpdate, UserResponse
from app.schemas.mongodb_schemas import UserInDB, UserCreate as UserCreateDB
from app.repositories.user_repository import UserRepository
from app.config.mongodb_config import get_database
from app.middleware.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    CurrentUser,
    CurrentUserDep,
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.exceptions.mongodb_exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


async def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    database = get_database()
    return UserRepository(database)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account"
)
async def register_user(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = await user_repo.find_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        existing_username = await user_repo.find_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        
        # Hash password and create user
        try:
            hashed_password = get_password_hash(user_data.password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
            
        user_create_db = UserCreateDB(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password  # This gets replaced with hashed_password in repository
        )
        
        user_id = await user_repo.create_user(user_create_db, hashed_password)
        
        # Get created user
        created_user = await user_repo.find_by_id(user_id)
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Convert to response format
        user_response = UserResponse(
            id=created_user["_id"],
            username=created_user["username"],
            email=created_user["email"],
            full_name=created_user.get("full_name"),
            is_active=created_user.get("is_active", True),
            created_at=created_user["created_at"].isoformat(),
            updated_at=created_user["updated_at"].isoformat(),
            profile=created_user.get("profile")
        )
        
        logger.info(f"User registered successfully: {user_data.username}")
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=dict,
    summary="Login user",
    description="Authenticate user and return access token"
)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Authenticate user and return access token."""
    try:
        # Find user by username or email
        user = await user_repo.find_by_username(form_data.username)
        if not user:
            user = await user_repo.find_by_email(form_data.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": str(user["_id"]),
            "username": user["username"],
            "email": user["email"]
        }
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        # Update last login
        await user_repo.update_last_login(str(user["_id"]))
        
        # Return user info and tokens
        user_response = UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"].isoformat(),
            updated_at=user["updated_at"].isoformat(),
            profile=user.get("profile")
        )
        
        response = {
            "user": user_response.model_dump(),
            "tokens": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
        
        logger.info(f"User logged in successfully: {user['username']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post(
    "/logout",
    summary="Logout user",
    description="Logout current user (client-side token removal)"
)
async def logout_user(current_user: CurrentUserDep):
    """Logout current user."""
    # In JWT-based auth, logout is typically handled client-side
    # by removing the token. Server-side logout would require
    # token blacklisting or short-lived tokens with refresh mechanism.
    logger.info(f"User logged out: {current_user.username}")
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: CurrentUserDep,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get current user information."""
    try:
        # Get fresh user data from database
        user = await user_repo.find_by_id(current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"].isoformat(),
            updated_at=user["updated_at"].isoformat(),
            profile=user.get("profile")
        )
        
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update current authenticated user information"
)
async def update_current_user(
    user_update: UserUpdate,
    current_user: CurrentUserDep,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update current user information."""
    try:
        # Update user
        success = await user_repo.update_user(current_user.id, user_update)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await user_repo.find_by_id(current_user.id)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = UserResponse(
            id=str(updated_user["_id"]),
            username=updated_user["username"],
            email=updated_user["email"],
            full_name=updated_user.get("full_name"),
            is_active=updated_user.get("is_active", True),
            created_at=updated_user["created_at"].isoformat(),
            updated_at=updated_user["updated_at"].isoformat(),
            profile=updated_user.get("profile")
        )
        
        logger.info(f"User updated successfully: {current_user.username}")
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


# Note: Token refresh is not implemented as it requires refresh token storage
# For a production app, implement refresh tokens with database storage