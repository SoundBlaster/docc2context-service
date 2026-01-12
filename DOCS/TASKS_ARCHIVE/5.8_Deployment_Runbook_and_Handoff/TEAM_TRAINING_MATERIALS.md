# Team Training Materials

**Purpose:** Documentation and materials for operations team training
**Audience:** DevOps Engineers, Operations Staff, Support Team
**Date:** 2026-01-13
**Facilitator:** Claude AI (Security & DevOps)

---

## Training Objectives

By the end of this training, participants will understand:

1. **Service Architecture:** How DocC2Context Service is designed and deployed
2. **Operations:** Daily operations, monitoring, and routine tasks
3. **Deployment:** How to safely deploy new versions
4. **Incident Response:** How to identify, respond to, and resolve incidents
5. **Troubleshooting:** How to diagnose and fix common problems
6. **Escalation:** When and how to escalate issues

---

## Module 1: Service Architecture (30 minutes)

### Overview

**DocC2Context Service** converts Swift DocC archives to Markdown files.

**Key components:**
- FastAPI application (Python)
- Swift CLI integration (compiled binary)
- File validation and security
- Monitoring and logging stack

### Deployment Architecture

```
Users
  ↓
Reverse Proxy (Nginx)
  ↓
Load Balancer
  ↓
API Instances (1-N)
  ├─ Cache (Redis)
  ├─ Storage (Workspaces in /tmp)
  └─ Logging (ELK Stack)
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10 |
| Framework | FastAPI | Latest |
| Deployment | Docker | 20.10+ |
| Orchestration | Docker Compose | Latest |
| CLI | Swift | docc2context |
| Cache | Redis | 7.x |
| Logs | Elasticsearch | 8.5+ |
| Metrics | Prometheus | Latest |

### Data Flow

```
1. User uploads ZIP file
   ↓
2. Validation (magic number, size, etc.)
   ↓
3. Extract to ephemeral workspace
   ↓
4. Invoke Swift CLI binary
   ↓
5. Collect converted Markdown files
   ↓
6. Stream response as ZIP
   ↓
