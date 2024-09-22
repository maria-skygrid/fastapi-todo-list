from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from database import SessionLocal
from starlette import status
from models import Users
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter()

# created with command openssl rand -hex 32
SECRET_KEY = 'de1ee65e2958c601c444e88e675b3a6b9fb9cac6080952f03f59a6ea97214e25'
ALGORITHM = 'HS256'

# encode
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

#decode
oauth_bearer = OAuth2PasswordBearer(tokenUrl='token')
# tokenUrl parameter contains the URL that the client sends to the API app.
# we need this function to verify the token in the API request.


def authenticate_user(username: str, password: str, db):
   user = db.query(Users).filter(Users.username == username).first()
   
   if not user:
      return False
   
   if not bcrypt_context.verify(password, user.hashed_password):
      return False
   
   return user
   

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# we call this function to all API endpoints that need authorization. 
def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
   try: 
      payload = jwt.decode(token, SECRET_KEY, algorithm=[ALGORITHM])
      username: str = payload.get('sub') #sub is our username
      user_id: int = payload.get('id')
      if username is None or user_id is None:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail='Could not validate user')
      return {'username': username, 'id': user_id}
   except JWTError:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail='Could not validate user')
      

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

class Token(BaseModel):
  access_token: str
  token_type: str


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
@router.post('/token', response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail='Could not validate user')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return { 'access_token': token, 'token_type': 'bearer' }
