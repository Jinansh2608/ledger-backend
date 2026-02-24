# Quick Reference Card - Common Operations

## Endpoints Quick Map

### Vendors Module (/api/vendors)
```
POST     /api/vendors                    → Create vendor
GET      /api/vendors/{id}               → Get vendor by ID
GET      /api/vendors                    → List all vendors (with filters)
PUT      /api/vendors/{id}               → Update vendor
DELETE   /api/vendors/{id}               → Delete vendor
GET      /api/vendors/{id}/details       → Get vendor with orders & payments
GET      /api/vendors/{id}/payments      → List vendor payments
GET      /api/vendors/{id}/payment-summary → Payment summary
```

### Purchase Orders Module (/api/vendor-orders)
```
POST     /api/vendor-orders              → Create PO
GET      /api/vendor-orders/{id}         → Get PO by ID
GET      /api/vendor-orders              → List POs (with filters)
PUT      /api/vendor-orders/{id}         → Update PO
DELETE   /api/vendor-orders/{id}         → Cancel PO
GET      /api/vendor-orders/{id}/history → Status history
POST     /api/vendor-orders/{id}/delivery → Record delivery
POST     /api/vendor-orders/{id}/invoice → Link invoice
```

### Payments Module (/api/payments)
```
POST     /api/payments                   → Create payment
GET      /api/payments/{id}              → Get payment by ID
GET      /api/payments                   → List payments (with filters)
PUT      /api/payments/{id}              → Update payment status
DELETE   /api/payments/{id}              → Delete payment
GET      /api/payments/{id}/status       → Payment status history
POST     /api/payments/bulk-process      → Bulk process payments
GET      /api/payments/summary/by-vendor → Payment summary
```

### Projects Module (/api/projects)
```
POST     /api/projects                   → Create project
GET      /api/projects/{id}              → Get project by ID
GET      /api/projects                   → List projects (with filters)
PUT      /api/projects/{id}              → Update project
DELETE   /api/projects/{id}              → Delete project
GET      /api/projects/{id}/summary      → Project summary with budget
POST     /api/projects/{id}/pos          → Link POs to project
POST     /api/projects/{id}/vendors      → Link vendors to project
GET      /api/projects/{id}/pos          → Get project POs
GET      /api/projects/{id}/vendors      → Get project vendors
```

### File Uploads Module (/api/uploads)
```
POST     /api/uploads/session            → Create upload session
GET      /api/uploads/session/{id}       → Get session details
POST     /api/uploads/session/{id}/files → Upload file to session
GET      /api/uploads/session/{id}/files → List session files
GET      /api/uploads/session/{id}/stats → Get session stats
DELETE   /api/uploads/session/{id}/files/{file_id} → Delete file
GET      /api/uploads/session/{id}/files/{file_id}/download → Download file
POST     /api/uploads/session/{id}/download-all → Download all as ZIP
DELETE   /api/uploads/session/{id}       → Delete session
```

### Billing PO Module (/api/billing)
```
POST     /api/billing/pos                → Create billing PO
GET      /api/billing/pos/{id}           → Get billing PO by ID
GET      /api/billing/pos                → List billing POs (with filters)
PUT      /api/billing/pos/{id}           → Update billing PO
POST     /api/billing/pos/{id}/payments  → Link payment to PO
GET      /api/billing/pos/{id}/payments  → Get PO payments
POST     /api/billing/pos/{id}/invoice   → Generate invoice
GET      /api/billing/clients/{id}/summary → Client billing summary
GET      /api/billing/statistics         → Billing statistics
```

### Documents Module (/api/documents)
```
POST     /api/documents/upload           → Upload document
GET      /api/documents/{id}             → Get document by ID
GET      /api/documents                  → List documents (with filters)
PUT      /api/documents/{id}             → Update document metadata
DELETE   /api/documents/{id}             → Delete document
GET      /api/documents/{id}/download    → Download document
POST     /api/documents/{id}/link        → Link document to item
POST     /api/documents/search           → Search documents
GET      /api/documents/stats            → Document statistics
```

---

## Common Request Patterns

### Filter/List Pattern
```
GET /api/endpoint?field1=value1&field2=value2&limit=10&offset=0

Common Parameters:
- limit        → Page size (default: 50, max: 100)
- offset       → Pagination offset (default: 0)
- sort_by      → Field to sort (default: created_at)
- sort_order   → asc or desc (default: desc)
```

### Date Filtering Pattern
```
?date_from=2026-01-01&date_to=2026-02-28

Or
?start_date=2026-01-01&end_date=2026-02-28
(varies by endpoint)
```

