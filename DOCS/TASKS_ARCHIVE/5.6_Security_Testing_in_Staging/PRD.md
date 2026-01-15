# Task 5.6: Security Testing in Staging

**Task ID:** 5.6
**Title:** Security Testing in Staging
**Priority:** Critical (Blocking Production)
**Phase:** 5
**Effort:** 8-12 hours
**Status:** In Planning

## Dependencies

- ✅ Task 5.1: Disable Swagger and Configure CORS
- ✅ Task 5.2: Configure Monitoring & Alerting
- ✅ Task 5.3: Set Up Log Aggregation

## Objective

Execute comprehensive security testing in the staging environment to validate that all security measures implemented in Tasks 5.1, 5.2, and 5.3 are functioning correctly. This is a blocking task for production deployment.

## Scope

This task covers:
1. Running all 25 security unit tests from `tests/test_security.py`
2. Testing resource limits under load (file size, batch uploads, memory/CPU)
3. Manually verifying all items in `SECURITY_CHECKLIST.md`
4. Conducting an internal security review with team member
5. Documenting all test results and addressing failures

## Implementation Plan

### Phase 1: Verify Staging Environment Setup

**Subtask 1.1:** Verify staging Docker environment
- [ ] Ensure staging environment has all required services running (app, redis, prometheus, alertmanager, elasticsearch, logstash, kibana)
- [ ] Verify `.env.staging` is correctly configured
- [ ] Run `docker-compose -f docker-compose.yml --profile staging up -d`
- [ ] Wait for all services to be healthy

**Acceptance Criteria:**
- All containers are running and healthy
- Health check endpoint returns 200
- Logs are flowing to ELK stack

---

### Phase 2: Execute Security Test Suite (25 Tests)

**Subtask 2.1:** Run all security tests in staging
- [ ] Execute: `pytest tests/test_security.py -v --tb=short`
- [ ] Capture complete test output
- [ ] Document any failures with full stack traces
- [ ] Expected: All 25 tests pass

**Tests to verify:** (From `tests/test_security.py`)
1. Magic number validation (non-ZIP rejection)
2. File size limit validation (>100MB rejection)
3. Zip bomb protection (decompression limits)
4. Path traversal prevention
5. Secure filename sanitization
6. CORS configuration validation
7. Swagger disabled in production config
8. HTTPS redirect (if applicable)
9. Security header validation
10. Rate limiting functionality
11. Request timeout enforcement
12. Subprocess timeout enforcement
13. Workspace cleanup validation
14. Error handling for malformed files
15. CLI stderr capture in error responses
16. Invalid content-type rejection
17. Empty file handling
18. Concurrent upload handling
19. Workspace isolation verification
20. Permission verification (0o700)
21. Environment variable validation
22. Secret non-exposure in responses
23. Request ID tracking in logs
24. Structured JSON logging validation
25. Error response format validation

