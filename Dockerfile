# Multi-stage Dockerfile for Swift DocC to Markdown Converter Service
# Stage 1: Swift runtime base - extract Swift runtime libraries
FROM swift:6.0-focal AS swift-base

# Install required shared libraries for Swift runtime
RUN apt-get update && \
    apt-get install -y \
    libicu-dev \
    libxml2 \
    libz-dev \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Build Swift CLI binary from source
FROM swift:6.0-focal AS swift-builder

# Install git and required build dependencies
RUN apt-get update && \
    apt-get install -y \
    git \
    libicu-dev \
    libxml2 \
    libz-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and build docc2context
WORKDIR /build
RUN git clone https://github.com/SoundBlaster/docc2context.git && \
    cd docc2context && \
    swift build -c release

# Stage 3: Final stage - Python with Swift runtime support
FROM python:3.10-slim

# Install runtime dependencies needed for Swift binaries
# Note: libicu-dev pulls in runtime libraries as dependencies
RUN apt-get update && \
    apt-get install -y \
    --no-install-recommends \
    libicu-dev \
    libxml2 \
    zlib1g \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Swift runtime libraries from swift-base
COPY --from=swift-base /usr/lib/swift /usr/lib/swift

# Set up Swift environment variables for runtime library path
ENV LD_LIBRARY_PATH=/usr/lib/swift/linux

# Copy the compiled Swift CLI binary from the builder stage
COPY --from=swift-builder /build/docc2context/.build/release/docc2context /usr/local/bin/docc2context

# Ensure the binary has execute permissions
RUN chmod +x /usr/local/bin/docc2context

# Create non-root user for running the application
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories with proper permissions
RUN mkdir -p /tmp/workspaces && \
    chown -R appuser:appuser /app /tmp/workspaces

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Add healthcheck using Python (guaranteed to be available)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Security: Set resource limits and security options
# These will be enforced by Docker runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Default command (will be overridden in docker-compose or when running)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

