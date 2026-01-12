# Alert Playbook: High Extraction Failure Rate

**Alert:** `HighExtractionFailureRate`
**Severity:** WARNING
**Threshold:** ZIP extraction failures > 20% over 5 minutes

## What This Means

More than 20% of ZIP extraction attempts are failing. This suggests either invalid user uploads or a problem with the extraction logic.

## Typical Causes

1. **Malformed ZIP files** - Users uploading bad archives
2. **Zip bomb protection triggered** - Legitimate files hitting limits
3. **Resource exhaustion** - Disk or memory full
4. **Symlink or path traversal attempts** - Security validation rejecting files

## Response Steps

1. **Check failure patterns:**
   ```bash
   docker logs docc2context | grep -i "extraction\|failed" | tail -30
   ```

2. **Check which error type:**
   - Validation error? → Check file size/count limits
   - Extraction error? → Check disk space
   - Security error? → Check symlink/path validation

3. **If disk full:**
   ```bash
   docker exec docc2context df -h
   docker exec docc2context rm -rf /tmp/swift-conv-*
   ```

4. **If resource issue:**
   - Scale up container limits
   - Check docker-compose.yml memory/cpu
   - Increase MAX_ZIP_SIZE if appropriate

5. **If legitimate files being rejected:**
   - Review validation rules in SECURITY_CHECKLIST.md
   - Check if limits are too strict

## When to Escalate

- If extraction failures block legitimate users → escalate to team
- If limits need adjustment → schedule review
- If persistent → escalate to security team

## Links

- Logs: `/var/log/docc2context/`
- Config: `SECURITY_CHECKLIST.md`
