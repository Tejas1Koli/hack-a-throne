from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthCheck(BaseModel):
    status: str
    version: str = "1.0.0"

@router.get("", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """
    Health check endpoint.
    
    Returns the current status of the API.
    """
    return HealthCheck(status="ok")