**Acceptance Criteria:**
- All 25 tests pass without modification
- Test output logged to file for documentation
- Any failures immediately escalated (don't continue if tests fail)

---

### Phase 3: Resource Limit Testing Under Load

**Subtask 3.1:** Test file size limits
- [ ] Upload file exactly at 100MB limit → should succeed
- [ ] Upload file at 100MB + 1 byte → should return 413 error
- [ ] Verify error message is clear and helpful
- [ ] Check response time (should be <5s for rejection)

**Subtask 3.2:** Test batch uploads
- [ ] Simulate 10 concurrent uploads of valid files
- [ ] Monitor memory usage during concurrent uploads
- [ ] Verify all uploads complete successfully
- [ ] Verify workspace cleanup occurs for all

**Subtask 3.3:** Monitor resource usage during testing
- [ ] During uploads, monitor:
  - Docker container memory usage (should stay <1.5GB)
  - CPU usage (should stay <80%)
  - Disk space (should not run low)
  - Network bandwidth
- [ ] Use: `docker stats` command
- [ ] Log findings to `TESTING_RESULTS.md`

**Acceptance Criteria:**
- File size limits enforced correctly (both sides of boundary)
- Concurrent uploads don't cause resource exhaustion
- Memory stays within configured limits
- CPU usage remains reasonable
- No orphaned workspaces after uploads

---

### Phase 4: SECURITY_CHECKLIST.md Manual Verification

**Subtask 4.1:** Verify Pre-Deployment Security Configuration
- [ ] Check `ENVIRONMENT=production` setting in staging
- [ ] Verify `ALLOWED_HOSTS` is restricted (not wildcard)
- [ ] Verify `CORS_ORIGINS` is restricted (not wildcard)
- [ ] Verify resource limits are set:
  - `MAX_UPLOAD_SIZE_MB=100`
  - `MAX_DECOMPRESSED_SIZE_MB=500`
  - `SUBPROCESS_TIMEOUT=60`
- [ ] Verify `LOG_LEVEL=INFO` (not DEBUG)

**Subtask 4.2:** Verify API Documentation Security
- [ ] Test: `curl http://staging-app:8000/docs` → should return 404
- [ ] Test: `curl http://staging-app:8000/redoc` → should return 404
- [ ] Test: `curl http://staging-app:8000/openapi.json` → should return 404

**Subtask 4.3:** Verify Docker Security
- [ ] Check Dockerfile has `USER appuser` (non-root)
- [ ] Verify resource limits in docker-compose.yml:
  - CPU: 2 cores
  - Memory: 2GB
- [ ] Verify security options:
  - `no-new-privileges:true`
  - Capabilities dropped
- [ ] Verify tmpfs has security flags

**Subtask 4.4:** Verify Network Security (if HTTPS available)
- [ ] If HTTPS configured:
  - [ ] Test TLS 1.2+ only
  - [ ] Verify HSTS header present
  - [ ] Verify strong cipher suites
  - [ ] Verify valid certificate

**Subtask 4.5:** Verify Rate Limiting (if Redis available)
- [ ] If Rate Limiting task completed:
  - [ ] Verify Redis is running and accessible
  - [ ] Make >10 uploads in 1 hour → should get rate limit error
  - [ ] Verify rate limit headers in response

**Subtask 4.6:** Verify Logging & Monitoring
- [ ] Check Prometheus metrics are being collected:
  - [ ] `curl http://prometheus:9090/api/v1/query?query=http_requests_total` returns data
- [ ] Check Elasticsearch is receiving logs:
  - [ ] `curl http://elasticsearch:9200/_count` shows documents
- [ ] Check Kibana dashboards are accessible:
  - [ ] `curl http://kibana:5601` returns 200

**Subtask 4.7:** Verify Access Control
- [ ] No unauthenticated admin endpoints
- [ ] Health check accessible from monitoring
- [ ] API endpoints respond with appropriate status codes

**Subtask 4.8:** Verify Secrets Management
- [ ] Scan: `grep -r "password\|secret\|key\|token" .env.staging | grep -v "REDIS_PASSWORD"` (should only see expected entries)
- [ ] Verify no secrets leaked in error responses
- [ ] Verify no secrets in request logs

**Acceptance Criteria for 4.1-4.8:**
- All checkbox items verified as working
- Any deviations documented with mitigation
- No critical issues found (or documented for Task 5.8)

---

### Phase 5: Security Smoke Tests

**Subtask 5.1:** Test basic file conversion workflow
- [ ] Upload valid DocC archive → should succeed
- [ ] Download converted output → should be valid ZIP
- [ ] Verify output contains markdown files
- [ ] Verify error handling on malformed inputs

**Subtask 5.2:** Test attack scenarios (from SECURITY_CHECKLIST.md Post-Deployment Verification)
- [ ] Zip Slip attack: Upload specially crafted ZIP with `../` paths → should be blocked
- [ ] Symlink attack: Upload ZIP with symlinks → should be blocked
- [ ] Command injection: Upload file with shell metacharacters → should be blocked
- [ ] Decompression bomb: Upload compressed bomb file → should be blocked
- [ ] Oversized file: Upload file >100MB → should be rejected
- [ ] Invalid file type: Upload PNG pretending to be ZIP → should be rejected
- [ ] Path traversal: Try accessing `/etc/passwd` through API → should fail

**Subtask 5.3:** Verify monitoring and alerting
- [ ] Generate test error condition (invalid upload)
- [ ] Verify error is logged to ELK stack
- [ ] Verify Prometheus metrics increase
- [ ] Check Kibana dashboards show the event

**Acceptance Criteria:**
- Basic workflow functions correctly
- All attack scenarios are properly blocked
- Monitoring/alerting detects and logs events
- No unexpected error messages or crashes

---

### Phase 6: Internal Security Review

**Subtask 6.1:** Peer review with another team member
- [ ] Schedule review session with team member
- [ ] Review all findings from Phases 1-5
- [ ] Check for configuration errors or oversights
- [ ] Verify nothing is unintentionally exposed
- [ ] Document reviewer's sign-off

**Subtask 6.2:** Address any findings
- [ ] If issues found, categorize as:
  - Blocker: Must fix before production
  - Major: Should fix before production
  - Minor: Can fix post-launch
- [ ] Document all issues and their status
- [ ] Create follow-up tasks if needed

**Acceptance Criteria:**
- Internal review is complete
- All blockers are resolved
- Major issues are documented with mitigation
- Reviewer sign-off obtained

---

### Phase 7: Documentation & Sign-Off

**Subtask 7.1:** Create testing results document
- [ ] Create `TESTING_RESULTS_PHASE_5.6.md` with:
  - All test results (pass/fail)
  - Resource monitoring data
  - Security checklist verification results
  - Findings and mitigations
  - Reviewer names and dates

**Subtask 7.2:** Mark Task 5.6 as complete
- [ ] Update `Workplan.md` to mark Task 5.6 as ✅ COMPLETED
- [ ] Note completion date
- [ ] Add reference to testing results document

**Subtask 7.3:** Verify no blockers remain
- [ ] Review all failures and mitigations
- [ ] Confirm none are blocking production
- [ ] If blockers exist, add them to blocking issues list

**Acceptance Criteria:**
- All test results documented
- Workplan updated
- No blocking issues remain
- Results available for Task 5.8 (Deployment Runbook)

---

## Definition of Done

**Task 5.6 is complete when:**

1. ✅ All 25 security tests pass in staging environment
2. ✅ Resource limits tested and verified working
3. ✅ All SECURITY_CHECKLIST.md items manually verified
4. ✅ Internal security review conducted and signed-off
5. ✅ Testing results documented in `TESTING_RESULTS_PHASE_5.6.md`
6. ✅ No blockers found (or documented and mitigated)
7. ✅ Workplan.md updated with completion status
8. ✅ Ready for Task 5.8 (Deployment Runbook)

## Verification Commands

Run these commands in staging environment:

```bash
# 1. Run security test suite
pytest tests/test_security.py -v --tb=short | tee STAGING_TEST_RESULTS.log

# 2. Run code quality checks (if not already passing)
ruff check app/ tests/
black --check app/ tests/
mypy app/ --ignore-missing-imports

# 3. Check health endpoint
curl -s http://localhost:8000/health | jq .

# 4. Verify Swagger is disabled
curl -s http://localhost:8000/docs -w "%{http_code}\n" -o /dev/null
# Should return 404

# 5. Verify CORS is restricted
curl -s -H "Origin: http://unauthorized.com" http://localhost:8000/health | grep -i access-control
# Should show restricted CORS headers

# 6. Check Prometheus metrics
curl -s http://localhost:9090/api/v1/query?query=up | jq .

# 7. Check Elasticsearch docs
curl -s http://localhost:9200/_count | jq .

# 8. Verify logs in Kibana (manual step)
# Open http://localhost:5601 and search for test events

# 9. Document resource usage during tests
docker stats --no-stream app elasticsearch redis prometheus
```

## Testing Checklist

Use this checklist to track Phase execution:

### Phase 1: Environment Setup
- [ ] All services running
- [ ] Health check returns 200
- [ ] Logs flowing to ELK

### Phase 2: Security Test Suite
- [ ] All 25 tests pass
- [ ] Test output captured
- [ ] No failures

### Phase 3: Resource Limits
- [ ] File size limits verified
- [ ] Batch uploads work
- [ ] Resource usage monitored
- [ ] Findings documented

### Phase 4: Checklist Verification
- [ ] All 8 subtasks completed
- [ ] All checklist items verified
- [ ] Issues documented

### Phase 5: Smoke Tests
- [ ] Basic workflow works
- [ ] Attack scenarios blocked
- [ ] Monitoring/alerting functional

### Phase 6: Internal Review
- [ ] Peer review completed
- [ ] Sign-off obtained
- [ ] Issues addressed

### Phase 7: Documentation
- [ ] Results documented
- [ ] Workplan updated
- [ ] No blockers remain

## Success Criteria

Task 5.6 is successful if:
- All 25 security tests pass without modification
- Resource limits work as designed
- All SECURITY_CHECKLIST.md items verified
- Internal review completed and signed-off
- Testing results fully documented
- No critical issues found
- Team confidence in security posture is high

## Notes

- This task is **blocking for production deployment**
- Any test failures must be addressed before proceeding
- Document all findings thoroughly
- Internal review is mandatory (not optional)
- Results feed into Task 5.8 (Deployment Runbook)

---

**Created:** 2026-01-13
**Target Completion:** 2026-01-14 (end of day)

**Archived:** 2026-01-13
