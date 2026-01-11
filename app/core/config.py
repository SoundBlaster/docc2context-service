"""Configuration management using Pydantic Settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # File Upload Configuration
    max_upload_size_mb: int = 100  # Maximum upload size in MB
    max_decompressed_size_mb: int = 500  # Maximum decompressed size in MB

    # Workspace Configuration
    workspace_base_path: str = "/tmp"  # Base path for workspaces
    workspace_prefix: str = "swift-conv"  # Prefix for workspace directories
    workspace_permissions: int = 0o700  # Directory permissions (octal)

    # Subprocess Configuration
    swift_cli_path: str = "docc2context"  # Path to Swift CLI binary
    subprocess_timeout: int = 60  # Default timeout in seconds
    max_subprocess_retries: int = 3  # Maximum retry attempts

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: list[str] = ["*"]  # Default to allow all origins

    # Application Metadata
    app_name: str = "DocC2Context Service"
    app_version: str = "0.1.0"
    app_description: str = "Swift DocC to Markdown Web Converter (MVP)"

    # Security Configuration
    environment: str = "development"  # development, staging, production
    allowed_hosts: list[str] = ["*"]  # Allowed hosts for TrustedHostMiddleware
    rate_limit: int = 100  # Maximum requests per minute per IP

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


# Global settings instance
settings = Settings()
