from fastapi import APIRouter
from app.config.mongodb_config import check_mongodb_health

router = APIRouter()

@router.get("/health", summary="Health check")
async def health():
    """
    Health check endpoint.
    
    Returns:
        Health status including database connection status
    """
    mongo_health = await check_mongodb_health()
    
    return {
        "status": "ok",
        "database": mongo_health
    }