# Deployment Guide - DocC2Context Service

**Version:** 1.0.0
**Last Updated:** 2026-01-11

## Table of Contents

1. [Overview](#overview)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
8. [Deployment Checklist](#deployment-checklist)
9. [Troubleshooting](#troubleshooting)

## Overview

This guide covers deploying the DocC2Context Service to a production environment. The service is containerized using Docker and can be deployed to any Docker-compatible infrastructure.

### Architecture Overview

- **Runtime**: Python 3.10+ with FastAPI
- **Swift CLI**: Compiled Swift binary for DocC conversion
- **Storage**: Ephemeral workspace storage (no persistent data)
- **Networking**: Single HTTP(S) endpoint on configurable port

## Infrastructure Requirements

### Minimum Requirements

- **CPU**: 2 cores (x86_64 or ARM64)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB minimum for Docker images and temporary workspace
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, or RHEL 8+)
- **Docker**: Version 20.10+ or compatible container runtime
- **Network**: Public or private network access depending on use case

### Recommended Production Setup

- **CPU**: 4+ cores for concurrent requests
- **RAM**: 16GB for handling multiple large archives
- **Disk**: 50GB SSD with automatic cleanup
- **Load Balancer**: Nginx or similar for SSL termination and rate limiting
- **Monitoring**: Prometheus + Grafana or equivalent
- **Logging**: Centralized logging (ELK stack, Splunk, or CloudWatch)

### Storage Considerations

The service uses ephemeral storage in `/tmp/swift-conv-{uuid}/` directories:

- Each conversion requires temporary disk space (up to 5x input file size)
- Workspace cleanup happens automatically after each request
- Orphaned directories are cleaned on startup
- No persistent data storage is required

**Disk Usage Example:**
- 100MB upload → ~500MB temporary workspace (5x expansion limit)
- Multiple concurrent conversions multiply this requirement
- Monitor `/tmp` usage and ensure sufficient free space

## Production Deployment

### Pre-Deployment Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/SoundBlaster/docc2context-service.git
   cd docc2context-service
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy example configuration
   cp .env.example .env

   # Edit configuration for production
   nano .env
   ```

   See [Environment Configuration](#environment-configuration) for details.

3. **Build Docker Image**
   ```bash
   # Build production image
   docker build -t docc2context-service:latest .

   # Tag for registry (optional)
   docker tag docc2context-service:latest your-registry/docc2context-service:v1.0.0
   ```

4. **Push to Registry** (Optional)
   ```bash
   # Login to Docker registry
   docker login your-registry

   # Push image
   docker push your-registry/docc2context-service:v1.0.0
   ```

### Deployment Options

#### Option 1: Docker Compose (Recommended for Single-Server)

1. **Create production docker-compose.yml**
   ```bash
   cp docker-compose.yml docker-compose.prod.yml
   ```

2. **Configure for production**
   ```yaml
   version: '3.8'
   services:
     web:
       image: docc2context-service:latest
       container_name: docc2context-service-prod
       restart: unless-stopped
       ports:
         - "8000:8000"
       env_file:
         - .env
       volumes:
         - /var/log/docc2context:/app/logs
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 40s
   ```

3. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

#### Option 2: Docker Run (Simple Single Container)

```bash
docker run -d \
  --name docc2context-service \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v /var/log/docc2context:/app/logs \
  docc2context-service:latest
```

#### Option 3: Kubernetes Deployment

1. **Create deployment manifest** (`k8s/deployment.yaml`)
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: docc2context-service
     labels:
       app: docc2context-service
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: docc2context-service
     template:
       metadata:
         labels:
           app: docc2context-service
       spec:
         containers:
         - name: docc2context-service
           image: your-registry/docc2context-service:v1.0.0
           ports:
           - containerPort: 8000
           env:
           - name: MAX_FILE_SIZE
             value: "104857600"
           - name: CLI_TIMEOUT
             value: "60"
           resources:
             requests:
               memory: "2Gi"
               cpu: "1000m"
             limits:
               memory: "4Gi"
               cpu: "2000m"
           livenessProbe:
             httpGet:
               path: /api/v1/health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /api/v1/health
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
   ```

2. **Create service manifest** (`k8s/service.yaml`)
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: docc2context-service
   spec:
     selector:
       app: docc2context-service
     ports:
     - protocol: TCP
       port: 80
       targetPort: 8000
     type: LoadBalancer
   ```

3. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

## Docker Deployment

### Building the Production Image

The Dockerfile uses a multi-stage build to optimize image size:

```bash
# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t docc2context-service:latest .

# Verify image size
docker images | grep docc2context-service
```

### Image Optimization

Current image size: ~856MB (optimized with multi-stage build)

To further optimize:
- Use Alpine base images (if compatible with Swift runtime)
- Remove development dependencies
- Compress layers with `docker-slim`

### Container Health Checks

The service includes built-in health checks:

```bash
# Check container health
docker ps
# Look for "healthy" status in the STATUS column

# Manual health check
docker exec docc2context-service curl -f http://localhost:8000/api/v1/health
```

## Environment Configuration

### Required Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False

# File Upload Limits
MAX_FILE_SIZE=104857600  # 100MB in bytes

# Swift CLI Configuration
CLI_TIMEOUT=60  # Timeout in seconds
CLI_PATH=/usr/local/bin/docc2context

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

See [CONFIGURATION.md](CONFIGURATION.md) for complete documentation.

### Security Considerations

**Production Checklist:**
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS with SSL/TLS certificates
- [ ] Configure rate limiting (via Nginx or application)
- [ ] Set appropriate `MAX_FILE_SIZE` limits
- [ ] Enable request logging with sensitive data filtering
- [ ] Use environment variables for all configuration (never hardcode)
- [ ] Regularly update Docker base images for security patches
- [ ] Implement network security groups/firewall rules

## Monitoring and Logging

### Application Logs

The service uses structured JSON logging:

```bash
# View logs
docker logs docc2context-service

# Follow logs in real-time
docker logs -f docc2context-service

# View recent errors
docker logs docc2context-service 2>&1 | grep "ERROR"
```

### Log Format

```json
{
  "timestamp": "2026-01-11T10:30:00.000Z",
  "level": "INFO",
  "message": "File upload received",
  "upload_filename": "archive.zip",
  "workspace_path": "/tmp/swift-conv-abc123",
  "request_id": "xyz789"
}
```

### Health Monitoring

**Endpoint:** `GET /api/v1/health`

Monitor health check endpoint:

```bash
# Basic monitoring script
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/health | jq -r .status)
  if [ "$STATUS" != "ready" ]; then
    echo "Service unhealthy: $STATUS"
    # Send alert
  fi
  sleep 30
done
```

### Metrics to Monitor

1. **Application Metrics:**
   - Request count and rate
   - Response times (p50, p95, p99)
   - Error rates (4xx, 5xx)
   - Conversion success/failure rate

2. **System Metrics:**
   - CPU utilization
   - Memory usage
   - Disk space (especially `/tmp`)
   - Network I/O

3. **Business Metrics:**
   - Files converted per hour/day
   - Average file size
   - Average conversion time

## Backup and Disaster Recovery

### Service Recovery

Since the service is stateless, recovery is straightforward:

1. **Container Failure:**
   ```bash
   # Restart container
   docker restart docc2context-service

   # Or recreate from image
   docker-compose -f docker-compose.prod.yml up -d --force-recreate
   ```

2. **Complete System Failure:**
   - Restore from infrastructure backup
   - Pull Docker image from registry
   - Deploy using saved configuration

### Configuration Backup

Backup these files regularly:
- `.env` (environment configuration)
- `docker-compose.prod.yml` (deployment configuration)
- Custom Nginx configuration (if applicable)

```bash
# Backup configuration
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env docker-compose.prod.yml nginx.conf
```

## Deployment Checklist

### Pre-Deployment

- [ ] Review and test all changes in staging environment
- [ ] Verify Docker image builds successfully
- [ ] Review environment variables for production
- [ ] Ensure sufficient infrastructure resources
- [ ] Set up monitoring and alerting
- [ ] Configure backup procedures
- [ ] Review security settings

### Deployment

- [ ] Build production Docker image
- [ ] Push image to registry (if using)
- [ ] Stop old container/service gracefully
- [ ] Deploy new container/service
- [ ] Verify health check endpoint responds
- [ ] Test file conversion functionality
- [ ] Monitor logs for errors
- [ ] Verify metrics collection

### Post-Deployment

- [ ] Monitor application for 24 hours
- [ ] Check error rates and performance metrics
- [ ] Verify log aggregation working
- [ ] Test disaster recovery procedures
- [ ] Update documentation with any changes
- [ ] Notify stakeholders of deployment completion

## Troubleshooting

### Common Production Issues

#### Container Won't Start

**Symptom:** Container exits immediately or restarts continuously

**Diagnosis:**
```bash
# Check container logs
docker logs docc2context-service

# Check container exit code
docker inspect docc2context-service | jq '.[0].State'
```

**Common Causes:**
- Missing or invalid environment variables
- Port already in use (8000)
- Insufficient memory/resources
- Swift binary missing in image

**Solutions:**
- Verify `.env` file is correct
- Check port availability: `netstat -tulpn | grep 8000`
- Increase Docker memory limit
- Rebuild Docker image

#### High Memory Usage

**Symptom:** Container using excessive memory

**Diagnosis:**
```bash
# Check memory usage
docker stats docc2context-service

# Check for memory leaks
docker exec docc2context-service ps aux | head -10
```

**Solutions:**
- Reduce concurrent request limit
- Decrease `MAX_FILE_SIZE` if needed
- Ensure workspace cleanup is working
- Add memory limits to Docker container
- Restart container periodically (cron job)

#### Slow Conversion Times

**Symptom:** Conversions taking longer than expected

**Diagnosis:**
```bash
# Check CPU usage
docker stats docc2context-service

# Check disk I/O
iostat -x 1
```

**Solutions:**
- Increase CPU allocation
- Use SSD instead of HDD for `/tmp`
- Check for disk space issues
- Optimize Swift CLI parameters
- Consider horizontal scaling

### Emergency Procedures

**Service Unresponsive:**
```bash
# Quick restart
docker restart docc2context-service

# Force stop and start
docker stop -t 30 docc2context-service
docker start docc2context-service
```

**Disk Full:**
```bash
# Clean up orphaned workspaces
rm -rf /tmp/swift-conv-*

# Check Docker disk usage
docker system df

# Clean up Docker if needed
docker system prune -a
```

## Support and Escalation

For production issues:

1. Check application logs first
2. Review this troubleshooting guide
3. Consult the main [README.md](../README.md)
4. Open a GitHub issue with:
   - Error logs
   - Environment details
   - Steps to reproduce

## Version History

- **1.0.0** (2026-01-11): Initial deployment guide
