# Logging & Log Aggregation Guide (Task 5.3)

This document describes the centralized logging infrastructure using the ELK Stack (Elasticsearch, Logstash, Kibana) for DocC2Context Service.

---

## Overview

The ELK Stack provides:

- **Centralized log aggregation** from the FastAPI application
- **Real-time log search and filtering** via Kibana dashboards
- **Structured JSON logging** for machine-readable events
- **Log retention policies** (90 days for security, 30 days for operational)
- **Security event tracking** (auth failures, rate limits)
- **Performance monitoring** (extraction anomalies)

---

## Architecture

```
Application (FastAPI)
    ↓
Structured JSON Logging
    ↓
Logstash (processing pipeline)
    ↓
Elasticsearch (indexing & storage)
    ↓
Kibana (visualization & dashboards)
```

### Components

1. **Elasticsearch** (Port 9200)
   - Search and analytics engine
   - Stores and indexes all logs
   - Time-based index rotation (daily)

2. **Logstash** (Port 5000)
   - Log ingestion and processing
   - Filters and enriches log events
   - Forwards processed logs to Elasticsearch

3. **Kibana** (Port 5601)
   - Web UI for log visualization
   - Interactive dashboards
   - KQL (Kibana Query Language) search interface

4. **Application** (FastAPI)
   - Generates structured JSON logs
   - Includes request IDs for tracing
   - Logs security events and performance metrics

---

## Quick Start

### 1. Start the ELK Stack

```bash
docker-compose up -d elasticsearch logstash kibana
```

Wait for services to be healthy:

```bash
# Check Elasticsearch
curl -s http://localhost:9200/_cluster/health | jq .

# Check Kibana
curl -s http://localhost:5601/api/status
```

### 2. Initialize Elasticsearch

```bash
bash scripts/setup_elasticsearch.sh
```

This script:
- Creates the ILM (Index Lifecycle Management) policy
- Creates index templates with proper mappings
- Creates the initial index for today

### 3. Access Kibana Dashboard

Open browser: http://localhost:5601

### 4. Start the Application

```bash
docker-compose up -d app
```

---

## Log Types & Event Tracking

### Extraction Events

Logged when files are processed for conversion.

```json
{
  "event_type": "extraction",
  "status": "success|failure",
  "file_name": "archive.zip",
  "file_size_bytes": 1024000,
  "extraction_time_seconds": 2.5,
  "error_message": null,
  "timestamp": "2026-01-13T10:30:45.123456Z",
  "request_id": "uuid-string"
}
```

**Dashboard:** Extraction Failures

**KQL Query Examples:**
```
event_type:extraction AND status:failure
event_type:extraction AND status:success AND extraction_time_seconds > 5
event_type:extraction AND @timestamp:(now-1h TO now)
```

### Security Events: Authentication Failures

Logged when authentication attempts fail.

```json
{
  "event_type": "auth_failure",
  "username": "testuser",
  "client_ip": "192.168.1.1",
  "reason": "Invalid credentials",
  "timestamp": "2026-01-13T10:35:22.456789Z",
  "request_id": "uuid-string"
}
```

**Dashboard:** Security Events

**KQL Query Examples:**
```
event_type:auth_failure
event_type:auth_failure AND client_ip:192.168.1.*
event_type:auth_failure AND @timestamp:(now-24h TO now)
```

### Security Events: Rate Limiting

Logged when rate limit thresholds are exceeded.

```json
{
  "event_type": "rate_limit",
  "client_ip": "10.0.0.5",
  "endpoint": "/api/v1/convert",
  "limit": 10,
  "window": "1hour",
  "timestamp": "2026-01-13T10:40:33.789012Z",
  "request_id": "uuid-string"
}
```

**Dashboard:** Security Events

**KQL Query Examples:**
```
event_type:rate_limit
event_type:rate_limit AND endpoint:/api/v1/convert
event_type:rate_limit AND @timestamp:(now-1d TO now)
```

### Performance Anomalies

Logged when performance metrics exceed thresholds.

