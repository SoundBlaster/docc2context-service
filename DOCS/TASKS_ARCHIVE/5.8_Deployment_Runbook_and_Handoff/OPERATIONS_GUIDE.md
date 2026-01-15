# Operations Guide

**Purpose:** Comprehensive guide for operating DocC2Context Service in production
**Audience:** DevOps, Operations, Site Reliability Engineers
**Last Updated:** 2026-01-13

---

## Table of Contents

1. System Overview
2. Daily Operations
3. Monitoring & Alerts
4. Scaling Operations
5. Backup & Recovery
6. Maintenance Tasks
7. Troubleshooting Reference
8. Contact Information

---

## System Overview

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Reverse Proxy                         │
│                   (Nginx/CloudFlare)                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Load Balancer (Optional)                    │
└────────────────────┬────────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
│  API     │  │  API       │  │  API       │
│  (1-N    │  │  Instance  │  │  Instance  │
│instances)│  │     2      │  │     N      │
└───┬──────┘  └─────┬──────┘  └─────┬──────┘
    └────────────────┼────────────────┘
                     │
    ┌────────────────┼────────────────────────┐
    │                │                        │
┌───▼─────┐  ┌──────▼──────┐  ┌─────────────▼──┐
│  Redis  │  │ Elasticsearch│  │  Logstash /  │
│ (Cache) │  │  (Logs)      │  │  Kibana      │
└─────────┘  └──────────────┘  └──────────────┘
    │
┌───▼──────────────────────────────────────────────────┐
│        Prometheus + Alertmanager (Monitoring)         │
└───────────────────────────────────────────────────────┘
```

### Key Components

**Application Layer:**
- FastAPI service (multi-instance)
- Swift CLI binary integration
- File validation engine
- Workspace manager

**Data Layer:**
- Redis (caching, rate limiting)
- Elasticsearch (log storage)
- Local filesystem (temporary workspaces)

**Monitoring Layer:**
- Prometheus (metrics collection)
- Alertmanager (alert routing)
- Grafana (dashboards)
- Kibana (log analysis)

### Resource Specifications

**Per Instance:**
- CPU: 2 cores (limit)
- Memory: 2GB (limit)
- Disk: 50GB for logs/workspaces
- Network: 1Gbps capable

**Dependencies:**
- Redis: 1GB memory
- Elasticsearch: 4GB memory
- Prometheus: 2GB memory
- Logstash: 1GB memory

**Total for Full Stack:** ~12GB memory, 4+ cores recommended

---

## Daily Operations

### Morning Checklist

```bash
#!/bin/bash
# Daily health check on arrival

echo "=== DocC2Context Service - Daily Checklist ==="

# 1. Service Status
echo "1. Service Status:"
docker-compose ps
echo "   Expected: All containers Up"

# 2. Error Rate
echo "2. Error Rate (last 1 hour):"
curl -s http://localhost:9090/api/v1/query?query='http_requests_total{status=~"5.."}'
echo "   Expected: < 1% of requests"

# 3. Resource Usage
echo "3. Resource Usage:"
docker stats --no-stream app
echo "   Expected: Memory < 1.5GB, CPU < 20%"

# 4. Disk Space
echo "4. Disk Space:"
df -h /tmp | tail -1
echo "   Expected: > 10GB free"

# 5. ELK Health
echo "5. Log Aggregation Health:"
curl -s http://localhost:9200/_cluster/health | jq '.status'
echo "   Expected: green or yellow"

# 6. Pending Alerts
echo "6. Pending Alerts:"
curl -s http://localhost:9093/api/v1/alerts | jq '.data | length'
echo "   Expected: 0 alerts"
```

### Hour-by-Hour Monitoring

**Every hour:**
- Check error rate
- Review critical alerts
- Spot check application logs
- Monitor key metrics

### End of Day Review

```bash
#!/bin/bash
# End of shift handoff

echo "=== End of Shift Handoff ==="

# 1. Summarize metrics
curl -s http://localhost:9090/api/v1/query?query=increase\(http_requests_total\[24h\]\) | jq '.data.result[] | {job: .labels.job, requests: .value[1]}'

# 2. Identify any incidents
docker-compose logs app | grep -i "error\|exception\|alert" | wc -l

# 3. Backup key data
docker-compose exec elasticsearch curl -s http://localhost:9200/_snapshot/backup/_status

