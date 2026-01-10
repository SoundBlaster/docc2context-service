"""FastAPI application entry point"""

import uuid
from contextvars import copy_context
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import get_logger, set_request_id, setup_logging
from app.api.v1 import router as v1_router

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and set request ID for each request"""

    async def dispatch(self, request: Request, call_next: Callable):
        # Generate request ID
        request_id = set_request_id()
        
        # Add request ID to request state for access in routes
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # TODO: Add binary detection in Task 1.8
    return {
        "status": "ready",
        "binary_detected": True  # Placeholder
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Application starting up", extra={"app_version": settings.app_version})


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )





