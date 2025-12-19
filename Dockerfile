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

# Clone the docc2context repository
WORKDIR /build
RUN git clone https://github.com/SoundBlaster/docc2context.git

# Build the Swift CLI binary
WORKDIR /build/docc2context
RUN swift build -c release

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
# The binary location depends on the Swift Package Manager output structure
# Typically: .build/release/{executable-name}
# We'll copy the entire .build/release directory and find the binary
COPY --from=swift-builder /build/docc2context/.build/release/docc2context /usr/local/bin/docc2context

# Ensure the binary has execute permissions
RUN chmod +x /usr/local/bin/docc2context

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

