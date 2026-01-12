# Workplan: Swift DocC to Markdown Web Converter (MVP)

This workplan breaks down the implementation roadmap from the PRD into actionable tasks with clear acceptance criteria and dependencies.

## Phase 1: The "Engine" (Backend)

### Task 1.1: Docker Environment Setup
**Priority:** Critical  
**Dependencies:** None  
**References:** PRD Section 5, Risk Mitigation Section 6

**Subtasks:**
1. Create `Dockerfile` with multi-stage build:
   - Base stage: Install Swift runtime and required shared libraries (libicu, etc.)
   - Python stage: Install Python 3.10 and FastAPI dependencies
   - Final stage: Combine Swift runtime + Python environment
2. Create `.dockerignore` to exclude unnecessary files
3. Create `docker-compose.yml` for local development (optional)
4. Test Docker build and verify Swift binary is accessible

**Acceptance Criteria:**
- [x] Docker image builds successfully
- [x] Swift runtime libraries are present (Swift binary will be added in later task)
- [x] Python 3.10 and FastAPI are installed
- [x] All required shared libraries are present
- [x] Image size is optimized (multi-stage build, 856MB)

**Estimated Time:** 4-6 hours

---

### Task 1.2: Deploy the CLI App from Source Code
**Priority:** Critical  
**Dependencies:** Task 1.1  
**References:** https://github.com/SoundBlaster/docc2context

**Subtasks:**
1. Clone or download the docc2context source code from GitHub
2. Build the Swift CLI binary from source:
   - Install Swift build tools in Docker image (if not already present)
   - Compile the CLI using Swift Package Manager
   - Ensure binary is built for Linux (if deploying on Linux)
3. Integrate the binary into the Docker image:
   - Copy the compiled binary to a standard location (e.g., `/usr/local/bin/docc2context`)
   - Ensure binary has execute permissions
   - Verify binary is accessible in PATH
4. Test binary execution:
   - Verify `docc2context --version` or similar command works
   - Ensure binary can be executed from Python subprocess

**Acceptance Criteria:**
- [x] CLI source code is accessible in the build context
- [x] Swift CLI binary is successfully compiled
- [x] Binary is installed in Docker image at a standard location
- [x] Binary is executable and accessible from Python subprocess
- [x] Binary responds to basic commands (version check, help, etc.)

**Estimated Time:** 4-6 hours

---

### Task 1.3: Core FastAPI Application Structure
**Priority:** Critical  
**Dependencies:** Task 1.2  
**References:** PRD Section 2, Section 4

**Subtasks:**
1. Initialize FastAPI application with proper project structure:
   - `app/main.py` - Application entry point
   - `app/api/v1/` - API routes
   - `app/core/` - Core utilities (config, logging)
   - `app/services/` - Business logic
2. Implement structured JSON logging with request IDs
3. Create configuration management (environment variables)
4. Set up CORS middleware for frontend integration

**Acceptance Criteria:**
- [x] FastAPI app starts successfully
- [x] Structured logging outputs JSON with request IDs
- [x] Configuration is loaded from environment variables
- [x] CORS is properly configured

**Estimated Time:** 3-4 hours

---

### Task 1.4: File Upload & Validation Service
**Priority:** Critical  
**Dependencies:** Task 1.3  
**References:** PRD FR1, FR2, Section 2

**Subtasks:**
1. Implement file upload endpoint `/api/v1/convert`:
   - Accept `multipart/form-data` with `file` field
   - Enforce 100MB upload limit (FR2)
2. Implement magic number validation (FR1):
   - Check ZIP file header (PK\x03\x04 or PK\x05\x06)
   - Reject non-ZIP files before processing
3. Implement zip bomb protection (FR2):
   - Track decompression size during extraction
   - Limit to 5x upload size or 500MB hard cap
   - Use secure extraction method
4. Implement path sanitization using `werkzeug.utils.secure_filename` or equivalent

**Acceptance Criteria:**
- [x] Endpoint accepts file uploads
- [x] Magic number validation rejects non-ZIP files (400 error)
- [x] Files >100MB are rejected (413 error)
- [x] Zip bomb protection prevents excessive decompression
- [x] File paths are sanitized before use

**Estimated Time:** 6-8 hours

---

### Task 1.5: Workspace Management Service
**Priority:** Critical  
**Dependencies:** Task 1.4  
**References:** PRD Section 2, Section 6

