# Deployment Runbook

**Purpose:** Step-by-step instructions for deploying DocC2Context Service to production.
**Audience:** DevOps/Operations Engineers
**Last Updated:** 2026-01-13

---

## Table of Contents

1. Pre-Deployment Preparation
2. Deployment Steps
3. Post-Deployment Verification
4. Troubleshooting
5. Rollback Procedures

---

## Pre-Deployment Preparation

### 1. Verify Prerequisites

Before starting deployment, ensure:

```bash
# Check Docker is running
docker ps

# Check Docker Compose is installed
docker-compose --version

# Check required tools
which git curl jq

# Verify git repository is clean
git status
```

Expected output: All tools available, no uncommitted changes.

### 2. Verify Deployment Checklist

- [ ] Read and understand DEPLOYMENT_CHECKLIST.md
- [ ] Verify all pre-deployment items are complete
- [ ] Confirm team training is complete
- [ ] Ensure deployment window is scheduled
- [ ] Notify stakeholders of deployment start time

### 3. Prepare Environment

```bash
# Navigate to project directory
cd /path/to/docc2context-service

# Verify .env.production exists
test -f .env.production && echo "✓ .env.production exists" || echo "✗ Missing .env.production"

# Verify docker-compose.production.yml exists
test -f docker-compose.production.yml && echo "✓ docker-compose.production.yml exists" || echo "✗ Missing production override"

# Check current version
git describe --tags

# Create deployment backup
cp .env.production .env.production.backup-$(date +%Y%m%d-%H%M%S)
```

### 4. Final Security Review

```bash
# Verify no secrets in committed code
git log --all --source --full-history -S "password\|secret\|api_key" -- :/

# Verify all tests pass
pytest tests/ -v --tb=short

# Verify code quality
ruff check app/
```

---

## Deployment Steps

### Step 1: Build Production Image (5 min)

**Purpose:** Create optimized Docker image with production settings

```bash
# Build image
docker build -t docc2context-service:prod-$(date +%Y%m%d-%H%M%S) .

# Tag as latest
docker tag docc2context-service:prod-$(date +%Y%m%d-%H%M%S) docc2context-service:latest

# Verify image
docker images | grep docc2context-service
```

**Verify:** Image builds without errors

### Step 2: Save Current State (2 min)

**Purpose:** Document current deployment for rollback

```bash
# Export current container state
docker-compose ps > deployment-state-before-$(date +%s).log

# Document running image
docker inspect $(docker-compose ps -q app) | jq '.[0].Image' > deployment-image-before.txt

# Backup current logs
docker-compose logs app > deployment-logs-before-$(date +%s).log

echo "✓ Current state backed up"
```

### Step 3: Pull Dependencies (3 min)

**Purpose:** Ensure all external services are ready

```bash
# Pull/start dependency images
docker pull redis:7-alpine
docker pull elasticsearch:8.5.0
docker pull logstash:8.5.0
docker pull kibana:8.5.0
docker pull prom/prometheus:latest
docker pull prom/alertmanager:latest

# Verify all images downloaded
docker images | grep -E "redis|elasticsearch|logstash|kibana|prometheus|alertmanager" | wc -l
# Expected: 6 images
```

**Verify:** All images present

### Step 4: Stop Old Containers (2 min)

**Purpose:** Gracefully shut down running containers

```bash
# Get current container state
docker-compose ps

# Stop containers (graceful shutdown)
docker-compose stop -t 30

# Wait for graceful shutdown
sleep 5

# Verify stopped
docker-compose ps
# Expected: All containers Down/Exited
```

**Verify:** All containers stopped

### Step 5: Update Configuration (2 min)

**Purpose:** Switch to production environment variables

```bash
# Verify production config exists
test -f .env.production || (echo "ERROR: .env.production not found" && exit 1)

# Switch to production env
ln -sf .env.production .env

# Verify switch
cat .env | head -5
# Expected: ENVIRONMENT=production
```

**Verify:** .env points to production config

### Step 6: Start New Containers (5 min)

**Purpose:** Launch production services

```bash
# Start with production overrides
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# Wait for services to start
sleep 10

# Check status
docker-compose ps

# Expected output: All containers Up
```

**Verify:** All containers running

### Step 7: Verify Service Health (3 min)

**Purpose:** Confirm application is responding

```bash
# Health check (retry up to 5 times)
for i in {1..5}; do
  echo "Health check attempt $i..."
  curl -s http://localhost:8000/health | jq . && break
  sleep 2
done

# Check logs for errors
docker-compose logs app | grep -i "error\|exception" | head -5

# If no errors, deployment successful
echo "✓ Service health verified"
```

**Verify:** Health endpoint returns `{"status": "ready"}`

---

## Post-Deployment Verification

### Verification Checklist

Execute these verification steps in order:

