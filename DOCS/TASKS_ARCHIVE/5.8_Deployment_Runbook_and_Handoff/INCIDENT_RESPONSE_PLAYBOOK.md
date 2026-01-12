# Incident Response Playbook

**Purpose:** Procedures for responding to security incidents and operational emergencies
**Audience:** DevOps, Security, Engineering Teams
**Last Updated:** 2026-01-13

---

## Incident Classification

### Severity Levels

**CRITICAL** (P0)
- Service completely unavailable
- Data breach confirmed
- Customer data at risk
- Revenue impact immediate
- Response time: Immediate (< 5 min)

**HIGH** (P1)
- Service degraded significantly (>50% users affected)
- Security vulnerability discovered
- Potential data loss
- Revenue/reputation risk
- Response time: < 15 minutes

**MEDIUM** (P2)
- Service degraded (< 50% users affected)
- Possible security issue (not confirmed)
- Minor data loss or corruption
- Limited customer impact
- Response time: < 1 hour

**LOW** (P3)
- Minor service issues
- No security risk
- No data loss
- Information only
- Response time: < 4 hours

---

## Incident Scenarios

### Scenario 1: File Upload Security Attack

**Detection:**
- Error rate spike (>10% 5xx errors)
- Extraction failures (>20% rate increase)
- Suspicious upload patterns in logs
- Security alert triggered

#### Investigation Steps

```bash
# 1. Check error rate
curl -s http://localhost:9090/api/v1/query?query=http_requests_total | jq '.data.result[] | {status: .labels.code, rate: .value[1]}'

# 2. View security logs
curl -s http://localhost:5601/api/console/proxy?path=_search \
  -d '{
    "query": {
      "match": {
        "event_type": "security_alert"
      }
    }
  }' | jq '.hits.hits[].fields'

# 3. Check file uploads in last hour
docker-compose logs app | grep -i "upload\|extract\|validation" | tail -20

# 4. Identify malicious uploads
docker-compose logs app | grep -i "error\|rejected\|blocked" | head -10
```

#### Containment Actions

```bash
# 1. If attack ongoing: Restrict uploads
# Scale down conversion workers (optional)
docker-compose scale conversion-worker=0

# 2. Block specific IPs (if pattern detected)
# [Configure in nginx/firewall]
# iptables -A INPUT -s <attacker_ip> -j DROP

# 3. Enable rate limiting if not already
# [Verify in .env: RATE_LIMIT=10]

# 4. Alert security team
echo "SECURITY INCIDENT: Upload attack detected
Time: $(date)
Attack Type: Malicious file upload attempt
IPs: [list detected IPs]
Action: Uploads temporarily restricted
" | mail -s "URGENT: Security Incident" security@example.com
```

#### Recovery Actions

```bash
# 1. Review and quarantine suspicious uploads
ls -ltr /tmp/swift-conv-* | tail -10

# 2. Clear old workspaces
find /tmp/swift-conv-* -mtime +1 -delete

# 3. Restore normal operations
docker-compose scale conversion-worker=3

# 4. Verify health
curl http://localhost:8000/health

# 5. Monitor error rate recovery
watch 'curl -s http://localhost:9090/api/v1/query?query=http_request_errors_total | jq ".data.result[0].value"'
```

#### Post-Incident Review

```
Questions to answer:
1. What was the attack vector?
2. Did validation correctly block it?
3. Were rate limits sufficient?
4. How long before detected?
5. What can prevent next time?
6. Were logs adequate?

Action items:
- [ ] Update file validation rules
- [ ] Increase rate limit if needed
- [ ] Enhance monitoring
- [ ] Conduct security review
```

---

### Scenario 2: Resource Exhaustion

**Detection:**
- Memory usage > 90% of limit
- CPU usage > 95%, sustained > 2 min
- Request timeouts increasing
- Service slowdown reported

#### Investigation Steps

```bash
# 1. Check container resource usage
docker stats --no-stream app

# 2. Get resource limit info
docker inspect app | grep -A 10 "Memory"

# 3. Check running processes
docker top app

# 4. Analyze memory growth over time
curl -s http://localhost:9090/api/v1/query_range?query=container_memory_usage_bytes&start=<1h_ago>&end=now | jq '.data.result[] | {time: .value[0], memory: .value[1]}'

# 5. Check for memory leaks
docker-compose logs app | grep -i "memory\|oom\|killed" | tail -10
```

#### Containment Actions

```bash
# 1. Restrict new uploads temporarily
# Scale down workers
docker-compose scale api=1  # Keep only 1 instance

# 2. Increase container memory limit
# Edit docker-compose.yml and increase mem_limit

# 3. Restart container (if OOM risk)
docker-compose restart app

# 4. Notify users
echo "MAINTENANCE NOTICE: Service temporarily limited
We're performing emergency maintenance.
Uploads are temporarily restricted.
Estimated duration: 30 minutes
" | broadcast_to_users
```