**Subtasks:**
1. Create workspace isolation service:
   - Generate ephemeral directories using `uuid4`
   - Base path: `/tmp/swift-conv-{uuid}/`
   - Ensure directory permissions are secure
2. Implement workspace cleanup:
   - Delete workspace after request completion (success or failure)
   - Use try/finally or context manager pattern
3. Create startup cleanup script:
   - Clear orphaned `/tmp/swift-conv-*` directories on boot
   - Can be cron job or container entrypoint script

**Acceptance Criteria:**
- [x] Unique workspace directories are created per request
- [x] Workspaces are deleted after request completion
- [x] Startup script cleans orphaned directories
- [x] Directory permissions are secure (700 or similar)

**Estimated Time:** 3-4 hours

---

### Task 1.6: SubprocessManager for Swift CLI Execution
**Priority:** Critical  
**Dependencies:** Task 1.5  
**References:** PRD FR4, Section 2

**Subtasks:**
1. Create `SubprocessManager` class:
   - Execute Swift binary via subprocess
   - Set timeout to 60 seconds (NFR)
   - Use `check=True` to raise on non-zero exit codes
   - Capture stdout and stderr separately
2. Implement exit code mapping:
   - Map Swift CLI exit codes to HTTP status codes
   - Provide meaningful error messages from stderr
3. Add resource monitoring:
   - Track execution time
   - Log resource usage

**Acceptance Criteria:**
- [x] Swift CLI is executed with 60s timeout
- [x] Non-zero exit codes raise exceptions
- [x] Stderr is captured and included in error responses
- [x] Execution time is logged
- [x] Process is killed if timeout is exceeded

**Estimated Time:** 4-5 hours

---

### Task 1.7: Conversion Pipeline & Response Streaming
**Priority:** Critical  
**Dependencies:** Task 1.6  
**References:** PRD FR3, Section 2

**Subtasks:**
1. Implement conversion pipeline:
   - Extract uploaded ZIP to workspace
   - Invoke Swift CLI on extracted archive
   - Collect generated Markdown files
2. Implement streaming response (FR3):
   - Zip the Markdown tree on-the-fly
   - Use `StreamingResponse` or `FileResponse` to avoid loading entire ZIP in RAM
   - Set appropriate headers (Content-Type, Content-Disposition)
3. Handle conversion errors:
   - Return 500 with CLI stderr in response body
   - Ensure cleanup happens even on errors

**Acceptance Criteria:**
- [x] Conversion pipeline completes successfully
- [x] Response is streamed (not buffered entirely in RAM)
- [x] Output ZIP contains Markdown files
- [x] Error responses include CLI stderr
- [x] Cleanup occurs on both success and failure

**Estimated Time:** 5-6 hours

---

### Task 1.8: Health Check Endpoint
**Priority:** Medium  
**Dependencies:** Task 1.3  
**References:** PRD Section 4

**Subtasks:**
1. Implement `GET /health` endpoint:
   - Check if Swift binary is available
   - Return `{"status": "ready", "binary_detected": true/false}`
2. Add basic system health checks (optional):
   - Disk space availability
   - Memory availability

**Acceptance Criteria:**
- [x] Endpoint returns 200 with status JSON
- [x] Binary detection works correctly
- [x] Response matches PRD specification

**Estimated Time:** 1-2 hours

---

## Phase 2: The "Portal" (Frontend)

### Task 2.1: Frontend Project Setup
**Priority:** High  
**Dependencies:** Task 1.3 (CORS configured)  
**References:** PRD Section 5

**Subtasks:**
1. Set up frontend structure:
   - Create `static/` directory in FastAPI app
   - Or create separate frontend project (if preferred)
2. Choose styling approach:
   - Option A: Tailwind CSS via CDN
   - Option B: Simple CSS file
3. Create base HTML structure:
   - `index.html` with proper meta tags
   - Responsive layout structure

**Acceptance Criteria:**
- [x] Frontend files are accessible
- [x] Styling framework is integrated
- [x] Base HTML structure is responsive

**Estimated Time:** 2-3 hours

---

### Task 2.2: Drag-and-Drop Upload Zone
**Priority:** High  
**Dependencies:** Task 2.1  
**References:** PRD Task 2.1

**Subtasks:**
1. Implement drag-and-drop zone:
   - Visual drop zone with clear boundaries
   - Handle `dragover`, `drop`, `dragleave` events
   - Prevent default browser behavior