### Status Filtering Pattern
```
?status=ACTIVE          → Single value
?status=ACTIVE,PENDING  → Multiple values (comma-separated)

Common statuses:
- Vendors: ACTIVE, INACTIVE, SUSPENDED
- POs: PENDING_CONFIRMATION, CONFIRMED, DELIVERED, COMPLETED
- Payments: PENDING, PROCESSING, COMPLETED, FAILED
- Projects: ACTIVE, ON_HOLD, COMPLETED, ARCHIVED
- Files: active, deleted
```

---

## Common Workflows (One-Liners)

### Create Complete Vendor-PO-Payment Flow
```python
# 1. Create vendor
vendor = post("/vendors", {name, email, gstin, ...})

# 2. Create PO
po = post(f"/vendor-orders", {vendor_id, po_number, amount, ...})

# 3. Create payment
payment = post("/payments", {vendor_id, vendor_order_id, amount, ...})

# 4. Update payment to COMPLETED
put(f"/payments/{payment_id}", {status: "COMPLETED", ...})
```

### Create Project & Track Budget
```python
# 1. Create project with budget
project = post("/projects", {name, budget: 5000000, ...})

# 2. Link POs to project
post(f"/projects/{project_id}/pos", {po_ids: [1, 2, 3]})

# 3. Get budget status
summary = get(f"/projects/{project_id}/summary")
# Check: budget_utilization_percent
```

### Upload & Auto-Parse Client PO
```python
# 1. Create session (client_id=1 for Bajaj)
session = post("/uploads/session", {client_id: 1, ...})

# 2. Upload file with auto_parse
post(f"/uploads/session/{session_id}/files", 
     files={file}, 
     data={auto_parse: true, uploaded_by: "admin"})
# Returns: po_id (if auto-parsed successfully)

# 3. Get session stats
stats = get(f"/uploads/session/{session_id}/stats")
```

### Process Bulk Payments
```python
# Collect all payment IDs to process
payment_ids = [101, 102, 103, 104, 105]

# Bulk process
post("/payments/bulk-process", {
    payment_ids: payment_ids,
    batch_reference: "BATCH-2026-001",
    processing_date: "2026-02-20",
    notes: "Weekly payment batch"
})
```

### Document Management - Upload & Link
```python
# 1. Upload document
doc = post("/documents/upload",
    files={file},
    data={
        project_id: 1,
        vendor_id: 42,
        document_type: "INVOICE",
        tags: ["vendor42", "q1_2026"]
    })

# 2. Link to additional items
post(f"/documents/{doc_id}/link", {item_type: "project", item_id: 2})
post(f"/documents/{doc_id}/link", {item_type: "vendor", item_id: 43})

# 3. Search documents
post("/documents/search", {
    query: "invoice 2026",
    filters: {document_type: "INVOICE", date_from: "2026-01-01"}
})
```

---

## Response Format Reference

### Success Response (GET)
```json
{
  "id": 1,
  "name": "Value",
  "email": "email@example.com",
  "created_at": "2026-02-17T10:30:00",
  "updated_at": "2026-02-17T10:30:00"
}
```

### Success Response (LIST)
```json
{
  "data": [
    { "id": 1, "name": "Value 1" },
    { "id": 2, "name": "Value 2" }
  ],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

### Error Response
```json
{
  "status": "ERROR",
  "error_code": "ERROR_TYPE",
  "message": "Human readable error message",
  "details": {
    "field": "fieldname",
    "issue": "specific problem"
  }
}
```

---

## Important Column Names & Values

### Vendor Payment Terms
```
NET_15, NET_30, NET_45, NET_60, COD, ADVANCE
```

### Payment Status
```
PENDING → PROCESSING → COMPLETED (or FAILED)
```

### PO Status
```
PENDING_CONFIRMATION → CONFIRMED → IN_TRANSIT → 
DELIVERED → INVOICE_RECEIVED → PAYMENT_PROCESSED → COMPLETED
```

### Vendor Status
```
ACTIVE, INACTIVE, SUSPENDED, BLACKLISTED
```

### Project Status
```
ACTIVE, ON_HOLD, COMPLETED, ARCHIVED
```

### Document Type
```
INVOICE, RECEIPT, CONTRACT, SPECIFICATION, AGREEMENT, 
CERTIFICATE, REPORT, OTHER
```

### File Status
```
active, deleted
```

---

## Key Database Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| vendor | Supplier master | id, name, gstin, email, phone |
| vendor_order | POs from vendors | id, vendor_id, po_number, amount, status |
| vendor_payment | Payments to vendors | id, vendor_id, vendor_order_id, amount, status |
| client_po | Client POs (auto-parsed) | id, client_id, po_number, vendor_id, total |
| project | Project portfolio | id, name, budget, status, owner |
| upload_session | File upload sessions | session_id, client_id, ttl_hours, status |
| upload_file | Files in sessions | id, session_id, file_size, mime_type, status |
| document | Document storage | id, filename, document_type, project_id |

---

## Common Query Parameter Combinations

### Get vendors by status
```
/api/vendors?status=ACTIVE&limit=20&offset=0
```

### Get pending payments for vendor
```
/api/payments?vendor_id=42&status=PENDING&limit=50
```

### Get project POs completed in date range
```
/api/vendor-orders?project_id=1&status=COMPLETED
&date_from=2026-01-01&date_to=2026-02-28
```

### Search invoices for vendor
```
/api/documents?vendor_id=42&document_type=INVOICE&limit=20
```

### Get client billing summary
```
/api/billing/clients/1/summary?start_date=2026-01-01&end_date=2026-02-28
```

---

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PUT/DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Validation error, invalid parameters |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate entry, business rule violation |
| 413 | Payload Too Large | File exceeded size limit |
| 500 | Server Error | Unexpected error on server |

---

## Rate Limiting

Currently: No rate limiting in development

Production limits (planned):
- 1000 requests/minute per user
- 100 MB upload/day per user
- 100 items/request for batch operations

---

## Authentication

Current: No authentication required (development)

Production: Bearer token required
```
Authorization: Bearer {jwt_token}
```

---

## File Upload Limits

- Max file size: 50 MB
- Auto-compression: Enabled for .xlsx, .xls, .csv
- Session TTL: Max 72 hours
- Supported types: Excel, CSV, PDF

---

## Pagination Best Practices

```python
# Get all items with pagination
items = []
offset = 0
limit = 100

