# File Upload Integration Guide

## Overview

The backend provides a comprehensive file upload system with features including:
- Session-based file management
- Client-specific PO parsing (Bajaj PO & Dava India Invoices)
- **Automatic database insertion of parsed data** ✅ (FIXED)
- File compression and decompression
- Access control and storage management
- Support for multiple file types

## 🎯 Important Fix (February 16, 2026)

**AUTO-PARSED FILES NOW SAVE TO DATABASE** ✅

When you upload a file with `auto_parse=true` and the session has `client_id`, the parsed PO data is now automatically inserted into the `client_po` and `client_po_line_item` tables.

**What happens:**
1. File uploaded → stored in `upload_file` table
2. Auto-parse enabled → parsed using client-specific parser
3. ✅ **NEW**: Parsed data automatically inserted into `client_po` table
4. Returns `client_po_id` in response for reference

**Before fix**: Parsed data was only stored as JSON metadata
**After fix**: Parsed data is inserted into business tables for queries/reports

---

## Quick Start

### 1. Create an Upload Session
```javascript
const response = await fetch('/api/uploads/session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    metadata: { project: "nexgen", user_id: 123 },
    ttl_hours: 24,
    client_id: 1  // 1=Bajaj, 2=Dava India
  })
});

const { session_id, expires_at } = await response.json();
```

### 2. Upload File to Session
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('uploaded_by', 'john_doe');
formData.append('po_number', 'PO-2024-001');  // optional
formData.append('auto_parse', 'true');  // auto-parse if client_id in session

const response = await fetch(`/api/uploads/session/${session_id}/files`, {
  method: 'POST',
  body: formData
});

const { file_id, access_url, direct_url } = await response.json();
```

### 3. Download File
```javascript
// Option 1: Using access URL from upload response
window.location.href = file.access_url;

// Option 2: Direct URL
window.location.href = file.direct_url;

// Option 3: By PO number
window.location.href = `/api/uploads/po/${po_number}/files/${file_id}/download`;
```

---

## Detailed API Reference

### 1. Session Management

#### Create Session
**Endpoint:** `POST /api/uploads/session`

**Request:**
```json
{
  "metadata": {
    "project": "string",
    "user": "string",
    "custom_field": "any value"
  },
  "ttl_hours": 24,
  "client_id": 1
}
```

**Response:**
```json
{
  "session_id": "sess_550e8400-e29b",
  "created_at": "2024-02-15T10:00:00Z",
  "expires_at": "2024-02-16T10:00:00Z",
  "status": "active",
  "metadata": { "project": "nexgen" },
  "file_count": 0
}
```

**Parameters:**
- `metadata` (optional): Custom metadata dict to store with session
- `ttl_hours` (optional, default=24): Session lifetime in hours (max=720)
- `client_id` (optional): Client ID (1=Bajaj, 2=Dava India) for auto-parsing

---

#### Get Session Details
**Endpoint:** `GET /api/uploads/session/{sessionId}`

**Response:**
```json
{
  "session_id": "sess_550e8400",
  "created_at": "2024-02-15T10:00:00Z",
  "expires_at": "2024-02-16T10:00:00Z",
  "status": "active",
  "metadata": { "project": "nexgen" },
  "file_count": 3
}
```

---

#### Get Session Statistics
**Endpoint:** `GET /api/uploads/session/{sessionId}/stats`

**Response:**
```json
{
  "session_id": "sess_550e8400",
  "total_files": 5,
  "total_size_bytes": 5242880,
  "total_downloads": 12,
  "created_at": "2024-02-15T10:00:00Z",
  "expires_at": "2024-02-16T10:00:00Z",
  "status": "active"
}
```

---

#### Delete Session
**Endpoint:** `DELETE /api/uploads/session/{sessionId}`

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Session deleted successfully",
  "data": { "session_id": "sess_550e8400" }
}
```

---

### 2. File Upload & Management

#### Upload File to Session
**Endpoint:** `POST /api/uploads/session/{sessionId}/files`

**Method:** multipart/form-data

**Parameters:**
- `file` (required): File to upload
- `uploaded_by` (optional): User who uploaded the file
- `po_number` (optional): Associate file with PO number
- `auto_parse` (optional, default=true): Auto-parse if client_id in session

