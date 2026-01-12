"""FastAPI application entry point"""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.v1.endpoints import router as endpoints_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.metrics import request_count, request_duration
from app.core.security import SecurityMiddleware

# Setup logging
setup_logging()

# Create FastAPI app with conditional Swagger/docs (Task 5.1)
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs" if settings.swagger_enabled else None,
    redoc_url="/redoc" if settings.swagger_enabled else None,
    openapi_url="/openapi.json" if settings.swagger_enabled else None,
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add HTTPS redirect middleware (for production)
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

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
    return {"status": "healthy", "message": "DocC2Context Service is running"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (Task 5.2)"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track HTTP request metrics (Task 5.2)"""
    # Skip metrics endpoint itself to avoid recursion
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method
    path = request.url.path
    start = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start

        # Record metrics
        request_count.labels(method=method, endpoint=path, status=response.status_code).inc()
        request_duration.labels(method=method, endpoint=path).observe(duration)

        return response
    except Exception as exc:
        # Record error
        request_count.labels(method=method, endpoint=path, status=500).inc()
        duration = time.time() - start
        request_duration.labels(method=method, endpoint=path).observe(duration)
        raise


@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Request timeout middleware"""
    try:
        # Set a timeout for the request (e.g., 30 seconds)
        import asyncio

        response = await asyncio.wait_for(call_next(request), timeout=30.0)
        return response
    except asyncio.TimeoutError:
        from fastapi import HTTPException

        raise HTTPException(status_code=408, detail="Request timeout")


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Application starting up", extra={"app_version": settings.app_version})
    # Initialize rate limiter
    from fastapi_limiter import FastAPILimiter

    try:
        from redis.asyncio import Redis

        redis = await Redis(host="localhost", port=6379)
        await FastAPILimiter.init(redis)
        logger.info("Rate limiter initialized with Redis")
    except Exception as e:
        logger.warning(f"Failed to initialize rate limiter: {str(e)}")
        # Skip rate limiter initialization if Redis is not available
        pass


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger = get_logger(__name__)
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=True)
