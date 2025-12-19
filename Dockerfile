# Multi-stage Dockerfile for Swift DocC to Markdown Converter Service
# Stage 1: Swift runtime base - extract Swift runtime libraries
FROM swift:5.9-focal AS swift-base

# Install required shared libraries for Swift runtime
RUN apt-get update && \
    apt-get install -y \
    libicu-dev \
    libxml2 \
    libz-dev \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Final stage - Python with Swift runtime support
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

# Note: Swift binary will be added in a later task and should be placed in /usr/local/bin
# or a directory in PATH. For now, we ensure the runtime environment is ready.

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (will be added in later tasks)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Default command (will be overridden in docker-compose or when running)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

