from fastapi import FastAPI
import models
from database import engine
from api import api_router

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(api_router)
