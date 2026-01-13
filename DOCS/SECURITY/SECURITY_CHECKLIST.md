# Production Security Checklist

This checklist should be completed before deploying DocC2Context Service to production.

## Pre-Deployment Security Configuration

### Environment Variables

- [ ] Set `ENVIRONMENT=production` in `.env.production`
- [ ] Configure `ALLOWED_HOSTS` with specific domains (remove `["*"]`)
- [ ] Configure `CORS_ORIGINS` with specific origins (remove `["*"]`)
- [ ] Set strong resource limits:
  - [ ] `MAX_UPLOAD_SIZE_MB=100` (or appropriate value)
  - [ ] `MAX_DECOMPRESSED_SIZE_MB=500` (or appropriate value)
  - [ ] `SUBPROCESS_TIMEOUT=60` (or appropriate value)
- [ ] Verify `LOG_LEVEL=INFO` (not DEBUG in production)

### API Documentation

- [ ] Disable Swagger UI in production (`docs_url=None` when `environment=="production"`)
- [ ] Disable ReDoc in production (`redoc_url=None` when `environment=="production"`)
- [ ] Disable OpenAPI schema endpoint in production (`openapi_url=None`)

### Docker Security

- [ ] Container runs as non-root user (verify `USER appuser` in Dockerfile)
- [ ] Resource limits configured in docker-compose.yml:
  - [ ] CPU limits (2 cores)
  - [ ] Memory limits (2GB)
- [ ] Security options enabled:
  - [ ] `no-new-privileges:true`
  - [ ] Capabilities dropped (`cap_drop: ALL`)
  - [ ] Only necessary capabilities added
- [ ] Temporary filesystem mounted with security options:
  - [ ] `noexec`
  - [ ] `nosuid`
  - [ ] `nodev`
  - [ ] Size limit (1GB)
- [ ] Health check configured and working

### Network Security

- [ ] HTTPS enforced (verify `HTTPSRedirectMiddleware` in production)
- [ ] TLS 1.2+ only (configured in reverse proxy)
- [ ] Strong cipher suites configured
- [ ] HSTS header enabled with appropriate max-age
- [ ] Valid TLS certificate installed
- [ ] Certificate auto-renewal configured

### Rate Limiting

- [ ] Redis instance deployed for rate limiting
- [ ] Redis connection secured (TLS, password)
- [ ] Rate limits configured appropriately:
  - [ ] `/api/v1/convert`: 10 requests/minute per IP (or adjusted based on usage)
  - [ ] Health checks: Reasonable limits
- [ ] Fallback rate limiting configured (in-memory if Redis unavailable)

### Reverse Proxy Configuration

- [ ] Nginx/reverse proxy deployed in front of application
- [ ] Security headers configured:
  - [ ] `Strict-Transport-Security`
  - [ ] `X-Frame-Options: DENY`
  - [ ] `X-Content-Type-Options: nosniff`
  - [ ] `X-XSS-Protection: 1; mode=block`
  - [ ] `Referrer-Policy: strict-origin-when-cross-origin`
  - [ ] `Content-Security-Policy` (appropriate for your use case)
- [ ] Request size limits enforced (`client_max_body_size 100M`)
- [ ] Timeouts configured:
  - [ ] `proxy_connect_timeout` (10s)
  - [ ] `proxy_read_timeout` (120s)
  - [ ] `proxy_send_timeout` (120s)
- [ ] Rate limiting configured at proxy level
- [ ] Connection limits per IP configured

### File System Security

- [ ] Workspace base path has restrictive permissions (0o700)
- [ ] Workspace cleanup job configured (remove old workspaces)
- [ ] Disk space monitoring enabled
- [ ] Inode usage monitoring enabled

### Dependency Security

- [ ] All dependencies pinned to specific versions
- [ ] Dependency hashes verified (`pip-compile --generate-hashes`)
- [ ] Vulnerability scanning enabled in CI/CD
- [ ] Regular dependency updates scheduled
- [ ] Security advisories monitored

### Logging & Monitoring

- [ ] Structured logging configured
- [ ] Security events logged to separate stream
- [ ] Log aggregation service configured (e.g., ELK, Splunk)
- [ ] Log retention policy defined
- [ ] Sensitive data not logged (paths, filenames sanitized)
- [ ] Monitoring dashboards created:
  - [ ] Request rate
  - [ ] Error rate
  - [ ] Response time
  - [ ] Resource usage (CPU, memory, disk)
  - [ ] Security events
