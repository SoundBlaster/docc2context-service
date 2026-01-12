# Alert Playbook: High Error Rate

**Alert:** `HighErrorRate`
**Severity:** CRITICAL
**Threshold:** HTTP 5xx error rate > 10% over 5 minutes

## What This Means

The service is returning server errors (500-599) at a rate exceeding 10%. This indicates a serious problem that requires immediate investigation.

## Typical Causes

1. **Service crash or panic** - Most common
2. **Downstream service unavailable** - Can't reach Swift CLI or other dependencies
3. **Configuration error** - Bad environment variables
4. **Memory/resource exhaustion** - Out of memory or file descriptors
5. **Unhandled exception** - Bug in code

## Response Steps

1. **Check if service is running:**
   ```bash
   docker-compose ps docc2context
   docker logs docc2context | tail -50
   ```

2. **Check error patterns in logs:**
   ```bash
   docker logs docc2context | grep -i error | tail -20
   ```

3. **Monitor resource usage:**
   ```bash
   docker stats docc2context
   ```

4. **If crashed, restart:**
   ```bash
   docker-compose restart docc2context
   ```

5. **If memory issue, scale:**
   ```bash
   # Update docker-compose.yml memory: "4G"
   docker-compose up -d docc2context
   ```

6. **If config error, fix and redeploy:**
   - Check SECURITY_CHECKLIST.md for required config
   - Verify .env file
   - Restart service

## Escalation

- **If unresolved after 5 minutes:** Page on-call engineer
- **If causing widespread outages:** Declare incident
- **If repeatedly happening:** Schedule post-mortem

## Links

- Logs: `/var/log/docc2context/`
- Monitoring: http://localhost:9090
- Alerts: http://localhost:9093