7. Clean up workspace
```

---

## Module 2: Daily Operations (45 minutes)

### Morning Startup Checks

```bash
# Run daily checklist
docker-compose ps                           # All containers Up
curl http://localhost:8000/health          # Health endpoint
docker stats --no-stream app                # Resource usage
df -h /tmp                                 # Disk space
```

### Monitoring Dashboard

**Prometheus:** http://localhost:9090
- Key metrics: Request rate, error rate, response time
- Useful queries: `rate(http_requests_total[5m])`

**Kibana:** http://localhost:5601
- Search logs by request ID
- View extraction failures
- Track security events

**Grafana (optional):** Pre-built dashboards
- Service health
- Resource usage
- Extraction pipeline

### Alert Response

**When an alert fires:**

1. **Check severity** - Is it critical?
2. **Investigate** - What's the issue?
3. **Respond** - Follow incident response playbook
4. **Document** - Log what happened

**Common alerts:**

| Alert | Meaning | Action |
|-------|---------|--------|
| HighErrorRate | > 10% errors | Check logs, restart if needed |
| MemoryExhaustion | Memory > 80% | Check for leaks, restart |
| ServiceDown | Unreachable | Immediate restart |
| ExtractionFailures | > 20% failing | Check file validation |

---

## Module 3: Scaling & Performance (30 minutes)

### Horizontal Scaling

Scale up when:
- CPU usage > 75%
- Memory usage > 80%
- Response time degrading
- Request queue building

**How to scale:**

```bash
docker-compose scale api=3    # Add instances
docker-compose ps             # Verify new instances
# Load balancer distributes traffic automatically
```

### Performance Optimization

**Before scaling, optimize:**

1. Check for slow operations in logs
2. Analyze extraction pipeline performance
3. Verify file validation isn't bottleneck
4. Check network connectivity

**Metrics to monitor:**

- API response time (target < 2s p95)
- Extraction success rate (target > 95%)
- Memory per instance (target < 1.5GB)
- CPU per instance (target < 20% average)

---

## Module 4: Deployment (60 minutes)

### Pre-Deployment Checklist

Use DEPLOYMENT_CHECKLIST.md:

- Environment variables correct
- Image built successfully
- Tests passing
- No secrets exposed
- Team aware of deployment

### Deployment Steps

1. Back up current state
2. Build new Docker image
3. Verify image integrity
4. Stop old containers gracefully
5. Start new containers
6. Run health checks
7. Verify monitoring
8. Test basic functionality

**See DEPLOYMENT_RUNBOOK.md for details.**

### Rollback Procedures

**When to rollback:**

- Service unavailable
- Error rate > 10%
- Data corruption
- Critical vulnerability
- Any critical issue

**How to rollback:**

```bash
# Quick rollback
docker-compose down
cp .env.production.backup-<timestamp> .env
docker-compose up -d
curl http://localhost:8000/health
```

**See ROLLBACK_RUNBOOK.md for detailed procedures.**

### Deployment Rehearsal

**Schedule:** Monthly (before production deployment)

**Procedure:**
1. Use staging environment
2. Execute full deployment checklist
3. Run all verification steps
4. Practice rollback
5. Document issues found
6. Review lessons learned

---

## Module 5: Incident Response (45 minutes)

### Incident Detection

**How to identify issues:**

1. Monitor dashboard alerts
2. Check error logs
3. Review user reports
4. Monitor resource usage
5. Check security alerts

### Incident Severity

| Severity | Impact | Response |
|----------|--------|----------|
| P0 - Critical | Service down | Immediate (< 5 min) |
| P1 - High | Degraded | Within 15 min |
| P2 - Medium | Limited | Within 1 hour |
| P3 - Low | Minor | Within 4 hours |

### Response Procedure

1. **Detect:** Alert or report
2. **Assess:** Severity and impact
3. **Respond:** Execute playbook
4. **Communicate:** Update status
5. **Resolve:** Fix issue
6. **Review:** Post-incident meeting

**See INCIDENT_RESPONSE_PLAYBOOK.md for scenarios.**

### Common Scenarios

**Scenario 1: Upload attacks**
- Spike in validation errors
- Check security logs
- Restrict uploads if needed
- Contact security team

**Scenario 2: Resource exhaustion**
- Memory/CPU hitting limits
- Scale up instances
- Check for memory leaks
- Restart if necessary

**Scenario 3: Service degradation**
- Slow responses
- Check resource usage
- Check error logs
- Scale or restart

**Scenario 4: Data issues**
- Unexpected deletions
- Verify backups
- Restore if needed
- Investigate cause

---

## Module 6: Troubleshooting (30 minutes)

### Common Issues

| Issue | Symptom | Diagnosis | Solution |
|-------|---------|-----------|----------|
| High memory | Memory > 1.5GB | Check logs, resource use | Restart, check for leak |
| Slow response | Response > 10s | Check CPU/disk | Scale up, optimize |
| Service down | Health check fails | Docker logs | Restart, check config |
| Upload errors | 400/413 errors | Validation logs | Check file, check limits |
| Data issues | Missing records | Elasticsearch health | Restore from backup |

### Debugging Tools

**Container logs:**
```bash
docker-compose logs app           # Last 100 lines
docker-compose logs -f app        # Follow logs
docker-compose logs app | tail -50 # Last 50 lines
```

**Resource monitoring:**
```bash
docker stats --no-stream           # Current usage
docker top app                     # Running processes
docker inspect app | grep Memory   # Memory limits
```

**Network debugging:**
```bash
netstat -an | grep 8000           # Port usage
curl -v http://localhost:8000/health  # Detailed response
```

**Database/cache:**
```bash
docker-compose exec redis redis-cli INFO
docker-compose exec elasticsearch curl -s _cluster/health
```

---

## Module 7: Escalation & Support (15 minutes)

### Escalation Path

```
Level 1: Shift Engineer
  ↓ (if cannot resolve in 10 min)
Level 2: On-Call DevOps Lead
  ↓ (if critical or unresolved in 30 min)
Level 3: Engineering Manager
  ↓ (if customer impact or security issue)