# 4. Document observations
cat > handoff-$(date +%s).log << EOF
Shift Summary:
- Uptime: 100%
- Total Requests: [number]
- Error Rate: [percentage]
- Incidents: [list]
- Alerts Triggered: [list]
- Issues for Next Shift: [list]
EOF
```

---

## Monitoring & Alerts

### Key Metrics to Watch

**Availability:**
- Service uptime: Target 99.9%
- Health check success rate: Target 100%

**Performance:**
- API response time (p95): Target < 2s
- Error rate: Target < 0.1%
- File extraction rate: Target > 95% success

**Resources:**
- Memory usage: Alert at 80%
- CPU usage: Alert at 75%
- Disk usage: Alert at 85%
- Network: Monitor for anomalies

**Security:**
- Failed validation attempts: Alert on spike
- Rate limit triggers: Alert on > 10/hour
- Error 400+ rate: Alert on spike

### Alert Interpretation

**HighErrorRate Alert**
- Meaning: > 10% of requests returning 5xx
- Action: Check error logs, restart if needed
- Escalate if: Persists > 5 min

**ExtractionFailures Alert**
- Meaning: > 20% of conversions failing
- Action: Check file validation, check disk space
- Escalate if: Continues increasing

**MemoryExhaustion Alert**
- Meaning: Memory > 80% of limit
- Action: Check for memory leaks, restart
- Escalate if: Memory keeps growing

**CPUExhaustion Alert**
- Meaning: CPU > 75% sustained
- Action: Scale up or check for slow operations
- Escalate if: Cannot improve with scaling

**ServiceDown Alert**
- Meaning: Service unreachable for > 1 min
- Action: IMMEDIATELY: Check status, restart if needed
- Escalate: IMMEDIATELY

---

## Scaling Operations

### Horizontal Scaling (Add Instances)

When to scale:
- CPU usage > 75% for > 10 min
- Memory usage > 80%
- Request queue growing
- Response time degrading

How to scale:

```bash
# Add more API instances
docker-compose scale api=3

# Monitor new instances
watch docker-compose ps

# Verify load distribution
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result | length'
```

### Vertical Scaling (Increase Resources)

When needed:
- Single instance maxed out
- Peak traffic predictable
- Cost-effective than horizontal

How to scale:

```bash
# Update docker-compose.yml
# Increase mem_limit and cpu limits

# Rebuild and restart
docker-compose down
docker-compose up -d

# Verify limits applied
docker inspect app | grep -A 2 Memory
```

### Auto-Scaling Setup (Optional)

For production, consider:

```yaml
# docker-compose with resource constraints
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

Then use orchestration (Kubernetes, Docker Swarm) for auto-scaling.

---

## Backup & Recovery

### Daily Backup Procedure

```bash
#!/bin/bash
# Run daily backup at 2 AM

# 1. Backup Elasticsearch
docker-compose exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup/daily-$(date +%Y%m%d)" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "*",
    "ignore_unavailable": true,
    "include_global_state": false
  }'

# 2. Backup configuration
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
  .env.production \
  docker-compose.yml \
  docker-compose.production.yml \
  prometheus.yml \
  alertmanager.yml

# 3. Verify backup
docker-compose exec elasticsearch curl -s "localhost:9200/_snapshot/backup" | jq '.snapshots | length'
```

### Restore from Backup

```bash
#!/bin/bash
# Restore from backup

# 1. Find backup to restore
docker-compose exec elasticsearch curl -s "localhost:9200/_snapshot/backup/_all"

# 2. Restore specific snapshot
docker-compose exec elasticsearch curl -X POST "localhost:9200/_snapshot/backup/<snapshot-name>/_restore"

# 3. Verify restoration
curl -s http://localhost:9200/_count | jq '.count'
```

---

## Maintenance Tasks

### Weekly

- [ ] Review error logs for patterns
- [ ] Check dependency updates available
- [ ] Verify backup success
- [ ] Review metrics for trends
- [ ] Update runbook if needed

### Monthly

- [ ] Security vulnerability scan
- [ ] Dependency updates (if safe)
- [ ] Capacity planning review
- [ ] Performance analysis
- [ ] Disaster recovery test

### Quarterly

- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Scaling strategy review
- [ ] Cost analysis
- [ ] Team training refresher

---

## Troubleshooting Reference

### Service Won't Start

```bash
# Check logs
docker-compose logs app

# Common issues:
# 1. Port in use: lsof -i :8000
# 2. Missing env: grep ENVIRONMENT .env
# 3. Dependency down: docker-compose ps

# Solutions:
docker-compose restart app
docker-compose up -d --force-recreate
```

### High Memory Usage

```bash
# Check memory
docker stats --no-stream app

# Investigate
docker top app  # See processes
docker-compose logs app | grep -i memory

# Solution
docker-compose restart app
# If persists, check for memory leak
```

### Slow Performance

```bash
# Check response times
curl -s http://localhost:9090/api/v1/query?query=http_request_duration_seconds

# Check resource usage
docker stats --no-stream

# Check load
netstat -an | grep ESTABLISHED | wc -l

# Solutions
docker-compose scale api=3  # Scale up
# Or identify slow operation and optimize
```

See ROLLBACK_RUNBOOK.md and INCIDENT_RESPONSE_PLAYBOOK.md for additional scenarios.

---

## Contact Information

**On-Call Engineer**
- Name: ________________________
- Phone: ________________________
- Email: ________________________

**DevOps Lead**
- Name: ________________________
- Phone: ________________________
- Email: ________________________

**Security Team**
- Email: ________________________
- Escalation: ________________________

**Incident Commander**
- Name: ________________________
- Phone: ________________________

**Emergency Numbers**
- Security Incident: ________________________
- Critical Incident: ________________________

---

## Key Documents

- DEPLOYMENT_CHECKLIST.md - Pre-deployment verification
- DEPLOYMENT_RUNBOOK.md - Step-by-step deployment
- ROLLBACK_RUNBOOK.md - Emergency rollback
- INCIDENT_RESPONSE_PLAYBOOK.md - Incident procedures
- OPERATIONS_GUIDE.md - This document

---

**Document Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Task:** 5.8 - Deployment Runbook & Handoff
