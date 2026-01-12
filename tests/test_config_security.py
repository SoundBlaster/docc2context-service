"""Security configuration tests for Task 5.1"""

import os


def test_cors_origins_json_format():
    """Test CORS_ORIGINS with JSON array format"""
    os.environ["CORS_ORIGINS"] = '["https://yourdomain.com"]'
    os.environ["ENVIRONMENT"] = "development"

    from app.core.config import Settings

    settings = Settings()
    assert settings.cors_origins == ["https://yourdomain.com"]


def test_swagger_enabled_configurable():
    """Test SWAGGER_ENABLED is configurable"""
    os.environ["SWAGGER_ENABLED"] = "false"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["CORS_ORIGINS"] = '["https://test.com"]'

    from app.core.config import Settings

    settings = Settings()
    assert settings.swagger_enabled is False


def test_env_production_file_exists():
    """Test that .env.production example exists"""
    assert os.path.exists(".env.production"), ".env.production should exist"

    with open(".env.production") as f:
        content = f.read()
        assert "SWAGGER_ENABLED=false" in content
        assert "CORS_ORIGINS" in content
        assert "yourdomain.com" in content


def test_main_py_uses_swagger_setting():
    """Test that main.py uses swagger_enabled setting"""
    # In development with default settings, swagger_enabled should be True
    # So docs_url should be set
    # We can't easily test the FastAPI app directly without starting it,
    # but we can verify the config is being used
    from app.core.config import settings
    from app.main import app

    if settings.swagger_enabled:
        # Swagger should be available at /docs
        assert app.openapi_url is not None or app.openapi_url == "/openapi.json"
    else:
        # Swagger should be disabled
        assert app.openapi_url is None and app.docs_url is None and app.redoc_url is None