2. Implement file input fallback:
   - Traditional file input button
   - Sync with drag-and-drop functionality
3. Add visual feedback:
   - Highlight zone on drag over
   - Show selected file name
   - Display file size

**Acceptance Criteria:**
- [x] Users can drag files onto the drop zone
- [x] Users can click to select files
- [x] Visual feedback is clear and responsive
- [x] File name and size are displayed

**Estimated Time:** 4-5 hours

---

### Task 2.3: Upload Progress & Processing States
**Priority:** High  
**Dependencies:** Task 2.2  
**References:** PRD FR5, Task 2.2

**Subtasks:**
1. Implement Fetch API with progress tracking:
   - Use `XMLHttpRequest` or Fetch with ReadableStream for upload progress
   - Display upload percentage (0-100%)
2. Implement processing state:
   - Show "Processing..." after upload completes
   - Display spinner or loading animation
   - Disable UI during processing
3. Handle response:
   - Trigger download when conversion completes
   - Show success message

**Acceptance Criteria:**
- [x] Upload progress bar shows 0-100%
- [x] Processing state is clearly indicated
- [x] Download starts automatically on success
- [x] UI is disabled during processing

**Estimated Time:** 4-5 hours

---

### Task 2.4: Error Handling UI
**Priority:** High  
**Dependencies:** Task 2.3  
**References:** PRD Task 2.3, FR5

**Subtasks:**
1. Implement error state UI:
   - Display error messages from API responses
   - Handle different error types:
     - 400: Invalid file type or corrupted ZIP
     - 413: File too large
     - 500: Server/CLI error (show stderr if available)
     - Network errors
2. Add user-friendly error messages:
   - Map technical errors to readable messages
   - Provide guidance on how to fix issues
3. Implement retry functionality:
   - Allow users to try again after errors
   - Reset UI state

**Acceptance Criteria:**
- [x] Error messages are displayed clearly
- [x] Different error types show appropriate messages
- [x] Users can retry after errors
- [x] UI resets properly after errors

**Estimated Time:** 3-4 hours

---

## Phase 3: Hardening & Testing

### Task 3.1: Security Hardening
**Priority:** High  
**Dependencies:** Task 1.7  
**References:** PRD Task 3.1, Section 3

**Subtasks:**
1. Add Nginx configuration (if using Nginx):
   - `limit_conn` to prevent connection flooding
   - `limit_req` for rate limiting
   - Request size limits
2. Implement additional security measures:
   - Request timeout middleware
   - Rate limiting at application level (if not using Nginx)
   - Input validation enhancements
3. Security headers:
   - Add security headers (CSP, X-Frame-Options, etc.)
   - Ensure HTTPS in production

**Acceptance Criteria:**
- [x] Nginx limits are configured (if applicable)
- [x] Rate limiting prevents abuse
- [x] Security headers are set
- [x] Request timeouts are enforced

**Estimated Time:** 3-4 hours

---

### Task 3.2: Unit & Integration Tests
**Priority:** High  
**Dependencies:** Task 1.7, Task 2.4  
**References:** PRD Task 3.2

**Subtasks:**
1. Set up testing framework:
   - Install pytest and required dependencies
   - Create `tests/` directory structure
   - Configure test fixtures
2. Write test cases for backend:
   - Test uploading non-ZIP file (should return 400)
   - Test uploading ZIP that isn't .doccarchive (should return 500)
   - Test file size limit (413 for >100MB)
   - Test magic number validation
   - Test zip bomb protection
   - Test CLI timeout simulation
   - Test workspace cleanup
   - Test successful conversion
3. Write test cases for frontend (optional):
   - Test drag-and-drop functionality
   - Test error handling
   - Test progress tracking

**Acceptance Criteria:**
- [x] All test cases pass
- [x] Test coverage >80% for critical paths
- [x] Tests run in CI/CD pipeline
- [x] Edge cases are covered

**Estimated Time:** 8-10 hours

---

### Task 3.3: Documentation & Deployment [INPROGRESS]
**Priority:** Medium
**Dependencies:** All previous tasks
**References:** PRD Section 1

**Subtasks:**
1. Create README.md:
   - Project overview
   - Setup instructions
   - API documentation
   - Deployment guide
2. Create API documentation:
   - OpenAPI/Swagger documentation (FastAPI auto-generates)
   - Example requests/responses
