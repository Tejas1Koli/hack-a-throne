from fastapi import APIRouter
from app.api.endpoints import analyze, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