```bash
# 1. Service Status
echo "=== SERVICE STATUS ==="
docker-compose ps

# 2. Health Endpoint
echo "=== HEALTH ENDPOINT ==="
curl -s http://localhost:8000/health | jq .

# 3. Metrics Endpoint
echo "=== METRICS ==="
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result[] | {job: .labels.job, instance: .labels.instance}'

# 4. Log Status
echo "=== ELK STACK ==="
curl -s http://localhost:9200/_cluster/health | jq .status

# 5. Alert Manager
echo "=== ALERTMANAGER ==="
curl -s http://localhost:9093/api/v1/alerts | jq '.data | length'

# 6. Application Logs
echo "=== APPLICATION LOGS (last 10 lines) ==="
docker-compose logs app | tail -10
```

### Functional Testing

Test basic functionality:

```bash
# Test 1: Upload small file
echo "Test 1: Small file upload..."
# (Create small test ZIP and upload via API)

# Test 2: Check file size limit
echo "Test 2: File size validation..."
# (Verify 100MB limit enforced)

# Test 3: Check error handling
echo "Test 3: Error handling..."
# (Upload invalid file, verify error response)

echo "✓ All functional tests passed"
```

### Monitoring Verification

Verify monitoring systems are working:

```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'
# Expected: All targets UP

# Check Kibana dashboards
curl -s http://localhost:5601/api/saved_objects/dashboard | jq '.saved_objects | length'
# Expected: Dashboards loaded

# Check alert rules loaded
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups | length'
# Expected: Alert groups present

echo "✓ Monitoring systems verified"
```

---

## Troubleshooting

### Container Fails to Start

**Symptom:** `docker-compose up` fails with error

```bash
# Check logs
docker-compose logs app

# Common issues:
# 1. Port already in use
netstat -an | grep 8000
lsof -i :8000

# 2. Environment variable not set
docker-compose config | grep ENVIRONMENT

# 3. Dependencies not ready
docker-compose logs redis elasticsearch

# Solution: Fix issue, then restart
docker-compose restart app
```

### Health Check Fails

**Symptom:** `curl http://localhost:8000/health` returns error

```bash
# Check if container is running
docker ps | grep app

# Check logs for errors
docker-compose logs app | tail -20

# Check if port is listening
netstat -an | grep 8000

# Restart application
docker-compose restart app

# Retry health check
curl http://localhost:8000/health
```

### High Memory Usage

**Symptom:** Memory usage near container limit

```bash
# Check container stats
docker stats --no-stream app

# Check for memory leaks in logs
docker-compose logs app | grep -i "memory"

# Restart container (if safe)
docker-compose restart app

# Monitor for improvement
watch docker stats --no-stream app
```

### Stuck in Upgrade

**Symptom:** Deployment appears to hang

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs app

# If stuck, force restart (may cause brief downtime)
docker-compose kill app
docker-compose rm app
docker-compose up -d app
```

---

## Rollback Procedures

### When to Rollback

Rollback immediately if:
- Health check fails repeatedly
- Error rate spikes (>10% 5xx errors)
- Service crashes
- Data corruption detected
- Security vulnerability discovered

### Rollback Steps

```bash
# 1. Stop current deployment
docker-compose down

# 2. Get previous version from backup
ls -la deployment-image-before.txt
PREVIOUS_VERSION=$(cat deployment-image-before.txt)

# 3. Restart with previous version
# Edit docker-compose.yml to use previous image
# OR manually start previous container

# 4. Verify previous version working
docker-compose ps

# 5. Verify health
curl http://localhost:8000/health

# 6. Notify stakeholders
echo "Rollback completed to previous version: $PREVIOUS_VERSION"
```

### Full Rollback Script

```bash
#!/bin/bash
set -e

echo "Initiating rollback..."

# Stop current
docker-compose down

# Restore environment
cp .env.production.backup-* .env

# Start previous version
docker-compose up -d

# Wait for startup
sleep 10

# Verify
curl http://localhost:8000/health

echo "✓ Rollback complete"
```

---

## Post-Deployment Monitoring

### First 24 Hours

Monitor closely:
- [ ] Check metrics every hour
- [ ] Review error logs
- [ ] Monitor resource usage
- [ ] Verify alerts are working
- [ ] Test incident response procedures

### Baseline Establishment

Record initial metrics:
```bash
# Save baseline metrics
curl -s http://localhost:9090/api/v1/query?query=http_requests_total > baseline-metrics.json
curl -s http://localhost:9200/_stats > baseline-elasticsearch-stats.json

# Note CPU and memory usage
docker stats --no-stream app > baseline-resource-usage.log
```

### Ongoing Monitoring

Continue with:
- [ ] Daily log review
- [ ] Weekly metrics analysis
- [ ] Monthly capacity planning
- [ ] Quarterly security audit

---

## Deployment Complete Checklist

- [ ] All containers running
- [ ] Health checks passing
- [ ] Monitoring systems active
- [ ] Logs flowing to ELK Stack
- [ ] Alerts configured and tested
- [ ] Functional tests passing
- [ ] Performance baseline established
- [ ] Team notified of deployment
- [ ] Documentation updated
- [ ] Deployment recorded in change log

---

## Emergency Contacts

**Deployment Issues:**
- DevOps Lead: ________________________
- Platform Engineer: ________________________
- On-Call Engineer: ________________________

**Escalation:**
- Tech Lead: ________________________
- Engineering Manager: ________________________
- VP Engineering: ________________________

---

**Document Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Task:** 5.8 - Deployment Runbook & Handoff
