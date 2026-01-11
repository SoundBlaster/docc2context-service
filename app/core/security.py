"""Security middleware for FastAPI application"""

from fastapi import Request, Response
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers and enforce security policies"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Add security headers to the response"""
        response = await call_next(request)

        # Add Content Security Policy (CSP) header
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # Add X-Frame-Options header to prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Add X-Content-Type-Options header to prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Add X-XSS-Protection header
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Add Referrer-Policy header
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add Strict-Transport-Security header (HSTS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


def get_security_middleware() -> Middleware:
    """Get the security middleware for FastAPI"""
    return Middleware(SecurityMiddleware)