while True:
    response = get(f"/api/endpoint?limit={limit}&offset={offset}")
    items.extend(response["data"])
    
    if len(items) >= response["total"]:
        break
    
    offset += limit
```

---

## Performance Tips

1. **Use appropriate limit values**
   - Too small (5): Many requests, slower
   - Too large (100+): Large responses, slower
   - Optimal: 20-50

2. **Filter before fetching**
   - Use status, date filters
   - Reduces data transferred
   - Faster processing

3. **Use bulk operations**
   - Batch 100+ items for creation
   - Use bulk-process for payments
   - Reduces API calls

4. **Cache results**
   - Cache vendor list (5 min)
   - Cache project summaries (10 min)
   - Cache payment summaries (15 min)

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `DUPLICATE_GSTIN` | Vendor GSTIN already exists | Use different GSTIN or update existing |
| `DUPLICATE_PO_NUMBER` | PO number already exists | Use unique PO number with vendor_id |
| `VENDOR_NOT_FOUND` | Invalid vendor_id | Check vendor exists before creating PO |
| `INVALID_AMOUNT` | Amount <= 0 or incorrect format | Ensure amount > 0 and numeric |
| `SESSION_EXPIRED` | Upload session TTL exceeded | Create new session and re-upload |
| `FILE_TOO_LARGE` | File exceeds 50 MB limit | Reduce file size or split upload |

---

## Testing Tips

### Use Postman Collection
```
File: Postman_Complete_Backend_Collection.json
- Pre-configured for localhost:8000
- Uses variables for reusable data
- Includes all 60+ endpoints
```

### Test Data Initialization
```python
# Create test vendor
vendor = {"name": "Test Vendor", "email": "test@vendor.com", 
          "gstin": "27AABFU6954R1Z1"}

# Create test PO
po = {"vendor_id": 42, "po_number": "TEST-001", 
      "amount": 100000, "status": "PENDING_CONFIRMATION"}

# Create test payment
payment = {"vendor_id": 42, "vendor_order_id": 5, 
           "amount": 100000, "status": "PENDING"}
```

---

## Module Load Order

1. **Vendor** - Create vendors first
2. **Vendor Orders** - Vendors must exist
3. **Vendor Payments** - Orders must exist
4. **Projects** - Standalone, but needs vendors/orders to link
5. **File Uploads** - Sessions are independent
6. **Billing PO** - Vendors and clients
7. **Documents** - All modules optional

---

## Support Resources

1. [Integration Master Guide](INTEGRATION_MASTER_GUIDE.md)
2. [File Upload Integration](INTEGRATION_FILE_UPLOAD.md)
3. [Vendors Integration](INTEGRATION_VENDORS.md)
4. [Payments Integration](INTEGRATION_PAYMENTS.md)
5. [PO Integration](INTEGRATION_VENDOR_ORDERS.md)
6. [Projects Integration](INTEGRATION_PROJECTS.md)
7. [Billing Integration](INTEGRATION_BILLING_PO.md)
8. [Documents Integration](INTEGRATION_DOCUMENTS.md)

---

## Version Info

API Version: 1.0
Backend: FastAPI 0.104.1
Database: PostgreSQL
Python: 3.13+

Last Updated: 2026-02-17

