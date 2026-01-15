# Monitoring & Alerting Guide (Task 5.2)

## Overview

DocC2Context Service uses Prometheus for metrics collection and Alertmanager for alert routing. This guide covers setup, configuration, and responding to alerts.

## Components

### Prometheus
- **Purpose:** Collect and store metrics
- **URL (local):** http://localhost:9090
- **Scrape interval:** 5 seconds
- **Retention:** 15 days (default)
- **Config file:** `prometheus.yml`

### Alertmanager
- **Purpose:** Route and manage alerts
- **URL (local):** http://localhost:9093
- **Config file:** `alertmanager.yml`

### Alert Rules
- **File:** `alert_rules.yml`
- **Alerts:** 6 critical/warning alerts
- **Playbooks:** `DOCS/PLAYBOOKS/`

## Quick Start

### Start monitoring locally (development):
```bash
# Start Prometheus and Alertmanager
docker-compose up prometheus alertmanager

# Access dashboards
# Prometheus: http://localhost:9090
# Alertmanager: http://localhost:9093

# Verify metrics are being collected
curl http://localhost:8000/metrics | head -20
```

### View metrics in Prometheus:
```
1. Go to http://localhost:9090
2. Click "Graph" tab
3. Enter query, e.g.:
   - http_requests_total (all requests)
   - rate(http_requests_total[5m]) (request rate)
   - http_request_duration_seconds (response times)
4. Click "Execute" to view
```

## Metrics Available

### HTTP Metrics
- `http_requests_total{method, endpoint, status}` - Total requests by method, endpoint, and status code
- `http_request_duration_seconds{method, endpoint}` - Request duration (histogram)

### ZIP Extraction Metrics
- `zip_extractions_total{status}` - Total extraction attempts
- `zip_extraction_duration_seconds` - Extraction duration
- `extraction_file_count` - Files per ZIP
- `extraction_size_bytes` - Extracted content size

### Operational Metrics
- `active_conversions` - Currently running conversions
- `conversion_errors_total{error_type}` - Errors by type
- `resource_usage{resource_type}` - CPU/memory/disk metrics

## Alerts

### Critical Alerts (require immediate action)
- **HighErrorRate** (>10% 5xx errors) - Service may be crashing
- **HighMemoryUsage** (>1800MB) - Risk of OOM kill
- **LowDiskSpace** (<1GB) - May stop accepting files
- **ServiceDown** (>1 min unreachable) - Complete outage

### Warning Alerts (should be investigated)
- **HighExtractionFailureRate** (>20% failures) - Many bad ZIPs or limits hit
- **HighCPUUsage** (>80% for 5+ min) - May need to scale

## Alert Playbooks

Each alert has a playbook at `DOCS/PLAYBOOKS/{AlertName}.md`:

| Alert | Playbook | Typical Fix Time |
|-------|----------|-----------------|
| HighErrorRate | `high_error_rate.md` | 5-10 min |
| ExtractionFailures | `extraction_failures.md` | 5-15 min |
| MemoryExhaustion | `memory_exhaustion.md` | 10-20 min |
| CPUExhaustion | `cpu_exhaustion.md` | 20+ min (scale) |
| ServiceDown | `service_down.md` | 2-5 min |

## Testing Alerts Locally

### Test high error rate alert:
```bash
# Simulate errors (these will 404)
for i in {1..100}; do
  curl -s http://localhost:8000/invalid-endpoint > /dev/null &
done

# Wait 2+ minutes, check Alertmanager
curl http://localhost:9093/api/v1/alerts | jq '.data[] | .labels.alertname'
```

### Test metrics being collected:
```bash
# Make some requests
curl http://localhost:8000/health
curl http://localhost:8000/health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics | grep http_requests_total
# Should see count increased
```

## Integrating Alerting (Production)

### Slack Integration

1. **Create Slack Webhook:**
   - Go to https://api.slack.com/messaging/webhooks
   - Create new app, enable webhooks
   - Copy webhook URL

