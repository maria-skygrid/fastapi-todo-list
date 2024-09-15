from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path
import models 
from models import Todos
from database import engine, SessionLocal
from starlette import status
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# only open the DB when we need to make changes to it and then close it. 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

# this db_dependency will be used in every endpoint
db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool    


# INDEX
@app.get('/', status_code=status.HTTP_200_OK)
def index(db: db_dependency):
    return db.query(Todos).all()

# SHOW
@app.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
def show(db: db_dependency, todo_id: int=Path(gt=0)):
    todo = db.get(Todos, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail='Element not')
    return todo

# POST
@app.post('/todo/', status_code=status.HTTP_201_CREATED)
def create(db: db_dependency, todo_request: TodoRequest):
    todo = Todos(**todo_request.model_dump())
    db.add(todo)
    db.commit()
 