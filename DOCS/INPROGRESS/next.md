# Next Task: 5.4 — Implement Rate Limiting

**Source:** Workplan.md
**Priority:** High (SHOULD-DO, first month)
**Phase:** 5
**Effort:** 6-8 hours
**Dependencies:** Task 5.2 (Monitoring complete) ✅
**Status:** Selected

## Description

Implement rate limiting to prevent abuse and ensure fair resource utilization. Configure rate limit rules for the `/convert` endpoint and other API routes. Support multiple rate limiting strategies with graceful degradation.

## Key Requirements

- `/convert` endpoint: 10 uploads/hour per IP
- All endpoints: 100 requests/minute per IP
- Internal IPs: Higher limits
- Graceful degradation if Redis unavailable
- Log rate limit triggers for investigation

## Acceptance Criteria

- Rate limiting is enforced on all endpoints
- Rate limits can be configured per endpoint/IP
- Graceful degradation when backing store unavailable
- Clear rate limit headers in responses
- Rate limit events are logged for audit

## Next Step

Run PLAN to generate an implementation-ready task PRD for this item.