3. Deployment preparation:
   - Create production Dockerfile (if different from dev)
   - Environment variable documentation
   - Deployment checklist

**Acceptance Criteria:**
- [x] README is comprehensive and clear
- [x] API documentation is accessible
- [x] Deployment guide is complete
- [x] Environment variables are documented

**Estimated Time:** 3-4 hours

---

## Phase 4: Quality Gates & Validation

### Task 4.1: Code Quality Gates
**Priority:** High
**Dependencies:** Task 3.2
**References:** PRD Section 4, Best Practices

**Subtasks:**
1. Set up code quality tools:
   - Install and configure linters (ruff, flake8, or pylint)
   - Install and configure formatters (black, isort)
   - Install and configure type checkers (mypy)
2. Create code quality validation script:
   - Run linters on all Python code
   - Run formatters in check mode
   - Run type checkers
   - Enforce minimum quality thresholds
3. Integrate with CI/CD:
   - Add code quality checks to GitHub Actions workflow
   - Fail builds on quality violations
   - Generate quality reports
4. Create pre-commit hooks:
   - Auto-format code on commit
   - Run quick linting checks
   - Prevent commits with obvious issues

**Acceptance Criteria:**
- [x] Code quality tools are installed and configured
- [x] Validation script enforces quality standards
- [x] CI/CD pipeline includes quality checks
- [x] Pre-commit hooks are available
- [x] All existing code passes quality checks
- [x] Documentation explains quality standards

**Estimated Time:** 4-6 hours

---

### Task 4.2: Environment Quality Gates
**Priority:** High
**Dependencies:** Task 3.3
**References:** PRD Section 6, CONFIGURATION.md

**Subtasks:**
1. Create environment validation script:
   - Verify all required environment variables are set
   - Validate environment variable values and types
   - Check for common misconfigurations
   - Verify file paths and permissions
2. Implement environment-specific validations:
   - Production: Enforce security settings (no DEBUG, CORS restrictions)
   - Staging: Verify staging-specific configuration
   - Development: Ensure development tools are available
3. Add environment health checks:
   - Verify Docker daemon is running
   - Check available disk space
   - Verify Swift CLI is accessible
   - Test network connectivity (if required)
4. Create environment setup automation:
   - Script to initialize development environment
   - Script to validate production readiness
   - Templates for different environments

**Acceptance Criteria:**
- [x] Environment validation script checks all variables
- [x] Environment-specific validations work correctly
- [x] Health checks detect common issues
- [x] Setup automation simplifies environment configuration
- [x] Validation runs in CI/CD pipeline
- [x] Documentation explains validation process

**Estimated Time:** 5-7 hours

---

### Task 4.3: Deployment Quality Gates
**Priority:** High
**Dependencies:** Task 3.3
**References:** DEPLOYMENT.md, Section 6

**Subtasks:**
1. Create deployment validation script:
   - Verify Docker image builds successfully
   - Test container startup and shutdown
   - Verify all endpoints are accessible
   - Check health endpoint returns expected response
2. Implement deployment smoke tests:
   - Test basic file conversion workflow
   - Verify API documentation is accessible
   - Test error handling scenarios
   - Verify workspace cleanup works
3. Add deployment security checks:
   - Scan Docker image for vulnerabilities
   - Verify no secrets in image layers
   - Check file permissions in container
   - Validate security headers
4. Create deployment rollback procedure:
   - Document rollback steps
   - Create rollback automation script
   - Test rollback scenarios

**Acceptance Criteria:**
- [ ] Deployment validation script checks all critical paths
- [ ] Smoke tests verify basic functionality
- [ ] Security checks pass for production images
- [ ] Rollback procedure is documented and tested
- [ ] Validation runs before deployment
- [ ] Failed validations prevent deployment

**Estimated Time:** 6-8 hours

---

### Task 4.4: Architecture Quality Gates
**Priority:** Medium
**Dependencies:** All previous tasks
**References:** PRD Section 2, Architecture Decisions

**Subtasks:**
1. Document architecture decisions:
   - Create Architecture Decision Records (ADRs)
   - Document key design patterns used
   - Explain component interactions
   - Document scalability considerations
2. Create architecture validation script:
   - Verify project structure follows conventions
   - Check for circular dependencies
   - Validate layer separation (API, services, core)
   - Ensure proper error handling patterns
