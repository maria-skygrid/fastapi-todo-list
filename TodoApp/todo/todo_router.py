from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
import models 
from models import Todos
from database import engine, SessionLocal
from starlette import status
from pydantic import BaseModel, Field

router = APIRouter()

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
@router.get('/', status_code=status.HTTP_200_OK)
def index(db: db_dependency):
    return db.query(Todos).all()

# SHOW
@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
def show(db: db_dependency, todo_id: int=Path(gt=0)):
    todo = db.get(Todos, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail='Element not')
    return todo

# POST
@router.post('/todo/', status_code=status.HTTP_201_CREATED)
def create(db: db_dependency, todo_request: TodoRequest):
    todo = Todos(**todo_request.model_dump())
    db.add(todo)
    db.commit()

# PUT
@router.put('/todo/{todo_id}/edit', status_code=status.HTTP_204_NO_CONTENT)
def update(
    db: db_dependency, 
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    todo = todo_request.model_dump(exclude_unset=True)
    updated_db = db.query(Todos).filter(Todos.id == todo_id).update(todo)
    if not updated_db:
        raise HTTPException(status_code=404, detail='Element not found')
    db.commit()

# DELETE
@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(
    db: db_dependency, 
    todo_id: int = Path(gt=0)
):
    todo = db.get(Todos, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Element not found")
    db.delete(todo)
    db.commit()