#### Recovery Actions

```bash
# 1. Identify memory leak source
# Check application logs
docker-compose logs app | grep -E "(DEBUG|TRACE)" | tail -20

# 2. If memory leak in application:
docker-compose restart app

# 3. If persistent: Scale to multiple instances
docker-compose scale app=3

# 4. Monitor recovery
watch 'docker stats --no-stream app | awk "{print \$6}"'

# 5. Restore normal operations
docker-compose scale app=1  # Restore normal
```

#### Post-Incident Review

```
Questions:
1. What caused the memory spike?
2. Was it a memory leak?
3. Are memory limits appropriate?
4. Can we prevent this?
5. What monitoring improvements needed?

Actions:
- [ ] Fix memory leak (if found)
- [ ] Adjust memory limits
- [ ] Add memory alerts
- [ ] Implement memory monitoring
```

---

### Scenario 3: Data Corruption / Loss

**Detection:**
- Data inconsistency detected
- Unexpected file deletions
- Checksum mismatches
- Backup verification fails

#### Investigation Steps

```bash
# 1. Check Elasticsearch health
curl -s http://localhost:9200/_cluster/health | jq .

# 2. Check for shard issues
curl -s http://localhost:9200/_cat/shards | grep UNASSIGNED

# 3. Verify data count
curl -s http://localhost:9200/_cat/indices | jq '.[] | {index: .index, docs: .docs_count}'

# 4. Check backup status
ls -ltr backup-* | tail -5

# 5. Review logs for deletion operations
docker-compose logs app | grep -i "delete\|drop\|remove" | head -20
```

#### Containment Actions

```bash
# 1. IMMEDIATELY: Stop writing to database
docker-compose stop app

# 2. Preserve current state
docker-compose logs app > incident-logs-$(date +%s).log

# 3. Check if backup available
ls -la backup-* | tail -1

# 4. Alert DBA / Data team
echo "CRITICAL: Possible data loss detected
Time: $(date)
Service: DocC2Context Service
Action: Service stopped to prevent further loss
" | mail -s "CRITICAL: Data Loss Alert" dba@example.com
```

#### Recovery Actions

```bash
# 1. Restore from latest backup
LATEST_BACKUP=$(ls -tr backup-* | tail -1)
docker exec elasticsearch elasticsearch-restore --backup $LATEST_BACKUP

# 2. Verify restoration
curl -s http://localhost:9200/_count

# 3. Compare with known good state
# [Detailed comparison depends on data type]

# 4. Restart service
docker-compose start app

# 5. Verify operation
curl http://localhost:8000/health

# 6. Monitor for stability
watch 'curl -s http://localhost:9200/_count | jq ".count"'
```

#### Post-Incident Review

```
Questions:
1. What caused the data loss?
2. Was it preventable?
3. Was backup sufficient?
4. How long was service down?
5. How much data was lost?
6. Can we restore automatically?

Actions:
- [ ] Fix root cause
- [ ] Improve backup procedures
- [ ] Implement data validation
- [ ] Add data loss alerts
- [ ] Enhance monitoring
```

---

### Scenario 4: Service Degradation / Slowdown

**Detection:**
- Response time > 10 seconds
- Timeout errors increasing
- CPU usage high (> 80%)
- Queued requests building up

#### Investigation Steps

```bash
# 1. Check response times
curl -s http://localhost:9090/api/v1/query?query=http_request_duration_seconds_bucket | jq '.data.result[] | {p95: .value[1]}'

# 2. Check active connections
netstat -an | grep ESTABLISHED | wc -l

# 3. Check disk I/O
docker stats --no-stream app | awk '{print $NF}'

# 4. Check conversion queue
docker-compose logs app | grep -i "queue\|pending" | tail -10

# 5. Check for errors
docker-compose logs app | grep -i "error\|timeout" | tail -20
```

#### Containment Actions

```bash
# 1. Scale up workers to handle load
docker-compose scale api=3

# 2. Clear request queue (if safe)
# [Depends on queue implementation]

# 3. Enable aggressive caching
# [If applicable to your service]

# 4. Restrict heavy operations temporarily
# Disable background jobs if any

# 5. Notify users of slower service
echo "SERVICE NOTICE: High traffic detected
Service is experiencing slower response times.
We're scaling resources to handle demand.
" | broadcast_to_users
```

#### Recovery Actions

