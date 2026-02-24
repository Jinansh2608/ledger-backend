# Documents & Files Management Integration Guide

## Overview
Document management system for storing, organizing, and retrieving files related to projects, vendors, and purchase orders.

## Architecture

```
Document Upload → Storage → Indexing → Search → Archive
       ↓            ↓          ↓         ↓        ↓
  Validation    Encrypt   Metadata   Filter   Compress
  Hash calc     Backup    Tags       Sort     Export
  Metadata      Version   Category   Query    Delete
```

---

## API Endpoints

### 1. Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: [Document file]
project_id: 1
vendor_id: 42
po_id: 5
document_type: "INVOICE" | "RECEIPT" | "CONTRACT" | "SPECIFICATION"
description: "Invoice for PO-2026-001"
tags: ["vendor42", "q1_2026"]
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "filename": "invoice_po_2026_001.pdf",
  "file_size": 256000,
  "document_type": "INVOICE",
  "upload_timestamp": "2026-02-17T10:30:00",
  "uploaded_by": "admin",
  "storage_path": "s3://bucket/2026/02/invoice_po_2026_001.pdf",
  "file_hash": "sha256_hash",
  "access_url": "https://api.example.com/api/documents/doc_abc123/download"
}
```

---

### 2. Get Document by ID
```http
GET /api/documents/{document_id}
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "filename": "invoice_po_2026_001.pdf",
  "original_filename": "invoice.pdf",
  "file_size": 256000,
  "document_type": "INVOICE",
  "upload_timestamp": "2026-02-17T10:30:00",
  "uploaded_by": "admin",
  "description": "Invoice for PO-2026-001",
  "tags": ["vendor42", "q1_2026"],
  "access_count": 5,
  "last_accessed": "2026-02-17T15:45:00",
  "linked_to": [
    {
      "type": "project",
      "id": 1,
      "name": "Q1 2026 Procurement"
    },
    {
      "type": "vendor",
      "id": 42,
      "name": "Supplier Name"
    },
    {
      "type": "po",
      "id": 5,
      "po_number": "PO-2026-001"
    }
  ]
}
```

---

### 3. List Documents (with filters)
```http
GET /api/documents?project_id=1&document_type=INVOICE&limit=10&offset=0
```

**Query Parameters:**
- `project_id` - Filter by project
- `vendor_id` - Filter by vendor
- `po_id` - Filter by PO
- `document_type` - Filter by type (INVOICE, RECEIPT, CONTRACT, SPECIFICATION)
- `tags` - Filter by tags (comma-separated)
- `uploaded_by` - Filter by uploader
- `date_from` - Filter from date
- `date_to` - Filter to date
- `limit` - Pagination limit (default: 50)
- `offset` - Pagination offset

**Response:**
```json
{
  "data": [
    {
      "document_id": "doc_abc123",
      "filename": "invoice.pdf",
      "document_type": "INVOICE",
      "file_size": 256000,
      "upload_timestamp": "2026-02-17T10:30:00"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

---

### 4. Download Document
```http
GET /api/documents/{document_id}/download
```

**Response:** Binary file with headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename=invoice.pdf
X-File-Hash: sha256_hash
```

---

### 5. Update Document Metadata
```http
PUT /api/documents/{document_id}
Content-Type: application/json

{
  "description": "Updated invoice for PO-2026-001",
  "tags": ["vendor42", "q1_2026", "invoiced"],
  "document_type": "INVOICE"
}
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "description": "Updated invoice for PO-2026-001",
  "tags": ["vendor42", "q1_2026", "invoiced"],
  "updated_at": "2026-02-17T11:30:00"
}
```

---

### 6. Link Document to Item
```http
POST /api/documents/{document_id}/link
Content-Type: application/json

{
  "item_type": "project|vendor|po",
  "item_id": 1
}
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "linked_to": [
    {
      "type": "project",
      "id": 1
    }
  ]
}
```

---

### 7. Search Documents
```http
POST /api/documents/search
Content-Type: application/json

{
  "query": "invoice 2026",
  "filters": {
    "document_type": "INVOICE",
    "date_from": "2026-01-01",
    "date_to": "2026-02-28"
  },
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc_abc123",
      "filename": "invoice.pdf",
      "relevance_score": 0.95,
      "matched_fields": ["filename", "description"]
    }
  ],
  "total": 5
}
```

---

### 8. Delete Document
```http
DELETE /api/documents/{document_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Document deleted successfully",
  "data": {"document_id": "doc_abc123"}
}
```

---

### 9. Get Document Statistics
```http
GET /api/documents/stats?project_id=1
```

**Response:**
```json
{
  "project_id": 1,
  "total_documents": 25,
  "total_size_bytes": 6400000,
  "documents_by_type": {
    "INVOICE": 10,
    "RECEIPT": 8,
    "CONTRACT": 5,
    "SPECIFICATION": 2
  },
  "recent_uploads": 3,
  "total_downloads": 45
}
```

---

## Database Schema

### document table
```sql
CREATE TABLE document (
  id VARCHAR PRIMARY KEY,
  original_filename VARCHAR(255) NOT NULL,
  storage_filename VARCHAR(255),
  storage_path TEXT,
  file_size BIGINT,
  file_hash VARCHAR(255),
  mime_type VARCHAR(100),
  document_type VARCHAR(50),
  description TEXT,
  project_id BIGINT,
  vendor_id BIGINT,
  po_id BIGINT,
  uploaded_by VARCHAR(100),
  upload_timestamp TIMESTAMP DEFAULT NOW(),
  access_count INT DEFAULT 0,
  last_accessed TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (project_id) REFERENCES project(id),
  FOREIGN KEY (vendor_id) REFERENCES vendor(id),
  FOREIGN KEY (po_id) REFERENCES vendor_order(id),
  INDEX idx_doc_type (document_type),
  INDEX idx_doc_project (project_id),
  INDEX idx_doc_vendor (vendor_id),
  INDEX idx_doc_po (po_id)
);
```

### document_tag table
```sql
CREATE TABLE document_tag (
  id BIGSERIAL PRIMARY KEY,
  document_id VARCHAR,
  tag VARCHAR(100),
  FOREIGN KEY (document_id) REFERENCES document(id),
  INDEX idx_tag (tag)
);
```

### document_link table
```sql
CREATE TABLE document_link (
  id BIGSERIAL PRIMARY KEY,
  document_id VARCHAR,
  linked_type VARCHAR(50),
  linked_id BIGINT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (document_id, linked_type, linked_id),
  FOREIGN KEY (document_id) REFERENCES document(id)
);
```

---

## Implementation Example

### Python
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Upload document
with open("invoice.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "project_id": 1,
        "vendor_id": 42,
        "po_id": 5,
        "document_type": "INVOICE",
        "description": "Invoice for PO-2026-001",
        "tags": ["vendor42", "q1_2026"]
    }
    upload_resp = requests.post(
        f"{BASE_URL}/api/documents/upload",
        files=files,
        data=data
    )
    doc = upload_resp.json()
    doc_id = doc["document_id"]

# 2. Get document details
details_resp = requests.get(
    f"{BASE_URL}/api/documents/{doc_id}"
)
details = details_resp.json()
print(f"Document: {details['filename']}")
print(f"Type: {details['document_type']}")
print(f"Downloads: {details['access_count']}")

# 3. List documents by project
list_resp = requests.get(
    f"{BASE_URL}/api/documents?project_id=1&limit=20"
)
documents = list_resp.json()["data"]
for doc in documents:
    print(f"{doc['filename']} - {doc['document_type']}")

# 4. Search documents
search_resp = requests.post(
    f"{BASE_URL}/api/documents/search",
    json={
        "query": "invoice 2026",
        "filters": {
            "document_type": "INVOICE",
            "date_from": "2026-01-01"
        }
    }
)
results = search_resp.json()["results"]
print(f"Found {len(results)} documents")

# 5. Link document to project
link_resp = requests.post(
    f"{BASE_URL}/api/documents/{doc_id}/link",
    json={
        "item_type": "project",
        "item_id": 2
    }
)

# 6. Update document metadata
update_resp = requests.put(
    f"{BASE_URL}/api/documents/{doc_id}",
    json={
        "description": "Updated invoice",
        "tags": ["vendor42", "q1_2026", "approved"]
    }
)

# 7. Download document
download_resp = requests.get(
    f"{BASE_URL}/api/documents/{doc_id}/download"
)
with open("downloaded_invoice.pdf", "wb") as f:
    f.write(download_resp.content)

# 8. Get statistics
stats_resp = requests.get(
    f"{BASE_URL}/api/documents/stats?project_id=1"
)
stats = stats_resp.json()
print(f"Total size: {stats['total_size_bytes']} bytes")
```

