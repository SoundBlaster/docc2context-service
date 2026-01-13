# Rollback Runbook

**Purpose:** Emergency procedures to revert to previous production version
**Audience:** DevOps/Operations Engineers
**Severity:** Critical
**Last Updated:** 2026-01-13

---

## Quick Rollback (< 2 minutes)

If immediate rollback is critical:

```bash
# 1. Stop everything
docker-compose down

# 2. Switch back to previous env
cp .env.production.backup-<timestamp> .env

# 3. Restart previous version
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health

# 5. Alert team
# "Rollback to previous version completed"
```

---

## Full Rollback Procedure

### Phase 1: Decision & Preparation (5 min)

#### Rollback Triggers

Stop deployment and rollback if **any** of these occur:

- Critical security vulnerability discovered
- Data corruption detected or suspected
- Service unavailable (health checks failing after 5 retries)
- Error rate > 10% (5xx errors)
- Memory usage > 90% of limit, sustained > 2 min
- CPU usage > 95%, sustained > 2 min
- More than 3 consecutive request timeouts
- Data loss or integrity issues
- Unrecoverable service crashes
- SECURITY_CHECKLIST.md items failing

#### Escalation Sequence

```
1. Current shift engineer detects issue
   ↓
2. Notifies on-call DevOps lead
   ↓
3. DevOps lead authorizes rollback
   ↓
4. Execute rollback procedure (this runbook)
   ↓
5. Verify service restored
   ↓
6. Post-incident review
```

#### Pre-Rollback Checklist

- [ ] Issue confirmed and verified
- [ ] Rollback authorized by lead
- [ ] Previous version verified in backup
- [ ] Communication plan ready
- [ ] Stakeholders notified
- [ ] Monitoring team on standby

### Phase 2: Stop Current Deployment (2 min)

#### 1. Stop Service Gracefully

```bash
# Get current container status
docker-compose ps

# Graceful stop (30 second timeout)
docker-compose stop -t 30

# Wait for graceful shutdown
sleep 5

# Verify all stopped
docker-compose ps
# Expected: All containers should show "Exited" or "Down"
```

#### 2. Preserve Current State (for debugging)

```bash
# Save current logs
docker-compose logs app > rollback-logs-failed-version-$(date +%s).log

# Save container state
docker-compose ps > rollback-state-before-rollback.log

# Export failed container config
docker inspect $(docker-compose ps -q app 2>/dev/null) > rollback-failed-container.json 2>/dev/null || true

# Save metrics snapshot
curl -s http://localhost:9090/api/v1/query?query=up > rollback-metrics-failed.json 2>/dev/null || true

echo "✓ Current state preserved for debugging"
```

### Phase 3: Restore Previous Version (3 min)

#### 1. Identify Previous Version

```bash
# Check backup files
ls -ltr deployment-image-before.* deployment-state-before-* 2>/dev/null | tail -5

# Get previous image tag
PREVIOUS_IMAGE=$(cat deployment-image-before.txt 2>/dev/null)
echo "Previous image: $PREVIOUS_IMAGE"

# Verify image exists locally
docker images | grep $(echo $PREVIOUS_IMAGE | cut -d: -f1)
```

#### 2. Restore Configuration

```bash
# List backup configs
ls -ltr .env.production.backup-* | tail -3

# Restore previous env
BACKUP_FILE=$(ls -tr .env.production.backup-* | tail -1)
cp $BACKUP_FILE .env.production

# Verify config
echo "Restored from: $BACKUP_FILE"
grep "ENVIRONMENT=" .env.production
```

#### 3. Switch to Previous Version

```bash
# Update docker-compose to use previous image (if necessary)
# This depends on how images are managed (tag vs. registry)

# For tag-based: pull previous tag
docker pull docc2context-service:stable

# Or if using registry: pull specific version
docker pull registry.example.com/docc2context-service:2026-01-12

# Set current to restored version
docker tag docc2context-service:stable docc2context-service:latest
```

### Phase 4: Start Previous Version (3 min)

#### 1. Start Services

```bash
# Start with standard config (previous version)
docker-compose up -d

# Wait for services to start
sleep 10

# Check status
docker-compose ps

# Expected: All containers "Up"
```

#### 2. Health Check Loop

```bash
# Health check with retry
for i in {1..10}; do
  echo "Health check attempt $i/10..."
  if curl -s http://localhost:8000/health | jq . 2>/dev/null; then
    echo "✓ Service healthy"
    break
  fi
  echo "  Waiting... (attempt $((i+1)))"
  sleep 3
done

# Verify health endpoint returns proper response
curl -s http://localhost:8000/health | jq '.status'
# Expected: "ready"
```

#### 3. Quick Functionality Test

```bash
# Test metrics endpoint
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result | length'
# Expected: > 0 (metrics being collected)

# Test logging
curl -s http://localhost:9200/_count | jq '.count'
# Expected: > 0 (logs being ingested)

# Test basic health checks
docker-compose ps | grep "Up" | wc -l
# Expected: All containers running
```

### Phase 5: Verification (3 min)

#### 1. Service Verification

