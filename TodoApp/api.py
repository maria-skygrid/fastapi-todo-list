from fastapi import APIRouter
from auth import router as auth_routes
from todo import router as todo_routes

api_router = APIRouter()

def todo_router():
  router = APIRouter(
    tags=["todo"]
  )
  router.include_router(todo_routes)
  return router

def auth_router():
  router = APIRouter(
    tags=["auth"], 
  )
  router.include_router(auth_routes)
  return router


api_router.include_router(todo_router())
api_router.include_router(auth_router())