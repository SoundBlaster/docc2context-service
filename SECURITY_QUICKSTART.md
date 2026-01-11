# Security Quick Start Guide

## For Developers

### Running Securely in Development

```bash
# 1. Use the development environment file
cp .env.development .env

# 2. Build and run with Docker (includes security hardening)
docker-compose up --build

# 3. Test security features
python -m pytest tests/test_security.py -v
```

### Security Testing Before Committing

```bash
# Run all tests including security tests
python -m pytest tests/ -v

# Check for common security issues
bandit -r app/

# Check dependencies for vulnerabilities
safety check --file requirements.txt
```

## For DevOps/SRE

### Production Deployment Quick Steps

1. **Configure Environment**
   ```bash
   cp .env.production .env
   # Edit .env with production values:
   # - Set ALLOWED_HOSTS=["your-domain.com"]
   # - Set CORS_ORIGINS=["https://your-app.com"]
   # - Set ENVIRONMENT=production
   ```

2. **Deploy with Security Options**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Verify Security**
   ```bash
   # Check container is running as non-root
   docker exec docc2context-service whoami
   # Should output: appuser

   # Check resource limits
   docker stats docc2context-service

   # Check health
   curl https://your-domain.com/health
   ```

4. **Test Security Features**
   ```bash
   # Try Zip Slip attack (should fail)
   # Try large file (should fail at 100MB)
   # Try rapid requests (should rate limit)
   ```

## For Security Teams

### Key Security Features Implemented

✅ **Input Validation**
- File size limits (100MB default)
- ZIP structure validation
- Magic number verification
- Filename sanitization (null bytes, control chars, path traversal)
- Content-type validation

✅ **ZIP Security**
- Zip Slip/path traversal protection
- Symlink detection and blocking
- Decompression bomb protection (5:1 ratio limit, 500MB max)
- File count limits (5000 files max)
- Directory depth limits (10 levels max)
- Nested ZIP detection and blocking
- Encrypted file detection

✅ **Command Injection Prevention**
- Whitelist-based command validation
- Argument sanitization (dangerous chars blocked)
- Environment variable filtering
- Null byte detection
- Argument length limits
- Always use shell=False for subprocess

✅ **Container Security**
- Non-root user (appuser, UID 1000)
- Security options: no-new-privileges, capability dropping
- Resource limits: 2 CPU cores, 2GB memory
- Temporary filesystem: noexec, nosuid, nodev
- Health checks
- Minimal base image

✅ **API Security**
- HTTPS redirect in production
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- CORS configuration
- Rate limiting support (requires Redis)
- Request timeouts
- Request size limits

### Quick Security Audit

```bash
# 1. Check for high-severity issues
docker run --rm -v $(pwd):/app aquasec/trivy filesystem /app

# 2. Check dependencies
pip install safety
safety check --file requirements.txt

# 3. Static analysis
pip install bandit
bandit -r app/ -ll

# 4. Check secrets
pip install detect-secrets
detect-secrets scan

# 5. Run security tests
python -m pytest tests/test_security.py -v
```

### Attack Scenarios to Test

**Zip Slip:**
```python
# Create malicious ZIP with path traversal
import zipfile
with zipfile.ZipFile('attack.zip', 'w') as zf:
    zf.writestr('../../etc/passwd', 'malicious')
# Upload - should be rejected
```

**Symlink Attack:**
```bash
# Create ZIP with symlinks
ln -s /etc/passwd secret
zip -y attack.zip secret
# Upload - should be rejected
```

**Decompression Bomb:**
```python
# Create highly compressed file
import zipfile
with zipfile.ZipFile('bomb.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('bomb.txt', b'0' * (1024 * 1024 * 1024))  # 1GB
# Upload - should be rejected
```

**Command Injection:**
```bash
# Try filename with shell metacharacters
curl -F "file=@test.zip;filename=\"evil;rm -rf /.zip\"" \
  http://localhost:8000/api/v1/convert
# Should be sanitized or rejected
```

## For Incident Response

### If Compromise Suspected

1. **Isolate**
   ```bash
   # Stop the container
   docker stop docc2context-service
   
   # Preserve logs
   docker logs docc2context-service > incident-logs.txt
   ```

2. **Investigate**
   ```bash
   # Check for suspicious files in workspace
   ls -la /tmp/swift-conv-*
   
   # Check container filesystem
   docker exec docc2context-service find / -mtime -1
   
   # Review security event logs
   grep "SECURITY:" app.log
   ```

3. **Respond**
   - Review SECURITY_AUDIT.md for known vulnerabilities
   - Check if patches applied
   - Analyze attack vectors
   - Update security measures

4. **Recover**
   ```bash
   # Deploy from known-good image
   docker pull your-registry/docc2context:latest
   docker-compose up -d
   
   # Verify integrity
   python -m pytest tests/test_security.py -v
   ```

## Common Security Questions

**Q: Can uploaded files escape the workspace?**  
A: No. All paths are validated with `resolve()` and checked against the workspace directory.

**Q: Can symlinks be used to read sensitive files?**  
A: No. Symlinks are detected in ZIP metadata and on extraction, then blocked.

**Q: Can an attacker inject commands?**  
A: No. Command arguments are validated against a whitelist and dangerous characters are blocked.

**Q: Can the container run as root?**  
A: No. Dockerfile explicitly switches to non-root user (appuser).

**Q: Are there resource limits?**  
A: Yes. CPU (2 cores), memory (2GB), disk (1GB tmp), file size (100MB), decompression (500MB), file count (5000), directory depth (10 levels).

**Q: Is rate limiting enabled?**  
A: Partially. Code is present but requires Redis. Fallback to in-memory rate limiting recommended.

**Q: Are security headers present?**  
A: Yes. HSTS, CSP, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy all configured.

**Q: Can I see detailed system info via health endpoint?**  
A: By default yes, but it should be disabled in production or moved to an authenticated endpoint.

## Security Resources

- **Security Audit**: See `SECURITY_AUDIT.md` for comprehensive vulnerability analysis
- **Deployment Checklist**: See `SECURITY_CHECKLIST.md` for production deployment steps
- **Test Suite**: See `tests/test_security.py` for security test examples
- **OWASP Resources**: https://owasp.org/www-project-top-ten/
- **CWE Database**: https://cwe.mitre.org/

## Reporting Security Issues

If you discover a security vulnerability, please email security@example.com (configure this).

**Do not** open a public GitHub issue for security vulnerabilities.

## Security Updates

This service should be regularly updated:
- Dependencies: Monthly
- Security patches: As released
- Security audit: Quarterly
- Penetration testing: Annually (recommended)
