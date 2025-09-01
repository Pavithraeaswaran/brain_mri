from fastapi import APIRouter
from .views import router as mri_router

api_router = APIRouter()
api_router.include_router(mri_router)