```json
{
  "event_type": "performance_anomaly",
  "metric": "extraction_time",
  "value": 15.5,
  "threshold": 10.0,
  "timestamp": "2026-01-13T10:45:50.012345Z",
  "request_id": "uuid-string"
}
```

**Dashboard:** Performance Anomalies

**KQL Query Examples:**
```
event_type:performance_anomaly
event_type:performance_anomaly AND metric:extraction_time AND value > 10
```

---

## Querying Logs

### Access Kibana

1. Open http://localhost:5601
2. Navigate to **Discover**
3. Select index: `docc2context-*`
4. Use the KQL search bar

### Common Queries

**Find all failures in the last 24 hours:**
```
status:failure AND @timestamp:(now-24h TO now)
```

**Find extraction anomalies:**
```
event_type:extraction AND extraction_time_seconds > 10
```

**Find security issues:**
```
event_type:(auth_failure OR rate_limit)
```

**Find errors for a specific file:**
```
file_name:"myfile.zip" AND status:failure
```

**Find requests from a specific IP:**
```
client_ip:192.168.1.100
```

**Trace a specific request:**
```
request_id:"specific-uuid-here"
```

---

## Dashboards

### 1. Extraction Failures Dashboard

**Purpose:** Monitor file conversion/extraction issues

**Key Visualizations:**
- Failure rate over time (line chart)
- Top 10 files by failure count (table)
- Failure reasons distribution (pie chart)
- Recent failures (last 1 hour) with details
- Extraction time histogram
- Failures by file size (scatter plot)

**Access:** Kibana → Dashboards → Extraction Failures

### 2. Security Events Dashboard

**Purpose:** Monitor authentication and rate limiting incidents

**Key Visualizations:**
- Failed authentication attempts (24h count)
- Failed auth by IP (table)
- Rate limit triggers (24h count)
- Rate limits by endpoint (bar chart)
- Top IPs triggering rate limits (table)
- Security events timeline

**Access:** Kibana → Dashboards → Security Events

### 3. Performance Anomalies Dashboard

**Purpose:** Track extraction performance and system anomalies

**Key Visualizations:**
- Average extraction time trend
- P95 extraction time (last 24h)
- Extraction time vs file size (scatter)
- Performance anomalies detected (table)
- Success vs failure time comparison
- Extraction rate (files/hour)
- Slowest extractions (table)
- Anomalies over time

**Access:** Kibana → Dashboards → Performance Anomalies

---

## Log Retention Policy

### Lifecycle Management (ILM)

Logs automatically transition through lifecycle phases:

| Phase | Age Range | Actions | Storage |
|-------|-----------|---------|---------|
| **Hot** | 0-1 day | Real-time indexing, rollover at 50GB | SSD (fast) |
| **Warm** | 1-30 days | Read-only, force merge | Standard |
| **Cold** | 30-90 days | Searchable snapshots | Slower storage |
| **Delete** | 90+ days | Permanent deletion | N/A |

### Retention by Event Type

**Security Events:** 90 days (production requirement)
- `auth_failure`
- `rate_limit`

**Operational Logs:** 30 days
- `extraction`
- `performance_anomaly`

### Managing Indices

**View all indices:**
```bash
curl -s http://localhost:9200/_cat/indices?v
```

**View ILM policy:**
```bash
curl -s http://localhost:9200/_ilm/policy/docc2context-retention | jq .
```

**Manually delete an old index:**
```bash
curl -X DELETE http://localhost:9200/docc2context-2025.01.01
```

---

## Using Structured Logger in Code

### Import and Initialize

```python
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)
```

### Log Extraction Events

```python
# Success
logger.log_extraction(
    status="success",
    file_name="archive.zip",
    file_size=len(file_content),
    extraction_time=2.5,
    request_id=request_id
)

# Failure
logger.log_extraction(
    status="failure",
    file_name="bad.zip",
    file_size=0,
    extraction_time=0.1,
    error_msg="Invalid ZIP format",
    request_id=request_id
)
```

### Log Security Events

```python
# Auth failure
logger.log_auth_failure(
    username="user@example.com",
    ip_address="192.168.1.100",
    reason="Invalid credentials",
    request_id=request_id
)

# Rate limit
logger.log_rate_limit(
    ip_address="10.0.0.5",
    endpoint="/api/v1/convert",
    limit=10,
    window="1hour",
    request_id=request_id
)
```