3. Implement dependency analysis:
   - Generate dependency graph
   - Identify potential issues (tight coupling, etc.)
   - Verify dependencies are up-to-date
   - Check for security vulnerabilities in dependencies
4. Create performance benchmarks:
   - Benchmark API endpoint response times
   - Benchmark conversion throughput
   - Test concurrent request handling
   - Document performance baselines

**Acceptance Criteria:**
- [ ] Architecture is documented with ADRs
- [ ] Architecture validation script enforces structure
- [ ] Dependency analysis identifies issues
- [ ] Performance benchmarks establish baselines
- [ ] Documentation explains architecture decisions
- [ ] Validation runs in CI/CD pipeline

**Estimated Time:** 8-10 hours

---

## Phase 5: Production Security Hardening & Deployment

### Task 5.1: Disable Swagger and Configure CORS ✅ COMPLETED
**Priority:** Critical (Blocking Production)
**Dependencies:** Task 3.3 (Documentation complete)
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md, SECURITY_CHECKLIST.md
**Completed:** 2026-01-13

**Subtasks:**
1. ✅ Add production configuration for Swagger:
   - ✅ Create environment variable `SWAGGER_ENABLED` (default: false)
   - ✅ Conditionally mount `/docs` and `/redoc` endpoints
   - ✅ Set in production `.env`: `SWAGGER_ENABLED=false`
2. ✅ Configure CORS allowlist:
   - ✅ Replace `["*"]` wildcard with specific allowed origins
   - ✅ Add environment variable `CORS_ORIGINS=["https://yourdomain.com"]`
   - ✅ Test that requests from unauthorized origins are rejected (403)
3. ✅ Create `.env.production` example file:
   - ✅ Document all required environment variables
   - ✅ Include security-specific settings

**Acceptance Criteria:**
- [x] Swagger is disabled in production config
- [x] CORS wildcard is removed
- [x] Unauthorized origins receive 403
- [x] `.env.production` documents all security settings
- [x] Verification step works: `curl http://localhost:8000/docs` → 404

**Estimated Time:** 1-2 hours (Actual: 2 hours)

---

### Task 5.2: Configure Monitoring & Alerting
**Priority:** Critical (Blocking Production)
**Dependencies:** Task 3.3
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md

**Subtasks:**
1. Set up metrics collection:
   - Install metrics library (Prometheus, DataDog, or CloudWatch)
   - Instrument key endpoints: `/convert`, `/health`
   - Track: request rate, error rate, response time, resource usage
2. Configure alerting thresholds:
   - Alert on high error rate (>10% 5xx errors)
   - Alert on extraction failures (suspicious pattern)
   - Alert on rate limit triggers
   - Alert on resource exhaustion (memory >90%, disk >80%)
3. Create alerting playbooks:
   - Document what each alert means
   - Provide troubleshooting steps
   - Document escalation procedures

**Acceptance Criteria:**
- [ ] Metrics are being collected
- [ ] Alerts are configured and tested
- [ ] Alert notifications work (email, Slack, PagerDuty)
- [ ] Playbooks are documented

**Estimated Time:** 4-6 hours

---

### Task 5.3: Set Up Log Aggregation
**Priority:** Critical (Blocking Production)
**Dependencies:** Task 3.3
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md

**Subtasks:**
1. Configure centralized logging:
   - Choose platform (ELK, Datadog, CloudWatch, Splunk)
   - Ingest container logs to central system
   - Include structured JSON logs from application
2. Set up log retention:
   - Minimum 90 days retention for security events
   - 30 days for operational logs
   - Configure archival to cold storage if needed
3. Create log search/analysis dashboards:
   - Dashboard for extraction failures
   - Dashboard for failed authentication attempts
   - Dashboard for rate limit triggers
   - Dashboard for performance anomalies

**Acceptance Criteria:**
- [ ] Logs are aggregated in central location
- [ ] All security events are logged
- [ ] Retention policy is enforced
- [ ] Dashboards are functional
- [ ] Can search and filter logs easily

**Estimated Time:** 4-6 hours

---

### Task 5.4: Implement Rate Limiting
**Priority:** High (SHOULD-DO, first month)
**Dependencies:** Task 5.2 (monitoring)
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md

**Subtasks:**
1. Choose rate limiting approach:
   - Option A: Deploy Redis and use redis-rate-limit middleware
   - Option B: Implement in-memory fallback with distributed coordination
   - Option C: Use API gateway / reverse proxy (Nginx, CloudFlare)