**Response:**
```json
{
  "status": "SUCCESS",
  "file_id": "file_xyz789",
  "session_id": "sess_550e8400",
  "original_filename": "Bajaj_PO.xlsx",
  "file_size": 1024000,
  "compressed_size": 512000,
  "is_compressed": true,
  "mime_type": "application/vnd.ms-excel",
  "file_hash": "sha256hash...",
  "compressed_hash": "sha256hash...",
  "upload_timestamp": "2024-02-15T10:30:00Z",
  "po_number": "PO-2024-001",
  "access_url": "/api/uploads/files/file_xyz789",
  "direct_url": "/uploads/sess_550e8400/file_xyz789.xlsx"
}
```

**Auto-Parse Behavior:**
- Only triggers if session has `client_id` in metadata
- Uses appropriate parser based on client (Bajaj PO or Dava India invoice)
- Parsing errors don't fail upload (graceful degradation)
- Parsed data is automatically inserted into database if `auto_save=true`

---

#### Upload & Parse PO (Combined)
**Endpoint:** `POST /api/uploads/po/upload`

**Query Parameters:**
- `client_id` (required, 1=Bajaj, 2=Dava India)
- `project_id` (optional): Link PO to project
- `uploaded_by` (optional): User who uploaded
- `auto_save` (optional, default=true): Auto-insert parsed PO to database

**Response (if parsed successfully):**
```json
{
  "status": "SUCCESS",
  "file_id": "file_xyz789",
  "session_id": "sess_550e8400",
  "client_id": 1,
  "client_name": "Bajaj",
  "parser_type": "po",
  "po_details": {
    "po_number": "123456",
    "po_date": "2024-02-15",
    "vendor_name": "XYZ Supplier",
    "po_value": 100000
  },
  "line_items": [
    {
      "description": "Item 1",
      "quantity": 10,
      "rate": 5000,
      "amount": 50000
    }
  ],
  "line_item_count": 2,
  "client_po_id": 42,
  "original_filename": "Bajaj_PO_123456.xlsx",
  "upload_timestamp": "2024-02-15T10:30:00Z"
}
```

**Response (if upload succeeded but parsing failed):**
```json
{
  "status": "UPLOAD_SUCCESS_PARSE_FAILED",
  "file_id": "file_xyz789",
  "session_id": "sess_550e8400",
  "po_details": {
    "error": "Could not parse file: Invalid format"
  },
  "line_items": [],
  "line_item_count": 0
}
```

---

### 3. File Listing & Retrieval

#### List Session Files
**Endpoint:** `GET /api/uploads/session/{sessionId}/files`

**Query Parameters:**
- `skip` (default=0): Pagination offset
- `limit` (default=50, max=100): Number of files to return

**Response:**
```json
{
  "status": "SUCCESS",
  "session_id": "sess_550e8400",
  "file_count": 3,
  "total_size": 3145728,
  "files": [
    {
      "id": "file_xyz789",
      "session_id": "sess_550e8400",
      "original_filename": "report.pdf",
      "storage_filename": "xyz789_report.pdf",
      "file_size": 1024000,
      "mime_type": "application/pdf",
      "file_hash": "sha256hash...",
      "upload_timestamp": "2024-02-15T10:30:00Z",
      "uploaded_by": "john_doe",
      "status": "active"
    }
  ]
}
```

---

#### List Files by PO Number
**Endpoint:** `GET /api/uploads/po/{poNumber}/files`

**Query Parameters:**
- `skip` (default=0): Pagination offset
- `limit` (default=50): Files to return

**Response:**
```json
{
  "status": "SUCCESS",
  "po_number": "PO-2024-001",
  "file_count": 2,
  "total_size": 2048000,
  "compressed_size": 1024000,
  "compression_ratio": 0.5,
  "files": [
    {
      "id": "file_xyz789",
      "original_filename": "invoice.pdf",
      "file_size": 1024000,
      "upload_timestamp": "2024-02-15T10:30:00Z"
    }
  ],
  "skip": 0,
  "limit": 50,
  "total_count": 2
}
```

---

### 4. File Download

#### Download File from Session
**Endpoint:** `GET /api/uploads/session/{sessionId}/files/{fileId}/download`

**Query Parameters:**
- `token` (optional): Access token for additional security

**Response:** Binary file stream

**Example:**
```javascript
const response = await fetch(`/api/uploads/session/${sessionId}/files/${fileId}/download`);
const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const link = document.createElement('a');
link.href = url;
link.download = 'file.pdf';
link.click();
```

---