### JavaScript
```javascript
const BASE_URL = "http://localhost:8000";

// 1. Upload document
async function uploadDocument() {
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("project_id", 1);
  formData.append("vendor_id", 42);
  formData.append("po_id", 5);
  formData.append("document_type", "INVOICE");
  formData.append("description", "Invoice for PO-2026-001");
  formData.append("tags", "vendor42,q1_2026");

  const response = await fetch(
    `${BASE_URL}/api/documents/upload`,
    {
      method: "POST",
      body: formData
    }
  );
  return response.json();
}

// 2. Get document details
async function getDocument(docId) {
  const response = await fetch(
    `${BASE_URL}/api/documents/${docId}`
  );
  return response.json();
}

// 3. List documents
async function listDocuments() {
  const response = await fetch(
    `${BASE_URL}/api/documents?project_id=1&limit=20`
  );
  const { data, total } = await response.json();
  console.log(`Total documents: ${total}`);
  data.forEach(doc => {
    console.log(`${doc.filename} - ${doc.document_type}`);
  });
}

// 4. Download document
async function downloadDocument(docId) {
  const response = await fetch(
    `${BASE_URL}/api/documents/${docId}/download`
  );
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = "document.pdf";
  a.click();
}

// 5. Search documents
async function searchDocuments(query) {
  const response = await fetch(
    `${BASE_URL}/api/documents/search`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        filters: {
          document_type: "INVOICE",
          date_from: "2026-01-01"
        }
      })
    }
  );
  return response.json();
}
```

