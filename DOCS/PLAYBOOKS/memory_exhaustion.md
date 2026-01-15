# Alert Playbook: High Memory Usage

**Alert:** `HighMemoryUsage`
**Severity:** CRITICAL
**Threshold:** Memory usage > 1800MB (90% of 2GB limit)

## What This Means

Container memory usage is critical. Next large operation will trigger OOM kill.

## Typical Causes

1. **Large ZIP extraction** - Legitimate but memory intensive
2. **Concurrent conversions** - Multiple uploads at same time
3. **Memory leak** - Bug in code
4. **Insufficient limits** - 2GB too small for workload

## Response Steps

1. **Check current usage:**
   ```bash
   docker stats docc2context
   ```

2. **Check for stuck conversions:**
   ```bash
   docker exec docc2context ps aux | grep swift
   ```

3. **Monitor over next 10 minutes:**
   - If drops back down: OK, was legitimate
   - If stays high: Need to scale

4. **To increase limits:**
   - Update docker-compose.yml: `memory: "4G"`
   - Restart: `docker-compose up -d docc2context`

5. **If memory leak suspected:**
   - Check app logs for memory growth patterns
   - Restart service to recover memory
   - Schedule code review

## Escalation

- If causes OOM kill: IMMEDIATE - scale or fix
- If repeatedly near limit: Scale container
- If suspected leak: Schedule debugging session

## Links

- Docker stats: `docker stats docc2context`
- Config: `docker-compose.yml`
