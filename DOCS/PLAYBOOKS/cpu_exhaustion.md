# Alert Playbook: High CPU Usage

**Alert:** `HighCPUUsage`
**Severity:** WARNING
**Threshold:** CPU usage > 80% for 5+ minutes

## What This Means

Service is using high CPU. May be processing intensive workload or have efficiency issue.

## Typical Causes

1. **Concurrent conversions** - Multiple ZIP extractions/conversions running
2. **Swift CLI processing** - Legitimate but CPU intensive
3. **Inefficient code** - Possible performance regression

## Response Steps

1. **Check CPU and process breakdown:**
   ```bash
   docker stats docc2context
   docker top docc2context
   ```

2. **Is this expected?**
   - During high-traffic periods: Normal
   - Sustained over time: May need scale

3. **Check for stuck processes:**
   ```bash
   # Verify conversion timeout is working
   docker logs docc2context | grep timeout
   ```

4. **If temporary: No action needed**

5. **If sustained: Scale horizontally**
   - Add more container instances
   - Load balance requests

## When to Escalate

- If causing slow response times → scale
- If sustained at high load → plan capacity
- If CPU usage seems wrong → profile code

## Links

- Metrics: http://localhost:9090
