from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()

# In-memory storage for simplicity
users_db = []
user_id_counter = 1

@router.post("/users", response_model=User, summary="Create a new user")
async def create_user(user: UserCreate):
    global user_id_counter
    new_user = User(id=user_id_counter, username=user.username, email=user.email)
    users_db.append(new_user)
    user_id_counter += 1
    return new_user

@router.get("/users", response_model=List[User], summary="Get all users")
async def get_users():
    return users_db

@router.get("/users/{user_id}", response_model=User, summary="Get a user by ID")
async def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{user_id}", response_model=User, summary="Update a user")
async def update_user(user_id: int, user_update: UserUpdate):
    for user in users_db:
        if user.id == user_id:
            if user_update.username is not None:
                user.username = user_update.username
            if user_update.email is not None:
                user.email = user_update.email
            return user
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/users/{user_id}", summary="Delete a user")
async def delete_user(user_id: int):
    for i, user in enumerate(users_db):
        if user.id == user_id:
            del users_db[i]
            return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