2. **Update `alertmanager.yml`:**
   ```yaml
   receivers:
     - name: 'critical'
       slack_configs:
         - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
           channel: '#critical-alerts'
           title: 'CRITICAL: {{ .GroupLabels.alertname }}'
   ```

3. **Restart Alertmanager:**
   ```bash
   docker-compose restart alertmanager
   ```

4. **Test:**
   ```bash
   # Trigger an alert or use amtool
   docker exec -it alertmanager amtool alert add TestAlert severity=critical
   ```

### Email Integration

1. **Configure in `alertmanager.yml`:**
   ```yaml
   global:
     smtp_smarthost: 'smtp.example.com:587'
     smtp_auth_username: 'your-email@example.com'
     smtp_auth_password: 'your-password'

   receivers:
     - name: 'critical'
       email_configs:
         - to: 'oncall@example.com'
           from: 'alerts@example.com'
   ```

### PagerDuty Integration

1. **Get routing key from PagerDuty**

2. **Configure in `alertmanager.yml`:**
   ```yaml
   receivers:
     - name: 'critical'
       pagerduty_configs:
         - routing_key: 'YOUR_ROUTING_KEY'
           description: '{{ .GroupLabels.alertname }}'
   ```

## Monitoring Queries (Prometheus)

### Service Health
```
# Request rate (requests per second)
rate(http_requests_total[1m])

# Error rate percentage
(sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100

# P95 response time
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Currently processing conversions
active_conversions
```

### Resource Monitoring
```
# Memory usage
resource_usage{resource_type="memory_mb"}

# CPU usage
resource_usage{resource_type="cpu_percent"}

# Free disk space
resource_usage{resource_type="disk_free_gb"}
```

### Extraction Metrics
```
# Extraction success rate
(sum(rate(zip_extractions_total{status="success"}[5m])) / sum(rate(zip_extractions_total[5m]))) * 100

# Average extraction time
avg(zip_extraction_duration_seconds_bucket)

# Largest extraction
max(extraction_size_bytes)
```

## Dashboards

For visual monitoring, create Grafana dashboards using these metrics:

```json
{
  "dashboard": {
    "title": "DocC2Context Service",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{"expr": "rate(http_requests_total[1m])"}]
      },
      {
        "title": "Error Rate",
        "targets": [{"expr": "(sum(rate(http_requests_total{status=~\"5...\"}[5m])) / sum(rate(http_requests_total[5m]))) * 100"}]
      },
      {
        "title": "Memory Usage",
        "targets": [{"expr": "resource_usage{resource_type=\"memory_mb\"}"}]
      }
    ]
  }
}
```

## Troubleshooting

### Prometheus not scraping metrics
```bash
# Check if service is running
docker-compose ps prometheus

# Check logs
docker logs prometheus

# Test metrics endpoint
curl http://localhost:8000/metrics | head
```

### Alertmanager not sending alerts
```bash
# Check if running
docker-compose ps alertmanager

# Check configuration
docker exec alertmanager amtool config routes

# Check logs
docker logs alertmanager
```

### Too many/too few alerts
- Edit thresholds in `alert_rules.yml`
- Adjust time windows (for, evaluation_interval)
- Restart Prometheus: `docker-compose restart prometheus`

## Performance Impact

- **Metrics collection overhead:** <1% CPU, <10MB memory
- **Scrape interval:** 5 seconds (can adjust in prometheus.yml)
- **Alert evaluation:** Every 30 seconds (can adjust in alert_rules.yml)

## Storage

- **Prometheus disk usage:** ~50MB per day (depends on cardinality)
- **Retention:** Set in prometheus.yml
- **To disable storage:** Set `--storage.tsdb.retention.time=1h` for short-lived test

## References

- Prometheus docs: https://prometheus.io/docs/
- Alertmanager docs: https://prometheus.io/docs/alerting/latest/overview/
- PromQL guide: https://prometheus.io/docs/prometheus/latest/querying/basics/
- Alert playbooks: See `DOCS/PLAYBOOKS/` directory
