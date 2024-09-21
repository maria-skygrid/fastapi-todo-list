from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from database import SessionLocal
from starlette import status
from models import Users
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def authenticate_user(username: str, password: str, db):
   user = db.query(Users).filter(Users.username == username).first()
   
   if not user:
      return False
   
   if not bcrypt_context.verify(password, user.hashed_password):
      return False
   
   return True
   

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
@router.get('/auth/', status_code=status.HTTP_200_OK)
def index(db: db_dependency):
  return db.query(Users).all()

# CREATE
@router.post('/auth', status_code=status.HTTP_201_CREATED)
def create(db: db_dependency, create_user_request: CreateUserRequest):
  user = Users(
    email=create_user_request.email,
    username=create_user_request.username, 
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    role=create_user_request.role, 
    hashed_password=bcrypt_context.hash(create_user_request.password),
    is_active=True
  )
  db.add(user)
  db.commit()

# LOGIN
@router.post('/token')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
       return 'Authentication failed'
    return 'Succesful Authentication'
