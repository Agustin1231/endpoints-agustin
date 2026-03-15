# TECHNICAL_SPECS.md - AI Agent Documentation

## Project Overview
Name: Python Utils API
Framework: FastAPI
Entry Point: main.py
Host Port: 8000

## Core Components and Entry Points

### 1. Browser Automation (endpoints/browser.py)
Prefix: /browser
Key Features:
- HubSpot Login Flow with 2FA support (uuid-based sessions).
- HTML Extraction from specific HubSpot Report URLs.
- Generic Navigation and Screenshot tool.
Dependencies: Playwright (async_api).

### 2. PDF Utilities (endpoints/html_pdf.py & endpoints/pdf_tools.py)
Endpoints:
- POST /html-to-pdf: Render HTML content into PDF bytes.
- POST /merge-pdfs: Combine Base64-encoded PDF files into a single binary.

### 3. Image Processing (endpoints/image_tools.py)
Endpoints:
- POST /image/strip-metadata: Expects UploadFile, returns Binary. Removes C2PA/caBX chunks and EXIF.
- POST /image/strip-metadata-base64: Expects JSON {"image_base64": "..."}. Returns JSON {"image_base64": "..."}.
Dependencies: Pillow (PIL).

### 4. Dynamic Execution (main.py)
Endpoints:
- POST /execute: Executes raw python strings via exec().
- POST /install: Dynamic package installation via pip.

## Environment Setup
Required system dependencies:
- Python 3.x
- Playwright binary (chromium)
- System libraries for Image processing (PIL)

## Implementation Details
- Session Management: Browser sessions are managed via a global SessionManager class in browser.py.
- Response Types: Mixed between Binary (Response object) and JSON depending on the endpoint utility.
- Error Handling: Standard HTTPException with status 400 or 500 for process failures.
