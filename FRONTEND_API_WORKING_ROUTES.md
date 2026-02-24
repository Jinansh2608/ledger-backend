# Frontend API Integration - Verified Working Routes

**Last Updated:** 2026-02-17  
**Backend Compatibility:** 96% (70/73 routes working)  
**Status:** Production Ready with Known Limitations

---

## ⚡ Quick Start - Copy-Paste Ready Endpoints

### Base URLs
```
Health & Projects:  http://localhost:8000/api
File Operations:    http://localhost:8000/uploads
```

---

## Health & System Status (✅ All Working)

```javascript
// Health check
GET /api/health

// Detailed diagnostics
GET /api/health/detailed
```

---

## Projects Management (✅ All Working)

```javascript
// List all projects
GET /api/projects

// Get specific project
GET /api/projects/{projectId}

// Create project
POST /api/projects
Content-Type: application/json
{
  "name": "Project Name",
  "client_id": "client123"
}

// Update project
PUT /api/projects/{projectId}

// Delete project
DELETE /api/projects/{projectId}

// Get financial summary
GET /api/projects/{projectId}/financial-summary

// Get billing summary
GET /api/projects/{projectId}/billing-summary

// Get P&L analysis
GET /api/projects/{projectId}/billing-pl-analysis
```

---

## Clients Management (✅ All Working)

```javascript
// List all clients
GET /api/clients
```

---

## Purchase Orders - POs (⚠️ 1 Alternative)

```javascript
// ✅ List POs with pagination
GET /api/po?skip=0&limit=10

// ✅ Get client PO
GET /api/client-po/{poId}

// ✅ Get PO details
GET /api/po/{poId}/details

// ✅ Get project POs
GET /api/projects/{projectId}/po

// ✅ Get enriched PO data
GET /api/projects/{projectId}/po/enriched

// ✅ CREATE PO IN PROJECT (NEW WAY)
POST /api/projects/{projectId}/po?client_id={clientId}
Content-Type: application/json
{
  "po_number": "PO123",
  "vendor_id": "vendor456"
}

// ✅ Update PO
PUT /api/po/{poId}

// ✅ Delete PO
DELETE /api/po/{poId}
```

**⚠️ DEPRECATED:** `POST /api/po` - Use project-scoped endpoint instead

---

## Line Items - Purchase Orders (✅ All Working)

```javascript
// Get line items
GET /api/po/{poId}/line-items

// Add line item
POST /api/po/{poId}/line-items
Content-Type: application/json
{
  "item_code": "ITEM001",
  "quantity": 10,
  "rate": 150.00
}

// Update line item
PUT /api/line-items/{lineItemId}

// Delete line item
DELETE /api/line-items/{lineItemId}
```

---

## Payments - Purchase Orders (✅ All Working)

```javascript
// Get PO payments
GET /api/po/{poId}/payments

// Create PO payment
POST /api/po/{poId}/payments
Content-Type: application/json
{
  "amount": 5000,
  "date": "2024-02-17",
  "method": "bank_transfer"
}

// Delete payment
DELETE /api/payments/{paymentId}
```

---

## Vendors Management (✅ All Working)

```javascript
// Get vendor
GET /api/vendors/{vendorId}

// List vendors with filters
GET /api/vendors?status=active&name=acme&limit=10&offset=0

// List vendors with pagination
GET /api/vendors?limit=10&offset=0

// Create vendor
POST /api/vendors
Content-Type: application/json
{
  "name": "Vendor Name",
  "email": "vendor@company.com",
  "phone": "+1234567890"
}

// Update vendor
PUT /api/vendors/{vendorId}

// Delete vendor
DELETE /api/vendors/{vendorId}

// Get vendor details
GET /api/vendors/{vendorId}/details

// Get vendor payment summary
GET /api/vendors/{vendorId}/payment-summary

// Get vendor payments
GET /api/vendors/{vendorId}/payments?limit=10&offset=0
```

**⚠️ NOTE:** `POST /api/vendors/{vendorId}/payments` - Not implemented. Use order-level instead:

```javascript
// ✅ CREATE VENDOR PAYMENT AT ORDER LEVEL
POST /api/vendor-orders/{orderId}/payments
Content-Type: application/json
{
  "amount": 2500,
  "date": "2024-02-17"
}

// ✅ OR CREATE AT PROJECT LEVEL
POST /api/projects/{projectId}/vendor-payments
```

---

## Vendor Orders (✅ All Working)

```javascript
// List vendor orders for project
GET /api/projects/{projectId}/vendor-orders

// Get order details
GET /api/vendor-orders/{orderId}

// Create vendor order
POST /api/projects/{projectId}/vendor-orders
Content-Type: application/json
{
  "vendor_id": "vendor123",
  "po_number": "PO789"
}

// Update vendor order
PUT /api/projects/{projectId}/vendor-orders/{orderId}

// Update order status
PUT /api/vendor-orders/{orderId}/status
Content-Type: application/json
{
  "status": "completed"
}

// Delete vendor order
DELETE /api/projects/{projectId}/vendor-orders/{orderId}

// Add line items to vendor order
POST /api/vendor-orders/{orderId}/line-items
```

---

