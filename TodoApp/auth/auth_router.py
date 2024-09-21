from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from database import SessionLocal
from models import Users
from pydantic import BaseModel, Field

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

db_dependency = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
  email: str
  username: str = Field(min_length=3, max_length=50)
  first_name: str = Field(min_length=3)
  last_name: str = Field(min_length=3)
  password: str
  role: str

# INDEX
@router.get('/auth/')
def get_user():
  return { 'user': 'authenticated' }

# CREATE
@router.post('/auth')
def create(create_user_request: CreateUserRequest):
  user = Users(
    email=create_user_request.email,
    username=create_user_request.username, 
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    role=create_user_request.role, 
    hashed_password=create_user_request.password,
    is_active=True
  )

  return user