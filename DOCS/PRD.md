# PRD: Swift DocC to Markdown Web Converter (MVP)

Here is the improved PRD with enhanced technical depth and structural clarity.

## 1. Executive Summary

Objective: Provide a lightweight, browser-based interface for the Swift DocC-Markdown CLI tool. This service allows developers to convert Apple-standard documentation archives into portable Markdown without installing the Swift toolchain locally.
Key Values: * Privacy-First: Zero persistent storage.
* Low Friction: No accounts, no installs.
* Portability: Works on any OS via the browser.

## 2. System Architecture & Data Flow
The service follows a synchronous pipe pattern. Because conversion is expected to be fast (<15s), we use a blocking request with a background cleanup task.
Request Lifecycle:
1. Ingestion: FastAPI receives a multipart/form-data POST request.
2. Validation: File headers are checked (Magic bytes for ZIP).
3. Workspace Isolation: A ephemeral directory is created using uuid4.
4. Transformation: The Swift binary is invoked via a controlled subprocess.
5. Egress: The resulting Markdown tree is zipped and streamed to the user.
6. Purge: The workspace is deleted regardless of success or failure.

## 3. Product Requirements

### Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| FR1 | Magic Number Validation | Do not rely on .zip extensions; validate the file header to prevent malicious uploads. |
| FR2 | Zip Bomb Protection | Limit decompression size to 5x the upload size or a hard cap of 500MB to prevent DOS. |
| FR3 | Streaming Response | Use FileResponse or StreamingResponse to ensure the server doesn't hold the entire output ZIP in RAM. |
| FR4 | Subprocess Sandboxing | Run the Swift binary with timeout and check=True to prevent hanging processes. |
| FR5 | Real-time Feedback | Frontend should use the Fetch API to track upload progress and display specific error messages from the CLI. |

### Non-Functional Requirements

* Statelessness: No session affinity required. Any instance can handle any request.
* Security: * Path Sanitization: Use werkzeug.utils.secure_filename or similar logic.
    * Resource Limits: Max 100MB per upload; Max 60s execution time.
* Observability: Structured JSON logging for request ID, conversion time, and error codes.

## 4. API Specification
POST /api/v1/convert
* Input: file: UploadFile
* Responses:
    * 200 OK: Returns .zip file stream.
    * 400 Bad Request: Invalid file type or corrupted ZIP.
    * 413 Payload Too Large: File exceeds 100MB.
    * 500 Internal Server Error: Swift CLI failure (includes CLI stderr in payload for debugging).
GET /health
* Response: {"status": "ready", "binary_detected": true}

## 5. Implementation Roadmap (Refined)

### Phase 1: The "Engine" (Backend)

* Task 1.1: Build a Dockerfile that includes the Swift runtime + Python 3.10.
* Task 1.2: Implement the SubprocessManager to handle CLI execution and exit code mapping.
* Task 1.3: Create a CleanupMiddleware or BackgroundTasks routine to wipe /tmp/{uuid}.

### Phase 2: The "Portal" (Frontend)

* Task 2.1: Build a drag-and-drop zone using vanilla JS and Tailwind CSS (or simple CSS).
* Task 2.2: Implement an XHR/Fetch progress bar to show upload % vs. "Processing..." state.
* Task 2.3: Error state UI for "Invalid Archive" or "Server Timeout."

### Phase 3: Hardening

* Task 3.1: Add Nginx limit_conn to prevent a single IP from flooding the converter.
* Task 3.2: Write Pytest cases for:
    * Uploading a non-zip file.
    * Uploading a ZIP that isn't a .doccarchive.
    * Simulating a CLI timeout.

## 6. Risk Mitigation

* Risk: Swift binary requires specific shared libraries (e.g., libicu).
    * Mitigation: Use a multi-stage Docker build to ensure the runtime environment matches the build environment exactly.
* Risk: Orphaned files if the server crashes mid-conversion.
    * Mitigation: Add a cron job or a startup script to clear /tmp/swift-conv-* directories on boot.
