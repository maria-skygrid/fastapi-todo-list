from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
import models 
from models import Todos
from database import engine, SessionLocal

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

@app.get('/')
def index(db: db_dependency):
    return db.query(Todos).all()
    