2. Configure rate limit rules:
   - `/convert` endpoint: 10 uploads/hour per IP
   - All endpoints: 100 requests/minute per IP
   - Allow higher limits for internal IPs
3. Implement graceful degradation:
   - If Redis is unavailable, fall back to in-memory limits
   - Log rate limit triggers for investigation
4. Test rate limiting:
   - Simulate traffic from single IP
   - Verify limits are enforced
   - Verify legitimate traffic isn't rejected

**Acceptance Criteria:**
- [ ] Rate limiting is deployed
- [ ] Limits prevent abuse (10 uploads/hour, 100 req/min)
- [ ] Fallback works if Redis unavailable
- [ ] Rate limit headers are returned
- [ ] Can be configured without code changes

**Estimated Time:** 4-6 hours

---

### Task 5.5: Dependency Management & Scanning
**Priority:** High (SHOULD-DO, first month)
**Dependencies:** Task 3.2 (tests passing)
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md

**Subtasks:**
1. Pin all dependency versions:
   - Update `requirements.txt` with exact versions
   - Add package hashes for verification
   - Document how to update dependencies safely
2. Set up CI/CD dependency scanning:
   - Install Dependabot, Snyk, or similar tool
   - Configure to scan on every PR
   - Fail builds on critical vulnerabilities
   - Auto-create PRs for security updates
3. Create dependency update process:
   - Weekly/monthly dependency checks
   - Test updates in development first
   - Document breaking changes
4. Set up container image scanning:
   - Scan Docker images for vulnerabilities
   - Fail builds if critical issues found

**Acceptance Criteria:**
- [ ] All dependencies have pinned versions
- [ ] Package hashes are included
- [ ] CI/CD scans dependencies
- [ ] Container images are scanned
- [ ] Process for updating dependencies is documented

**Estimated Time:** 2-3 hours

---

### Task 5.6: Security Testing in Staging
**Priority:** Critical (Before Production)
**Dependencies:** Task 5.1, 5.2, 5.3
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md, SECURITY_CHECKLIST.md

**Subtasks:**
1. Run security test suite in staging:
   - Execute `pytest tests/test_security.py -v` in staging environment
   - Verify all 25 tests pass
   - Check that actual response codes match expectations
2. Test resource limits under load:
   - Upload files near the 100MB limit
   - Verify size rejection works
   - Test large batch uploads
   - Monitor memory/CPU during uploads
3. Run through SECURITY_CHECKLIST.md:
   - Manually verify each checklist item
   - Document results
   - Address any failures
4. Conduct internal security review:
   - Have another team member review security measures
   - Check for configuration errors
   - Verify nothing is exposed unintentionally
5. (Optional) Hire external security firm:
   - Conduct professional penetration testing
   - Review threat model
   - Test against real-world attack scenarios

**Acceptance Criteria:**
- [ ] All 25 security tests pass in staging
- [ ] Resource limits work correctly
- [ ] All SECURITY_CHECKLIST.md items are verified
- [ ] Internal review is complete and documented
- [ ] No blockers found (or documented and mitigated)

**Estimated Time:** 8-12 hours (internal), +3-5 days (external review if done)

---

### Task 5.7: Health Endpoint Security
**Priority:** Medium (SHOULD-DO, first month)
**Dependencies:** Task 3.3
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md

**Subtasks:**
1. Restrict health endpoint access:
   - Add IP allowlist for `/health` endpoint
   - Only allow from internal IPs or monitoring service
   - Return 403 for unauthorized IPs
2. Add optional authentication:
   - Support bearer token for external monitoring
   - Document token generation process
3. Document health endpoint usage:
   - Create runbook for monitoring integration
   - Document expected response format
   - Document SLA for response time

**Acceptance Criteria:**
- [ ] `/health` is restricted to authorized IPs
- [ ] External monitoring can access with token
- [ ] Runbook documents integration process
- [ ] Tests verify access control works

**Estimated Time:** 1-2 hours

---

### Task 5.8: Deployment Runbook & Handoff
**Priority:** High (Before Production)
**Dependencies:** All Phase 5 tasks
**References:** SECURITY_IMPLEMENTATION_SUMMARY.md

**Subtasks:**
1. Create production deployment checklist:
   - Verify all MUST-DO items are complete
   - Document each verification step
   - Create approval gates
