# File Upload Integration Guide

## Overview
The File Upload System provides session-based file management with automatic PO parsing, compression, and storage. Supports multiple clients (Bajaj, Dava India) with automatic parser selection.

## Architecture

```
Upload Session → File Storage → Auto Parser → Database Insertion
     ↓              ↓               ↓              ↓
  Store metadata  Save files    Extract data   Insert PO
  Set TTL         Compress      Validate       Link project
  Track status    Encrypt       Transform      Create relations
```

---

## API Endpoints

### 1. Create Upload Session
```http
POST /api/uploads/session
Content-Type: application/json

{
  "metadata": {
    "project": "string",
    "description": "string",
    "department": "string"
  },
  "ttl_hours": 24,
  "client_id": 1
}
```

**Response:**
```json
{
  "session_id": "sess_client1_20260217_060822_dba7",
  "created_at": "2026-02-17T06:08:22.123456",
  "expires_at": "2026-02-18T06:08:22.123456",
  "status": "active",
  "metadata": {
    "project": "Test Project",
    "client_id": 1,
    "client_name": "Bajaj"
  },
  "file_count": 0
}
```

**Status Codes:**
- `200` - Session created successfully
- `400` - Invalid request parameters
- `500` - Server error

---

### 2. Upload File to Session
```http
POST /api/uploads/session/{session_id}/files
Content-Type: multipart/form-data

file: [Excel/PDF file]
uploaded_by: admin
po_number: PO-2026-001 (optional)
auto_parse: true
```

**Response:**
```json
{
  "file_id": "file_abc123def456",
  "session_id": "sess_client1_20260217_060822_dba7",
  "original_filename": "BAJAJ_PO.xlsx",
  "file_size": 125456,
  "compressed_size": 45123,
  "is_compressed": true,
  "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "file_hash": "sha256_hash",
  "compressed_hash": "sha256_hash",
  "upload_timestamp": "2026-02-17T06:08:22.123456",
  "po_number": "PO-2026-001",
  "access_url": "https://api.example.com/api/uploads/session/sess_abc/files/file_abc/download",
  "parse_status": "SUCCESS",
  "parse_error": null,
  "po_id": 42
}
```

**File Type Support:**
- Excel: `.xlsx`, `.xls`
- CSV: `.csv`
- PDF: `.pdf`

**Max File Size:** 50MB

---

### 3. Get Session Details
```http
GET /api/uploads/session/{session_id}
```

**Response:**
```json
{
  "session_id": "sess_client1_20260217_060822_dba7",
  "created_at": "2026-02-17T06:08:22.123456",
  "expires_at": "2026-02-18T06:08:22.123456",
  "status": "active",
  "metadata": {
    "project": "Test Project",
    "client_id": 1,
    "client_name": "Bajaj"
  },
  "file_count": 3
}
```

---

### 4. List Session Files
```http
GET /api/uploads/session/{session_id}/files
```

**Response:**
```json
[
  {
    "id": "file_abc123",
    "session_id": "sess_client1_20260217_060822_dba7",
    "original_filename": "BAJAJ_PO.xlsx",
    "storage_filename": "uuid_name_1.xlsx",
    "file_size": 125456,
    "compressed_size": 45123,
    "mime_type": "application/vnd.ms-excel",
    "upload_timestamp": "2026-02-17T06:10:00",
    "uploaded_by": "admin",
    "status": "active"
  }
]
```

---

### 5. Get Session Statistics
```http
GET /api/uploads/session/{session_id}/stats
```

**Response:**
```json
{
  "session_id": "sess_client1_20260217_060822_dba7",
  "total_files": 3,
  "total_size_bytes": 356368,
  "total_downloads": 0,
  "created_at": "2026-02-17T06:08:22",
  "expires_at": "2026-02-18T06:08:22",
  "status": "active"
}
```

---

### 6. Download File
```http
GET /api/uploads/session/{session_id}/files/{file_id}/download
```

**Response:** Binary file with headers:
```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename=BAJAJ_PO.xlsx
```

---

### 7. Delete File
```http
DELETE /api/uploads/session/{session_id}/files/{file_id}
```

**Response:**
```json
{
  "file_id": "file_abc123",
  "session_id": "sess_client1_20260217_060822_dba7",
  "deleted": true
}
```

---

### 8. Download All Files as ZIP
```http
POST /api/uploads/session/{session_id}/download-all
```

**Response:** ZIP file containing all session files

---

### 9. Delete Session
```http
DELETE /api/uploads/session/{session_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Session deleted successfully",
  "data": {"session_id": "sess_client1_20260217_060822_dba7"}
}
```

---

## Auto-Parsing Feature

When `auto_parse=true` and session has `client_id`:

1. **Parser Selection** - Automatically selects based on client_id
   - Client 1 (Bajaj) → Bajaj PO Parser
   - Client 2 (Dava India) → Proforma Invoice Parser