Level 4: VP Engineering
```

### When to Escalate

- Service down
- Data loss
- Security incident
- Stuck on diagnosis > 15 min
- Multiple instances failing
- Rollback needed

### Communication

**Alert team:**
- Slack: #incidents
- Email: ops-team@example.com
- Phone: [emergency number]

**Update customers:**
- Status page
- Email to users
- Social media (if applicable)

---

## Hands-On Practice

### Exercise 1: Deploy to Staging (30 min)

**Objective:** Execute full deployment checklist

**Steps:**
1. Use DEPLOYMENT_CHECKLIST.md
2. Execute each verification step
3. Deploy to staging
4. Verify health checks
5. Document process

### Exercise 2: Handle Incident (20 min)

**Scenario:** "Memory usage spiking, users report slowness"

**Task:**
1. Diagnose the issue
2. Decide action (scale, restart, investigate)
3. Execute response
4. Verify recovery
5. Document findings

### Exercise 3: Rollback Practice (20 min)

**Scenario:** "New deployment broke something"

**Task:**
1. Detect issue
2. Authorize rollback
3. Execute ROLLBACK_RUNBOOK.md
4. Verify previous version working
5. Document lessons learned

---

## Key Documents

All team members must have access to:

1. **DEPLOYMENT_CHECKLIST.md** - Before any deployment
2. **DEPLOYMENT_RUNBOOK.md** - During deployment
3. **ROLLBACK_RUNBOOK.md** - For emergencies
4. **INCIDENT_RESPONSE_PLAYBOOK.md** - For incidents
5. **OPERATIONS_GUIDE.md** - Daily reference
6. **SECURITY_CHECKLIST.md** - Compliance verification

---

## Training Schedule

**Session 1: Architecture & Operations**
- Duration: 2 hours
- Topics: Modules 1, 2
- Hands-on: None

**Session 2: Deployment & Troubleshooting**
- Duration: 2.5 hours
- Topics: Modules 3, 6
- Hands-on: Exercise 1

**Session 3: Incident Response**
- Duration: 2 hours
- Topics: Module 5
- Hands-on: Exercise 2, 3

**Session 4: Team Q&A**
- Duration: 1 hour
- Review of all modules
- Answer team questions
- Address concerns

**Total Training Time:** 7.5 hours over 4 days

---

## Knowledge Assessment

**After training, team should be able to:**

- [ ] Describe the service architecture
- [ ] Execute daily startup checks
- [ ] Identify and respond to alerts
- [ ] Execute deployment checklist
- [ ] Perform rollback
- [ ] Handle common incidents
- [ ] Troubleshoot issues
- [ ] Know when to escalate

**Validation:** Quiz or practical exam

---

## Ongoing Training

**Monthly:**
- Review recent incidents
- Update runbooks if needed
- Discuss lessons learned
- Practice new scenarios

**Quarterly:**
- Full training refresher
- Review architecture changes
- Update team on new features
- Security training

**Annually:**
- Major training review
- Update all documentation
- Conduct disaster recovery drill
- Team feedback and improvements

---

## Training Sign-Off

### Attendee Information

**Name:** _________________________ **Date:** _____________

**Company:** _________________________ **Role:** _____________

### Modules Completed

- [ ] Module 1: Service Architecture
- [ ] Module 2: Daily Operations
- [ ] Module 3: Scaling & Performance
- [ ] Module 4: Deployment
- [ ] Module 5: Incident Response
- [ ] Module 6: Troubleshooting
- [ ] Module 7: Escalation & Support

### Hands-On Exercises

- [ ] Exercise 1: Deploy to Staging (Passed)
- [ ] Exercise 2: Handle Incident (Passed)
- [ ] Exercise 3: Rollback Practice (Passed)

### Trainer Sign-Off

**Trainer Name:** ________________________ **Date:** ___________

**Trainer Signature:** ________________________

### Trainee Sign-Off

**I confirm that I understand the material and can perform the operations required.**

**Trainee Signature:** ________________________ **Date:** ___________

---

**Document Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Task:** 5.8 - Deployment Runbook & Handoff
