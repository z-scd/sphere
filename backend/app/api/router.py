from fastapi import APIRouter
from . import notebook, class_9_10

api_router = APIRouter(prefix='/api/v1')
# Notebook Services
api_router.include_router(notebook.router, prefix='/notebook', tags=['notebook'])
# Class 9-10
api_router.include_router(class_9_10.router, prefix='/class-9-10', tags=['class-9-10'])