2. **Data Extraction** - Extracts:
   ```json
   {
     "po_details": {
       "po_number": "PO-2026-001",
       "po_date": "2026-02-17",
       "vendor_name": "Supplier Name",
       "vendor_gstin": "18AABCU9603R1Z0",
       "subtotal": 100000,
       "cgst": 9000,
       "sgst": 9000,
       "igst": 0,
       "total": 118000
     },
     "line_items": [
       {
         "item_name": "Item 1",
         "quantity": 10,
         "unit_price": 1000,
         "taxable_amount": 10000,
         "gross_amount": 11800
       }
     ]
   }
   ```

3. **Database Insertion** - Auto-inserts into `client_po` table

4. **Error Handling** - Parsing errors don't fail upload (graceful degradation)

---

## Database Schema

### upload_session table
```sql
CREATE TABLE upload_session (
  session_id VARCHAR PRIMARY KEY,
  client_id BIGINT,
  metadata JSONB,
  created_at TIMESTAMP,
  expires_at TIMESTAMP,
  status VARCHAR,
  ttl_hours INT
);
```

### upload_file table
```sql
CREATE TABLE upload_file (
  id VARCHAR PRIMARY KEY,
  session_id VARCHAR,
  po_number VARCHAR,
  original_filename VARCHAR,
  storage_filename VARCHAR,
  storage_path TEXT,
  file_size BIGINT,
  compressed_size BIGINT,
  is_compressed BOOLEAN,
  mime_type VARCHAR,
  file_hash VARCHAR,
  upload_timestamp TIMESTAMP,
  uploaded_by VARCHAR,
  metadata JSONB,
  status VARCHAR,
  FOREIGN KEY (session_id) REFERENCES upload_session(session_id)
);
```

---

## Implementation Example

### Python (requests)
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Create session
session_resp = requests.post(
    f"{BASE_URL}/api/uploads/session",
    json={
        "metadata": {"project": "test", "description": "Test upload"},
        "ttl_hours": 24,
        "client_id": 1
    }
)
session_id = session_resp.json()["session_id"]

# 2. Upload file
with open("BAJAJ_PO.xlsx", "rb") as f:
    files = {"file": f}
    data = {
        "uploaded_by": "admin",
        "auto_parse": "true"
    }
    upload_resp = requests.post(
        f"{BASE_URL}/api/uploads/session/{session_id}/files",
        files=files,
        data=data
    )
    result = upload_resp.json()
    file_id = result["file_id"]
    po_id = result.get("po_id")  # If auto-parsed

# 3. Get stats
stats_resp = requests.get(
    f"{BASE_URL}/api/uploads/session/{session_id}/stats"
)
print(f"Total files: {stats_resp.json()['total_files']}")

# 4. Download file
download_resp = requests.get(
    f"{BASE_URL}/api/uploads/session/{session_id}/files/{file_id}/download"
)
with open("downloaded_file.xlsx", "wb") as f:
    f.write(download_resp.content)
```

### JavaScript (fetch)
```javascript
const BASE_URL = "http://localhost:8000";

// 1. Create session
const sessionResp = await fetch(`${BASE_URL}/api/uploads/session`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    metadata: { project: "test" },
    ttl_hours: 24,
    client_id: 1
  })
});
const { session_id } = await sessionResp.json();

// 2. Upload file
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("uploaded_by", "admin");
formData.append("auto_parse", "true");

const uploadResp = await fetch(
  `${BASE_URL}/api/uploads/session/${session_id}/files`,
  {
    method: "POST",
    body: formData
  }
);
const result = await uploadResp.json();
console.log("File ID:", result.file_id);
console.log("Parse Status:", result.parse_status);
console.log("PO ID:", result.po_id);
```

---

## Error Handling

### Common Errors

```json
{
  "status": "ERROR",
  "error_code": "HTTP_ERROR",
  "message": "Session not found or expired",
  "path": "/api/uploads/session/invalid_session"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Not found (session/file doesn't exist)
- `413` - File too large (> 50MB)
- `500` - Server error

---

## Best Practices

1. **Session Management**
   - Always create session before uploading files
   - Set appropriate TTL based on use case
   - Clean up expired sessions regularly

2. **File Handling**
   - Validate file type before upload
   - Check file size limits
   - Use file hashing for integrity verification

3. **PO Parsing**
   - Enable auto_parse for supported clients only
   - Handle parsing errors gracefully
   - Validate parsed data before using

4. **Performance**
   - Use file compression (automatic)
   - Batch multiple files in single session
   - Implement pagination for file lists

5. **Security**
   - Validate session ownership (add auth)
   - Scan uploaded files for malware
   - Restrict allowed file types
   - Use HTTPS in production

---

## Limitations & Considerations

- Max file size: **50MB**
- Session TTL: Max **72 hours**
- Compression: Auto-enabled for xlsx/xls/csv
- File retention: Based on session TTL
- Concurrent uploads: No limit (configurable)
- Storage: Local filesystem (consider object storage for production)