```bash
# 1. Identify bottleneck
# CPU-bound? Network-bound? I/O-bound?

# 2. For CPU bottleneck:
docker-compose scale api=3  # Add more workers
docker stats --no-stream app  # Monitor CPU

# 3. For I/O bottleneck:
docker top app  # Check I/O processes
# Consider optimizing queries or adding indexes

# 4. For network bottleneck:
# Check network configuration
# Verify load balancer distribution

# 5. Monitor recovery
watch 'curl -s http://localhost:9090/api/v1/query?query=http_request_duration_seconds | jq ".data.result[0].value[1]"'
```

#### Post-Incident Review

```
Questions:
1. What caused the slowdown?
2. Was it expected load or attack?
3. Did scaling help?
4. Are limits appropriate?
5. Can we predict this?

Actions:
- [ ] Optimize slow operations
- [ ] Improve load balancing
- [ ] Set up auto-scaling
- [ ] Enhance monitoring
- [ ] Capacity planning
```

---

### Scenario 5: Security Vulnerability Discovered

**Detection:**
- New CVE affecting dependency
- Security scan finds vulnerability
- Suspicious activity pattern
- Potential breach indicators

#### Investigation Steps

```bash
# 1. Identify affected dependency
grep "vulnerable-package==" requirements.txt

# 2. Check if exploitable
# Research CVE details
# Determine if code path exposed

# 3. Check logs for exploitation attempts
docker-compose logs app | grep -i "error\|exception" | grep "vulnerable-code"

# 4. Assess impact
# What data could be accessed?
# How many users affected?

# 5. Check if already compromised
# [Depends on vulnerability type]
```

#### Containment Actions

```bash
# 1. IMMEDIATE: If critical vulnerability
# Prepare to take service offline
docker-compose stop app

# 2. Apply temporary mitigation
# Update requirements.txt with patched version
# Rebuild image

# 3. Apply WAF rules (if applicable)
# Block known exploit patterns

# 4. Alert security team
echo "SECURITY: Vulnerability detected
Package: [package name]
Severity: [CRITICAL/HIGH]
CVE: [CVE number]
Action: Patch in progress
" | mail -s "Security Alert" security@example.com
```

#### Recovery Actions

```bash
# 1. Update dependency
sed -i 's/vulnerable-package==old/vulnerable-package==new/' requirements.txt

# 2. Rebuild image
docker build -t docc2context-service:patched .

# 3. Test in staging
docker-compose -f docker-compose.staging.yml up

# 4. Verify patch
pip show vulnerable-package | grep Version

# 5. Deploy patch
# Follow deployment runbook

# 6. Verify service
curl http://localhost:8000/health
```

#### Post-Incident Review

```
Questions:
1. How did this dependency get outdated?
2. Are we scanning dependencies?
3. What's the update process?
4. Was any data compromised?
5. How can we prevent next time?

Actions:
- [ ] Set up dependency scanning in CI
- [ ] Enable auto-updates
- [ ] Create security update SLA
- [ ] Add to compliance checklist
- [ ] Train team on security updates
```

---

## General Incident Procedures

### Escalation Chain

**Level 1 (Shift Engineer)**
- Monitors service
- Detects issues
- Initiates response

**Level 2 (On-Call Lead)**
- Authorizes actions
- Coordinates response
- Decides on rollback

**Level 3 (Manager)**
- Stakeholder communication
- Resource allocation
- Post-incident decisions

**Level 4 (VP/Executive)**
- Major incidents only
- External communication
- Strategy decisions

### Communication Template

```
INCIDENT ALERT

Severity: [P0/P1/P2/P3]
Service: DocC2Context Service
Time Detected: [timestamp]
Impact: [describe]
Status: [Investigating/In Progress/Resolved]

Investigation:
- Finding 1: [description]
- Finding 2: [description]

Actions Taken:
- Action 1: [description]
- Action 2: [description]

Current Status:
- Service health: [status]
- User impact: [description]
- ETA to resolution: [time]

Next Update: [time]
```

### Post-Incident Review

Schedule meeting within 24 hours:

**Attendees:**
- Incident commander
- Engineers involved
- DevOps team
- Product owner (if significant)

**Agenda:**
1. Timeline review (15 min)
2. Root cause analysis (15 min)
3. Contributing factors (10 min)
4. What went well (5 min)
5. What could improve (5 min)
6. Action items (10 min)

---

## Incident Response Checklist

- [ ] Issue detected and severity assessed
- [ ] Incident commander assigned
- [ ] Stakeholders notified
- [ ] Investigation started
- [ ] Root cause identified
- [ ] Corrective actions taken
- [ ] Service restored / verified
- [ ] Post-incident review scheduled
- [ ] Root cause documented
- [ ] Prevention measures planned
- [ ] Lessons documented
- [ ] Team trained on improvements

---

**Document Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Task:** 5.8 - Deployment Runbook & Handoff