---

## Document Organization

### Recommended Folder Structure
```
documents/
├── projects/
│   ├── project_1/
│   │   ├── invoices/
│   │   ├── receipts/
│   │   ├── contracts/
│   │   └── specifications/
├── vendors/
│   ├── vendor_42/
│   │   ├── agreements/
│   │   ├── certifications/
│   │   └── invoices/
├── pos/
│   ├── po_5/
│   │   ├── invoice/
│   │   ├── receipt/
│   │   └── delivery/
```

---

## Document Types

- `INVOICE` - Invoice from vendor
- `RECEIPT` - Proof of delivery/receipt
- `CONTRACT` - Vendor agreement or contract
- `SPECIFICATION` - Product/service specification
- `AGREEMENT` - Service level agreement
- `CERTIFICATE` - Compliance/quality certificate
- `REPORT` - Project or audit report
- `OTHER` - Other document types

---

## Error Handling

**413 Payload Too Large**
```json
{
  "status": "ERROR",
  "error_code": "FILE_TOO_LARGE",
  "message": "File size exceeds limit (max: 100MB)"
}
```

**404 Not Found - Document Missing**
```json
{
  "status": "ERROR",
  "error_code": "DOCUMENT_NOT_FOUND",
  "message": "Document not found"
}
```

---

## Best Practices

1. **Upload & Storage**
   - Use meaningful file names
   - Add comprehensive descriptions
   - Tag documents properly
   - Include metadata

2. **Organization**
   - Organize by project/vendor
   - Use consistent naming convention
   - Link related documents
   - Archive old files

3. **Security**
   - Encrypt sensitive documents
   - Track access/downloads
   - Set appropriate permissions
   - Maintain audit logs

4. **Retention**
   - Define retention policies
   - Archive completed projects
   - Comply with regulations
   - Secure deletion

---

## Performance Considerations

- Index on document_type for filtering
- Index on tags for tag-based queries
- Compress PDFs before storage
- Use CDN for document delivery
- Archive documents older than 2 years
- Implement pagination for large results