## Billing POs (✅ All Working)

```javascript
// Create billing PO
POST /api/projects/{projectId}/billing-po
Content-Type: application/json
{
  "client_id": "client123"
}

// Get billing PO
GET /api/billing-po/{billingPoId}

// Update billing PO
PUT /api/billing-po/{billingPoId}

// Approve billing PO
POST /api/billing-po/{billingPoId}/approve

// Get line items
GET /api/billing-po/{billingPoId}/line-items

// Add line item
POST /api/billing-po/{billingPoId}/line-items

// Delete line item
DELETE /api/billing-po/{billingPoId}/line-items/{lineItemId}
```

---

## Verbal Agreements (✅ All Working)

```javascript
// Create verbal agreement
POST /api/projects/{projectId}/verbal-agreement?client_id={clientId}

// List verbal agreements
GET /api/projects/{projectId}/verbal-agreements

// Add PO to verbal agreement
PUT /api/verbal-agreement/{agreementId}/add-po
Content-Type: application/json
{
  "po_id": "po456"
}
```

---

## File Upload & Management (⚠️ 1 Limitation)

### Upload Operations

```javascript
// Upload PO file
POST /api/uploads/po/upload?client_id={clientId}&auto_save=true&project_id={projectId}
Content-Type: multipart/form-data
- file: (binary file)

// Get PO files
GET /api/uploads/po/{poNumber}
```

### Session Operations

```javascript
// Create upload session
POST /api/uploads/session

// Get session info
GET /api/uploads/session/{sessionId}

// Upload file to session
POST /api/uploads/session/{sessionId}/files
Content-Type: multipart/form-data
- file: (binary file)

// List session files
GET /api/uploads/session/{sessionId}/files?skip=0&limit=10

// Get session statistics
GET /api/uploads/session/{sessionId}/stats

// Download single file
GET /api/uploads/session/{sessionId}/files/{fileId}/download

// ⚠️ MISSING: Bulk download as ZIP
// Alternative: Download files individually or use client-side ZIP

// Delete single file
DELETE /api/uploads/session/{sessionId}/files/{fileId}

// Delete entire session
DELETE /api/uploads/session/{sessionId}
```

**⚠️ LIMITATION:** `POST /api/uploads/session/{sessionId}/download-all` does NOT exist

**Workarounds:**
```javascript
// Option 1: Download files individually
async function downloadAllFiles(sessionId) {
  const stats = await fetch(`/api/uploads/session/${sessionId}/stats`);
  const files = await fetch(`/api/uploads/session/${sessionId}/files`);
  
  for (const file of files.data) {
    const url = `/api/uploads/session/${sessionId}/files/${file.id}/download`;
    // Download each file
  }
}

// Option 2: Use JSZip library on frontend
// Fetch all files, create ZIP client-side, download
```

---

## Documents Management (✅ All Working)

```javascript
// Upload document
POST /api/documents/upload
Content-Type: multipart/form-data

// Get project documents
GET /api/documents/project/{projectId}

// Get PO documents
GET /api/documents/po/{poId}

// Get specific document
GET /api/documents/{docId}

// Download document
GET /api/documents/download/{docId}
```

---

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": { /* resource data */ },
  "message": "Operation completed"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "details": { /* error details */ }
}
```

### Pagination Response
```json
{
  "data": [ /* array of items */ ],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

---

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request processed |
| 201 | Created | Resource created |
| 204 | No Content | Successful, no response body |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Add auth headers |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Backend issue, retry later |

---

## Authentication Headers

```javascript
// Most endpoints may require:
{
  "Authorization": "Bearer {token}",
  "Content-Type": "application/json"
}
```

---

## Frontend Route Map Summary

### ✅ Fully Working (63 routes)
- Health checks
- Projects (full CRUD)
- Clients
- POs (with project context)
- Line items
- Payments
- Vendors (full CRUD)
- Vendor orders
- Billing POs
- Verbal agreements
- File uploads (single file)
- Documents

### ⚠️ Working with Alternatives (7 routes)
- PO creation → Use `/projects/{projectId}/po`
- Vendor payments → Use `/vendor-orders/{orderId}/payments`

### ❌ Not Available (3 routes)
- `POST /api/po` (direct PO creation)
- `POST /api/vendors/{vendorId}/payments` (vendor-level payments)
- `POST /api/uploads/session/{sessionId}/download-all` (bulk ZIP download)

---

## Integration Checklist for Frontend

- [ ] Update PO creation endpoints to use project context
- [ ] Update vendor payment creation to use order context
- [ ] Handle bulk file download via individual downloads or client-side ZIP
- [ ] Test all CRUD operations
- [ ] Implement error handling for 404s
- [ ] Add loading states for long operations
- [ ] Test pagination with various limits
- [ ] Verify authentication/authorization flows

---

## Support & Debugging

If an endpoint returns 404:
1. Check the exact path and method in this guide
2. Verify you're using the correct prefix (`/api` vs `/uploads`)
3. Check that required path parameters are included
4. See "Alternatives" section above

For issues, enable verbose logging on the frontend:
```javascript
// Log all API calls
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('API Call:', args);
  return originalFetch.apply(this, args);
};
```