- [ ] Alerts configured:
  - [ ] High error rate
  - [ ] Security event spike
  - [ ] Resource exhaustion
  - [ ] Failed health checks
  - [ ] Slow response times

### Access Control

- [ ] Administrative endpoints protected (if any)
- [ ] Authentication implemented (if required)
- [ ] API keys configured (if required)
- [ ] Role-based access control (if required)

### Secrets Management

- [ ] No secrets in environment files committed to git
- [ ] Secrets managed via secret management service (e.g., Vault, AWS Secrets Manager)
- [ ] Database credentials secured (if applicable)
- [ ] API keys secured
- [ ] TLS certificates/keys secured

### Container Registry

- [ ] Docker images scanned for vulnerabilities
- [ ] Image signing enabled
- [ ] Private container registry used
- [ ] Image pull secrets configured
- [ ] Old image versions cleaned up regularly

### CI/CD Security

- [ ] Branch protection enabled on main branch
- [ ] Required reviews for PRs
- [ ] Secrets scanning enabled
- [ ] SAST (Static Application Security Testing) enabled
- [ ] SCA (Software Composition Analysis) enabled
- [ ] Container scanning enabled
- [ ] Signed commits enforced (recommended)
- [ ] CI/CD secrets properly managed

### Backup & Recovery

- [ ] Backup strategy defined (if applicable)
- [ ] Recovery procedures documented
- [ ] Disaster recovery plan created
- [ ] Regular backup testing scheduled

### Compliance & Auditing

- [ ] Security audit completed (see SECURITY_AUDIT.md)
- [ ] Penetration testing completed (recommended)
- [ ] Compliance requirements verified (SOC 2, GDPR, etc.)
- [ ] Security incident response plan created
- [ ] Runbook created for common security scenarios

## Post-Deployment Verification

### Smoke Tests

- [ ] Application starts successfully
- [ ] Health check endpoint returns 200
- [ ] Can upload and convert valid DocC archive
- [ ] Invalid uploads properly rejected
- [ ] HTTPS redirect working
- [ ] Security headers present in responses
- [ ] Rate limiting working
- [ ] Logs being generated and aggregated

### Security Tests

- [ ] Attempt Zip Slip attack (should be blocked)
- [ ] Attempt symlink attack (should be blocked)
- [ ] Attempt command injection (should be blocked)
- [ ] Upload decompression bomb (should be blocked)
- [ ] Upload file over size limit (should be blocked)
- [ ] Rapid requests trigger rate limiting
- [ ] Invalid file types rejected
- [ ] Path traversal attempts blocked

### Performance Tests

- [ ] Load test with expected traffic
- [ ] Verify resource limits honored
- [ ] Check response times under load
- [ ] Verify graceful degradation under stress

### Monitoring Verification

- [ ] Metrics being collected
- [ ] Dashboards showing data
- [ ] Test alerts triggering correctly
- [ ] Logs searchable in log aggregation system

## Ongoing Security Maintenance

### Daily/Weekly

- [ ] Review security event logs
- [ ] Check error rates
- [ ] Verify backup success (if applicable)
- [ ] Monitor disk usage

### Monthly

- [ ] Review and update dependencies
- [ ] Review access logs for anomalies
- [ ] Test disaster recovery procedures
- [ ] Review and update firewall rules

### Quarterly

- [ ] Security audit review
- [ ] Update security checklist
- [ ] Review and test incident response plan
- [ ] Penetration testing (recommended)
- [ ] Dependency vulnerability scan
- [ ] Review and rotate secrets (API keys, etc.)

### Annually

- [ ] Full security audit
- [ ] Professional penetration test
- [ ] Update threat model
- [ ] Review and update security policies
- [ ] Security training for team

## Security Contacts

- [ ] Security incident contact defined
- [ ] Security escalation path documented
- [ ] Vulnerability disclosure policy published
- [ ] Security email/contact form configured

## Documentation

- [ ] Security architecture documented
- [ ] Deployment procedures documented
- [ ] Security runbook created
- [ ] Known limitations documented
- [ ] Security best practices shared with team

---

**Sign-off**

- [ ] Security engineer approval: _________________ Date: _______
- [ ] DevOps approval: _________________ Date: _______
- [ ] Product owner approval: _________________ Date: _______

**Notes:**

_Use this space to document exceptions, deviations, or additional security measures implemented._