```bash
# Comprehensive health check
echo "=== SERVICE VERIFICATION ==="

# API health
curl -I http://localhost:8000/health | head -1
# Expected: HTTP/1.1 200

# Metrics collection
curl -s http://localhost:9090/-/healthy | head -1
# Expected: "Prometheus is healthy"

# Logging system
curl -s http://localhost:9200/_cluster/health | jq '.status'
# Expected: "green" or "yellow"

# Alert system
curl -s http://localhost:9093/-/healthy | head -1
# Expected: "AlertManager is healthy"
```

#### 2. Data Verification (if applicable)

```bash
# Check data integrity
# This depends on your data model

# Example: Verify no data loss
curl -s http://localhost:9200/_count | jq .

# Compare with baseline
# If count is less than expected, investigate
```

#### 3. Performance Verification

```bash
# Check resource usage
docker stats --no-stream app

# Expected:
# - Memory: < 1.5GB
# - CPU: < 20%
# - Network: normal traffic

# Check for errors in logs
docker-compose logs app | grep -i "error\|exception\|fatal" | tail -10
# Expected: No critical errors
```

### Phase 6: Communication (2 min)

#### 1. Notify Stakeholders

```bash
# Prepare notification
echo "ROLLBACK COMPLETED

Service: DocC2Context Service
Timestamp: $(date)
Previous Version: $(cat deployment-image-before.txt)
Reason: [Document reason for rollback]
Status: Service operational and verified

Next Steps:
1. Post-incident review in 24 hours
2. Root cause analysis
3. Corrective action implementation

Contact: [DevOps Lead Name]
" | mail -s "Service Rollback: DocC2Context" team@example.com
```

#### 2. Update Status Page (if applicable)

```bash
# If you have a status page:
# POST /api/status/incident
# {
#   "incident": "rollback",
#   "service": "docc2context",
#   "status": "operational",
#   "reason": "[reason]"
# }
```

#### 3. Document Incident

```bash
# Create incident record
cat > incident-$(date +%s).log << EOF
INCIDENT: Service Rollback

Timestamp: $(date)
Service: DocC2Context Service
Trigger: [Describe what went wrong]
Duration: [Time from detection to rollback]
Version Rolled Back From: $(cat deployment-image-before.txt)
Status: Service restored

Immediate Actions:
- [ ] Service verified healthy
- [ ] Stakeholders notified
- [ ] Logs preserved for analysis
- [ ] Post-incident review scheduled

Root Cause: [To be determined in review]
Prevention: [To be determined in review]
EOF
```

---

## Post-Rollback Activities

### Immediate (During Rollback)

- [x] Service health verified
- [x] Stakeholders notified
- [x] Incident documented
- [ ] On-call team acknowledged

### Within 1 Hour

- [ ] Team briefing (what happened)
- [ ] Preliminary impact assessment
- [ ] Investigation started
- [ ] Temporary workarounds implemented

### Within 24 Hours

- [ ] Post-incident review meeting
- [ ] Root cause analysis
- [ ] Corrective actions identified
- [ ] Prevention measures planned

### Within 1 Week

- [ ] Corrective actions implemented
- [ ] Fix validated in staging
- [ ] Re-deployment plan created
- [ ] Deployment approved and scheduled

---

## Rollback Troubleshooting

### Previous Version Won't Start

```bash
# Check image exists
docker images

# If image missing, pull from registry
docker pull registry.example.com/docc2context-service:previous-tag

# If can't reach registry:
# 1. Check network connectivity
# 2. Check registry credentials
# 3. Use local image if available

# Start with alternate image
docker tag docc2context-service:working docc2context-service:latest
docker-compose up -d
```

### Data Inconsistency After Rollback

```bash
# Check data status
curl -s http://localhost:9200/_cluster/health

# If degraded:
# 1. Check disk space
# 2. Check Elasticsearch logs
# 3. Restart Elasticsearch

docker-compose restart elasticsearch

# Wait for recovery
sleep 30

# Verify recovery
curl -s http://localhost:9200/_cluster/health
```

### Memory Keeps Growing

```bash
# Monitor memory over time
watch -n 2 'docker stats --no-stream app'

# If memory continues rising:
# 1. Check for memory leaks in logs
# 2. Restart container
# 3. Escalate to engineering team

docker-compose restart app
```

---

## Prevention

To prevent future rollbacks:

1. **Pre-Deployment Testing**
   - Run full test suite
   - Staging deployment rehearsal
   - Load testing in staging

2. **Gradual Rollout**
   - Blue-green deployment
   - Canary deployment
   - Progressive traffic migration

3. **Monitoring**
   - Set up proactive alerts
   - Monitor key metrics
   - Alert on anomalies

4. **Post-Deployment**
   - Bake time (30 min observation)
   - Gradual traffic increase
   - Watchful waiting period

---

## Rollback Checklist

Complete this checklist when executing rollback:

- [ ] Issue confirmed and verified
- [ ] Rollback authorized
- [ ] Team notified
- [ ] Current state backed up
- [ ] Service stopped gracefully
- [ ] Previous version verified
- [ ] Services started
- [ ] Health checks passing
- [ ] Data verified (no loss)
- [ ] Performance acceptable
- [ ] Stakeholders notified
- [ ] Incident logged
- [ ] Post-incident review scheduled
- [ ] Root cause investigation started

---

**Document Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Task:** 5.8 - Deployment Runbook & Handoff
