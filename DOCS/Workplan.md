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

### Task 1.2: Core FastAPI Application Structure
**Priority:** Critical  
**Dependencies:** Task 1.1  
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
- [ ] FastAPI app starts successfully
- [ ] Structured logging outputs JSON with request IDs
- [ ] Configuration is loaded from environment variables
- [ ] CORS is properly configured

**Estimated Time:** 3-4 hours

---

### Task 1.3: File Upload & Validation Service
**Priority:** Critical  
**Dependencies:** Task 1.2  
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
- [ ] Endpoint accepts file uploads
- [ ] Magic number validation rejects non-ZIP files (400 error)
- [ ] Files >100MB are rejected (413 error)
- [ ] Zip bomb protection prevents excessive decompression
- [ ] File paths are sanitized before use

**Estimated Time:** 6-8 hours

---

### Task 1.4: Workspace Management Service
**Priority:** Critical  
**Dependencies:** Task 1.3  
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
- [ ] Unique workspace directories are created per request
- [ ] Workspaces are deleted after request completion
- [ ] Startup script cleans orphaned directories
- [ ] Directory permissions are secure (700 or similar)

**Estimated Time:** 3-4 hours

---

### Task 1.5: SubprocessManager for Swift CLI Execution
**Priority:** Critical  
**Dependencies:** Task 1.4  
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
- [ ] Swift CLI is executed with 60s timeout
- [ ] Non-zero exit codes raise exceptions
- [ ] Stderr is captured and included in error responses
- [ ] Execution time is logged
- [ ] Process is killed if timeout is exceeded

**Estimated Time:** 4-5 hours

---

### Task 1.6: Conversion Pipeline & Response Streaming
**Priority:** Critical  
**Dependencies:** Task 1.5  
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
- [ ] Conversion pipeline completes successfully
- [ ] Response is streamed (not buffered entirely in RAM)
- [ ] Output ZIP contains Markdown files
- [ ] Error responses include CLI stderr
- [ ] Cleanup occurs on both success and failure

**Estimated Time:** 5-6 hours

---

### Task 1.7: Health Check Endpoint
**Priority:** Medium  
**Dependencies:** Task 1.2  
**References:** PRD Section 4

**Subtasks:**
1. Implement `GET /health` endpoint:
   - Check if Swift binary is available
   - Return `{"status": "ready", "binary_detected": true/false}`
2. Add basic system health checks (optional):
   - Disk space availability
   - Memory availability

**Acceptance Criteria:**
- [ ] Endpoint returns 200 with status JSON
- [ ] Binary detection works correctly
- [ ] Response matches PRD specification

**Estimated Time:** 1-2 hours

---

## Phase 2: The "Portal" (Frontend)

### Task 2.1: Frontend Project Setup
**Priority:** High  
**Dependencies:** Task 1.2 (CORS configured)  
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
- [ ] Frontend files are accessible
- [ ] Styling framework is integrated
- [ ] Base HTML structure is responsive

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
- [ ] Users can drag files onto the drop zone
- [ ] Users can click to select files
- [ ] Visual feedback is clear and responsive
- [ ] File name and size are displayed

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
- [ ] Upload progress bar shows 0-100%
- [ ] Processing state is clearly indicated
- [ ] Download starts automatically on success
- [ ] UI is disabled during processing

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
- [ ] Error messages are displayed clearly
- [ ] Different error types show appropriate messages
- [ ] Users can retry after errors
- [ ] UI resets properly after errors

**Estimated Time:** 3-4 hours

---

## Phase 3: Hardening & Testing

### Task 3.1: Security Hardening
**Priority:** High  
**Dependencies:** Task 1.6  
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
- [ ] Nginx limits are configured (if applicable)
- [ ] Rate limiting prevents abuse
- [ ] Security headers are set
- [ ] Request timeouts are enforced

**Estimated Time:** 3-4 hours

---

### Task 3.2: Unit & Integration Tests
**Priority:** High  
**Dependencies:** Task 1.6, Task 2.4  
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
- [ ] All test cases pass
- [ ] Test coverage >80% for critical paths
- [ ] Tests run in CI/CD pipeline
- [ ] Edge cases are covered

**Estimated Time:** 8-10 hours

---

### Task 3.3: Documentation & Deployment
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
- [ ] README is comprehensive and clear
- [ ] API documentation is accessible
- [ ] Deployment guide is complete
- [ ] Environment variables are documented

**Estimated Time:** 3-4 hours

---

## Summary

**Total Estimated Time:** 60-75 hours

**Critical Path:**
1. Docker Setup (1.1)
2. FastAPI Structure (1.2)
3. File Upload & Validation (1.3)
4. Workspace Management (1.4)
5. SubprocessManager (1.5)
6. Conversion Pipeline (1.6)
7. Frontend Implementation (2.1-2.4)
8. Testing & Hardening (3.1-3.2)

**Dependencies Graph:**
- Phase 1 tasks are sequential (each depends on previous)
- Phase 2 can start after Task 1.2 (CORS)
- Phase 3 requires completion of Phase 1 and Phase 2

**Risk Items:**
- Swift binary compatibility (mitigated by Task 1.1)
- Orphaned files (mitigated by Task 1.4)
- Resource exhaustion (mitigated by Task 3.1)

