# Alert Playbook: Service Down

**Alert:** `ServiceDown`
**Severity:** CRITICAL
**Condition:** Service not responding to health checks for 1+ minute

## What This Means

Service is completely unavailable. All user requests will fail. This is a production outage.

## Response Steps

### IMMEDIATE (First 2 minutes)

1. **Verify service status:**
   ```bash
   docker-compose ps docc2context
   curl http://localhost:8000/health
   ```

2. **If not running, restart:**
   ```bash
   docker-compose restart docc2context
   docker logs docc2context
   ```

3. **If restart fixes it: Done**

### If Restart Doesn't Help (3-5 minutes)

1. **Check for crash logs:**
   ```bash
   docker logs docc2context | tail -100
   ```

2. **Check disk/memory:**
   ```bash
   docker stats
   df -h /
   ```

3. **Check if dependencies are running:**
   ```bash
   docker-compose ps  # Verify redis, swift, etc.
   ```

4. **Restart all services:**
   ```bash
   docker-compose restart
   docker-compose ps
   ```

### Escalation Path

- **< 5 min down:** Restart services, investigate in background
- **5-15 min down:** Page on-call engineer immediately
- **> 15 min down:** Declare incident, full team response

## Communication

1. Notify #incidents channel: "DocC2Context service is DOWN"
2. Provide status updates every 5 minutes
3. Notify when recovered: "Service RECOVERED at [time]"

## Post-Incident

1. Collect logs: `docker logs docc2context > /tmp/incident.log`
2. Check system resources when outage occurred
3. Schedule root cause analysis meeting
4. Update playbook if needed

## Emergency Contacts

- On-Call Engineer: [configured in your system]
- Team Slack: #docc2context
- Status Page: [if applicable]
