"""API v1 routes"""

from fastapi import APIRouter

from app.api.v1.endpoints import router as endpoints_router

# Create API router
router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include endpoint routers
router.include_router(endpoints_router, tags=["conversion"])

# Routes will be added here in future tasks
