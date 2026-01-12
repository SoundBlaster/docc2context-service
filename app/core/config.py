"""Configuration management using Pydantic Settings"""

import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # File Upload Configuration
    max_upload_size_mb: int = 100  # Maximum upload size in MB
    max_decompressed_size_mb: int = 500  # Maximum decompressed size in MB
    max_zip_files: int = 5000  # Maximum files in a ZIP archive
    max_zip_depth: int = 10  # Maximum directory depth in ZIP

    # Workspace Configuration
    workspace_base_path: str = "/tmp"  # Base path for workspaces
    workspace_prefix: str = "swift-conv"  # Prefix for workspace directories
    workspace_permissions: int = 0o700  # Directory permissions (octal)
    workspace_max_age_seconds: int = 3600  # Maximum age for workspace cleanup (1 hour)

    # Subprocess Configuration
    swift_cli_path: str = "docc2context"  # Path to Swift CLI binary
    subprocess_timeout: int = 60  # Default timeout in seconds
    max_subprocess_retries: int = 3  # Maximum retry attempts
    subprocess_memory_limit_mb: int = 1024  # Memory limit for subprocess (1GB)

    # Logging
    log_level: str = "INFO"

    # Security Configuration
    environment: str = "development"  # development, staging, production
    allowed_hosts: list[str] = ["*"]  # Allowed hosts for TrustedHostMiddleware
    rate_limit: int = 100  # Maximum requests per minute per IP

    # Swagger/Documentation (Task 5.1)
    swagger_enabled: bool = True  # Enable Swagger docs (default True for development)

    # CORS Configuration (Task 5.1)
    cors_origins: list[str] = ["*"]  # Default to allow all origins in development

    # Application Metadata
    app_name: str = "DocC2Context Service"
    app_version: str = "0.1.0"
    app_description: str = "Swift DocC to Markdown Web Converter (MVP)"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        json_schema_extra={"cors_origins": "Can be JSON array or comma-separated string"},
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON array or comma-separated string"""
        if isinstance(v, list):
            return v

        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):  # JSON array format
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON for CORS_ORIGINS: {v}")
            else:  # Comma-separated format
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("swagger_enabled", "cors_origins", mode="after")
    @classmethod
    def validate_production_security(cls, v, info):
        """Validate security settings for production environment"""
        # Only validate when we have all context
        if info.field_name == "cors_origins":
            environment = info.data.get("environment", "development")
            cors_origins = v
            if environment == "production":
                if "*" in cors_origins:
                    raise ValueError(
                        'CORS wildcard ["*"] is not allowed in production. '
                        'Set CORS_ORIGINS to specific allowed origins (e.g., ["https://yourdomain.com"]).'
                    )
            return v

        if info.field_name == "swagger_enabled":
            environment = info.data.get("environment", "development")
            swagger_enabled = v
            if environment == "production" and swagger_enabled:
                raise ValueError(
                    "SWAGGER_ENABLED must be False in production. Set SWAGGER_ENABLED=false."
                )
            return v

        return v


# Global settings instance (created on first import)
try:
    settings = Settings()
except Exception as e:
    # If settings creation fails, provide a helpful error message
    import sys

    print(f"ERROR: Failed to load settings: {e}", file=sys.stderr)
    # Create a dummy settings object so imports don't crash completely
    # This allows testing and debugging
    settings = None