### Log Performance Issues

```python
logger.log_performance_anomaly(
    metric_name="extraction_time",
    value=15.5,
    threshold=10.0,
    request_id=request_id
)
```

---

## Elasticsearch API Examples

### Search for Logs

```bash
# All extraction failures
curl -s 'http://localhost:9200/docc2context-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"match": {"event_type": "extraction"}},
          {"match": {"status": "failure"}}
        ]
      }
    },
    "size": 20
  }' | jq .
```

### Aggregations (Analytics)

```bash
# Count failures by error type
curl -s 'http://localhost:9200/docc2context-*/_search' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {"match": {"status": "failure"}},
    "aggs": {
      "errors": {
        "terms": {"field": "error_message.keyword", "size": 10}
      }
    },
    "size": 0
  }' | jq .
```

---

## Troubleshooting

### Logs Not Appearing in Elasticsearch

1. **Check Logstash connectivity:**
   ```bash
   docker logs docc2context-logstash
   ```

2. **Verify application logging:**
   ```bash
   docker logs docc2context-service | head -20
   ```

3. **Check Elasticsearch health:**
   ```bash
   curl -s http://localhost:9200/_cluster/health | jq .
   ```

### Kibana Won't Load

1. **Verify Elasticsearch is running:**
   ```bash
   curl -s http://localhost:9200/ | jq .
   ```

2. **Check Kibana logs:**
   ```bash
   docker logs docc2context-kibana
   ```

3. **Restart Kibana:**
   ```bash
   docker restart docc2context-kibana
   ```

### Out of Disk Space

1. **Check disk usage:**
   ```bash
   docker exec docc2context-elasticsearch \
     curl -s http://localhost:9200/_cat/indices?v
   ```

2. **Delete old indices:**
   ```bash
   curl -X DELETE http://localhost:9200/docc2context-2026.01.01
   ```

3. **Adjust retention policy** in `logstash_retention.conf`

### High Memory Usage

1. **Reduce Java heap:**
   ```bash
   # Edit docker-compose.yml, change:
   # ES_JAVA_OPTS=-Xms512m -Xmx512m
   # to smaller values (e.g., 256m/256m)
   ```

2. **Restart Elasticsearch:**
   ```bash
   docker-compose restart elasticsearch
   ```

---

## Production Considerations

### Security

- [ ] Enable Elasticsearch X-Pack security
- [ ] Configure TLS/SSL for Elasticsearch
- [ ] Set up Kibana authentication
- [ ] Restrict Elasticsearch network access

### Performance

- [ ] Use multi-node Elasticsearch cluster
- [ ] Configure sharding and replication
- [ ] Implement snapshot/backup strategy
- [ ] Monitor Elasticsearch resource usage

### Monitoring

- [ ] Set up alerts for log ingestion failures
- [ ] Monitor Elasticsearch disk space
- [ ] Track log volume growth
- [ ] Configure log aggregation from other services

### Backup & Recovery

```bash
# Create Elasticsearch snapshot
curl -X PUT http://localhost:9200/_snapshot/backup

# Restore from snapshot
curl -X POST http://localhost:9200/_snapshot/backup/snapshot-1/_restore
```

---

## Integration with Alertmanager

Logs can trigger Prometheus alerts via custom rules:

```yaml
groups:
  - name: log_alerts
    rules:
      - alert: HighExtractFailureRate
        expr: |
          count(docc2context_extraction_failures{status="failure"} [5m]) /
          count(docc2context_extractions [5m]) > 0.2
        for: 5m
        annotations:
          summary: "High extraction failure rate detected"
```

---

## Related Documentation

- [Monitoring & Alerting Guide](MONITORING.md) - Prometheus metrics and alerts
- [Security Implementation](SECURITY_IMPLEMENTATION_SUMMARY.md) - Security requirements
- [Deployment Guide](DEPLOYMENT.md) - Production deployment

---

**Last Updated:** 2026-01-13
**Task:** 5.3 - Set Up Log Aggregation