#### Download File by PO
**Endpoint:** `GET /api/uploads/po/{poNumber}/files/{fileId}/download`

**Response:** Binary file stream

---

### 5. File Deletion

#### Delete Individual File
**Endpoint:** `DELETE /api/uploads/session/{sessionId}/files/{fileId}`

**Query Parameters:**
- `user_id` (optional): User deleting the file

**Response:**
```json
{
  "file_id": "file_xyz789",
  "session_id": "sess_550e8400",
  "deleted": true
}
```

---

#### Delete Session (and All Files)
**Endpoint:** `DELETE /api/uploads/session/{sessionId}`

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Session deleted successfully",
  "data": { "session_id": "sess_550e8400" }
}
```

---

## Frontend Integration Examples

### React Hook: File Upload
```javascript
import { useState } from 'react';

function FileUpload({ projectId, clientId }) {
  const [sessionId, setSessionId] = useState(null);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  // Create session
  const createSession = async () => {
    const response = await fetch('/api/uploads/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        metadata: { project_id: projectId },
        ttl_hours: 24,
        client_id: clientId
      })
    });
    const data = await response.json();
    setSessionId(data.session_id);
  };

  // Upload file
  const uploadFile = async (file) => {
    if (!sessionId) {
      await createSession();
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('uploaded_by', 'user@example.com');
    formData.append('auto_parse', 'true');

    try {
      const response = await fetch(`/api/uploads/session/${sessionId}/files`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setFiles([...files, data]);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={(e) => uploadFile(e.target.files[0])}
        disabled={uploading}
      />
      <div>
        {files.map((f) => (
          <div key={f.file_id}>
            {f.original_filename} - {f.file_size} bytes
          </div>
        ))}
      </div>
    </div>
  );
}

export default FileUpload;
```

### React Hook: File Download
```javascript
function FileDownload({ sessionId, fileId, filename }) {
  const downloadFile = async () => {
    const response = await fetch(
      `/api/uploads/session/${sessionId}/files/${fileId}/download`
    );
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  return <button onClick={downloadFile}>Download</button>;
}

export default FileDownload;
```

### React Hook: List Session Files
```javascript
import { useEffect, useState } from 'react';

function FileList({ sessionId }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchFiles = async () => {
      const response = await fetch(`/api/uploads/session/${sessionId}/files`);
      const data = await response.json();
      setFiles(data.files);
      
      const statsResponse = await fetch(`/api/uploads/session/${sessionId}/stats`);
      const statsData = await statsResponse.json();
      setStats(statsData);
      
      setLoading(false);
    };
    fetchFiles();
  }, [sessionId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Files: {files.length}</h2>
      <p>Total Size: {(stats.total_size_bytes / 1024 / 1024).toFixed(2)} MB</p>
      <ul>
        {files.map((file) => (
          <li key={file.id}>
            {file.original_filename} - {(file.file_size / 1024).toFixed(2)} KB
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FileList;
```

### React Component: Upload & Parse PO
```javascript
import { useState } from 'react';

function POUpload({ projectId }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        `/api/uploads/po/upload?client_id=1&project_id=${projectId}&auto_save=true`,
        {
          method: 'POST',
          body: formData
        }
      );
      const data = await response.json();
      
      if (data.status === 'SUCCESS') {
        setResult({
          poNumber: data.po_details.po_number,
          poValue: data.po_details.po_value,
          lineItems: data.line_items,
          clientPoId: data.client_po_id
        });
      } else if (data.status === 'UPLOAD_SUCCESS_PARSE_FAILED') {
        setError('File uploaded but parsing failed. Please check format.');
      }
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".xlsx,.xls,.csv"
        onChange={handleUpload}
        disabled={loading}
      />
      
      {loading && <p>Uploading and parsing...</p>}
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {result && (
        <div>
          <h3>PO Parsed Successfully</h3>
          <p>PO Number: {result.poNumber}</p>
          <p>PO Value: ₹{result.poValue}</p>
          <p>Line Items: {result.lineItems.length}</p>
          <p>Saved to Database ID: {result.clientPoId}</p>
        </div>
      )}
    </div>
  );
}

export default POUpload;
```

---

## Supported File Types

### For Bajaj PO
- Excel files (.xlsx, .xls)
- CSV format
- Format: Specific Bajaj PO column layout

### For Dava India
- Excel files (.xlsx, .xls)
- CSV format
- Format: Dava India proforma invoice layout

### General Files
- PDF (.pdf)
- Word documents (.docx, .doc)
- Images (.jpg, .jpeg, .png)
- Any binary file

---

## File Size Limits

- **Maximum file size:** 50 MB
- **Recommended size:** < 10 MB for optimal performance
- **Batch upload:** Upload multiple files sequentially (separate requests)

---

## Error Handling

### Common Errors

**404 Not Found**
```json
{
  "detail": "Session not found or expired"
}
```
Solution: Create a new session or verify session_id

---

**400 Bad Request**
```json
{
  "detail": "Invalid file type"
}
```
Solution: Check file format matches expected type

---

**413 Payload Too Large**
```json
{
  "detail": "File size exceeds limit"
}
```
Solution: Upload files smaller than 50 MB

---

**500 Internal Server Error**
```json
{
  "detail": "Upload failed: [error details]"
}
```
Solution: Check server logs, retry, or contact support

---

## Best Practices

### 1. Session Management
```javascript
// Create session once, reuse for multiple files
const session = await createSession();
const sessionId = session.session_id;

// Upload multiple files in the same session
for (const file of files) {
  await uploadFile(sessionId, file);
}

// Clean up when done
await deleteSession(sessionId);
```

### 2. Error Handling
```javascript
try {
  const response = await fetch(url);
  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error.detail);
  }
} catch (error) {
  console.error('Network Error:', error);
}
```

### 3. Progress Tracking
```javascript
const uploadFileWithProgress = async (file, sessionId) => {
  const formData = new FormData();
  formData.append('file', file);

  const xhr = new XMLHttpRequest();

  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percentComplete = (e.loaded / e.total) * 100;
      console.log(`Upload progress: ${percentComplete}%`);
    }
  });

  return new Promise((resolve, reject) => {
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    xhr.addEventListener('error', reject);
    xhr.open('POST', `/api/uploads/session/${sessionId}/files`);
    xhr.send(formData);
  });
};
```

### 4. File Validation Before Upload
```javascript
const validateFile = (file) => {
  // Check file size
  if (file.size > 50 * 1024 * 1024) {
    throw new Error('File exceeds 50 MB limit');
  }

  // Check file type
  const allowedTypes = ['application/vnd.ms-excel', 'application/pdf'];
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Invalid file type');
  }

  return true;
};
```

---

## Auto-Parsing Configuration

### What Gets Parsed
When `auto_parse=true` and session has `client_id`:

**For Bajaj PO (client_id=1):**
- PO Number
- PO Date
- Vendor Information
- Line Items (Description, Quantity, Rate, Amount)
- Tax Information (HSN, CGST, SGST, IGST)
- Total Value

**For Dava India (client_id=2):**
- Invoice Number
- Invoice Date
- Ship-to Address
- Bill-to Address
- Line Items
- GST Amount
- Grand Total

### Automatic Database Insertion
When `auto_save=true`:
- Parsed data is automatically inserted into `client_po` table
- `client_po_id` is returned in response
- Errors during insertion don't fail the upload

---

## Performance Tips

1. **Use compression:** Files are auto-compressed (saves ~50% space)
2. **Pagination:** Use `skip` and `limit` for large file lists
3. **Batch operations:** Upload related files in same session
4. **Cleanup:** Delete old sessions to free storage
5. **Monitoring:** Check session stats periodically

---

## Security Considerations

1. **Session expiration:** Sessions auto-expire after TTL (default 24h)
2. **File isolation:** Files are stored under session directory
3. **Access control:** Optional token parameter for additional security
4. **User tracking:** `uploaded_by` parameter for audit trail
5. **Safe deletion:** Soft delete keeps files temporarily for recovery

---

## Troubleshooting

### Files not uploading
- Check session hasn't expired
- Verify file size < 50 MB
- Check file format is supported
- Review browser console for errors

### Parsing failed but upload succeeded
- File format may not match expected layout
- Check column headers match expected parser format
- Try uploading without auto_parse and review manually

### Session expired
- Sessions expire after TTL hours (default 24)
- Create new session for new uploads
- Extend TTL in create session request if needed

### Performance issues
- Large files take longer to parse/compress
- Use pagination (`skip`, `limit`) for file lists
- Consider uploading in batches rather than bulk

---

## Support & Documentation

- Full API Reference: See endpoint details above
- Code Examples: React examples provided in this guide
- Test Script: `verify_routes.py` includes file upload tests

