"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1.endpoints import router as endpoints_router

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(endpoints_router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"))

# Root endpoint to serve frontend
@app.get("/")
async def root():
    """Serve the frontend application"""
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "message": "DocC2Context Service is running"
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Application starting up", extra={"app_version": settings.app_version})


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger = get_logger(__name__)
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