2. Create runbook for common operations:
   - How to deploy new version
   - How to rollback
   - How to scale up/down
   - How to investigate security incidents
3. Create incident response playbook:
   - How to detect attacks
   - How to respond to each type of incident
   - Who to contact, escalation procedures
   - Post-incident review process
4. Handoff to operations team:
   - Train ops team on all runbooks
   - Conduct deployment rehearsal
   - Document known issues and workarounds

**Acceptance Criteria:**
- [ ] Deployment checklist is complete
- [ ] Runbooks cover all common operations
- [ ] Incident response playbook is documented
- [ ] Ops team is trained
- [ ] Deployment rehearsal is successful

**Estimated Time:** 4-6 hours

---

## Summary

**Total Estimated Time:** 83-106 hours (Phase 1-4) + 30-45 hours (Phase 5) = **113-151 hours**

**Phase 5 Breakdown:**
- **MUST-DO (Blocking):** Tasks 5.1, 5.2, 5.3, 5.6, 5.8 = ~24-32 hours
- **SHOULD-DO (First month):** Tasks 5.4, 5.5, 5.7 = ~7-11 hours

**Critical Path:**
1. Docker Setup (1.1)
2. Deploy CLI App (1.2)
3. FastAPI Structure (1.3)
4. File Upload & Validation (1.4)
5. Workspace Management (1.5)
6. SubprocessManager (1.6)
7. Conversion Pipeline (1.7)
8. Frontend Implementation (2.1-2.4)
9. Testing & Hardening (3.1-3.3)
10. Quality Gates & Validation (4.1-4.4)
11. Security Hardening (5.1-5.3, 5.6) - BLOCKING for production
12. Deployment & Handoff (5.8)

**Dependencies Graph:**
- Phase 1 tasks are sequential (each depends on previous)
- Phase 2 can start after Task 1.3 (CORS)
- Phase 3 requires completion of Phase 1 and Phase 2
- Phase 4 requires completion of Phase 3
- Phase 5 starts after Phase 3 and runs in parallel with Phase 4
- Phase 5 MUST-DO items (5.1, 5.2, 5.3, 5.6, 5.8) are BLOCKING for production
- Phase 5 SHOULD-DO items (5.4, 5.5, 5.7) can be done in first month after launch

**Risk Items:**
- Swift binary compatibility (mitigated by Task 1.1)
- Orphaned files (mitigated by Task 1.4 and 1.5)
- Resource exhaustion (mitigated by Task 3.1 and 5.2)
- Code quality drift (mitigated by Task 4.1)
- Environment misconfiguration (mitigated by Task 4.2)
- Deployment failures (mitigated by Task 4.3)
- Architecture decay (mitigated by Task 4.4)
- **Security misconfiguration (mitigated by Task 5.1, 5.2, 5.3)**
- **Undetected attacks (mitigated by Task 5.2 monitoring, 5.3 logging)**
- **Insufficient rate limiting (mitigated by Task 5.4)**
- **Dependency vulnerabilities (mitigated by Task 5.5)**
- **Deployment errors (mitigated by Task 5.8 runbooks)**

---

## Phase 5: Implementation Order & Success Criteria

### Blocking Dependencies (No Production Deployment Until Complete)
These tasks MUST be done before exposing service to untrusted networks:
1. ✅ Task 5.1: Swagger disabled + CORS hardened
2. ✅ Task 5.2: Monitoring & alerting configured
3. ✅ Task 5.3: Log aggregation working
4. ✅ Task 5.6: Security testing passed in staging
5. ✅ Task 5.8: Deployment runbooks created & team trained

### First Month Tasks (Should Complete Within 30 Days)
1. Task 5.4: Rate limiting deployed
2. Task 5.5: Dependency scanning configured
3. Task 5.7: Health endpoint secured

### Success Criteria for Production Ready
- [ ] All Phase 5 MUST-DO items complete
- [ ] All 25 security tests pass in staging
- [ ] SECURITY_CHECKLIST.md all items verified
- [ ] Monitoring alerts are active and tested
- [ ] Logs are aggregating and searchable
- [ ] Ops team has run deployment rehearsal
- [ ] Incident response playbook is documented
- [ ] No known security vulnerabilities
- [ ] Rate limiting prevents abuse
- [ ] Team is trained on all runbooks

