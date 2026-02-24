# Complete Backend Routes & Functions Reference

**Last Updated:** February 17, 2026  
**Total Routes:** 84+ API Endpoints  
**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api`

---

## Table of Contents

1. [Health & Diagnostics](#health--diagnostics)
2. [Clients](#clients)
3. [Projects](#projects)
4. [Purchase Orders (POs)](#purchase-orders-pos)
5. [Line Items](#line-items)
6. [Payments](#payments)
7. [Vendors](#vendors)
8. [Vendor Orders](#vendor-orders)
9. [Vendor Payments](#vendor-payments)
10. [Vendor Payment Links](#vendor-payment-links)
11. [Billing POs](#billing-pos)
12. [Verbal Agreements](#verbal-agreements)
13. [Proforma Invoices](#proforma-invoices)
14. [Documents](#documents)
15. [File Uploads](#file-uploads)
16. [Misc Routes](#misc-routes)

---

## Health & Diagnostics

### Module: `app/apis/health.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 1 | `GET` | `/api/health` | `health_check()` | Basic health check - returns 200 if API is running |
| 2 | `GET` | `/api/health/detailed` | `detailed_health_check()` | Detailed health with DB connection status, pool info |

---

## Clients

### Module: `app/apis/client_po.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 3 | `GET` | `/api/clients` | `list_clients()` | Get all clients in the system |
| 4 | `GET` | `/api/client-po/{client_po_id}` | `get_client_po()` | Get specific client PO details |

---

## Projects

### Module: `app/apis/projects.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 5 | `GET` | `/api/projects` | `list_projects()` | List all projects with pagination |
| 6 | `GET` | `/api/projects/{project_id}` | `get_project()` | Get specific project details |
| 7 | `POST` | `/api/projects` | `create_project()` | Create new project |
| 8 | `PUT` | `/api/projects/{project_id}` | `update_project()` | Update project details |
| 9 | `DELETE` | `/api/projects/{project_id}` | `delete_project()` | Delete project |
| 10 | `GET` | `/api/projects/search` | `search_projects()` | Search projects by query parameter |

---

## Purchase Orders (POs)

### Module: `app/apis/po_management.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 11 | `GET` | `/api/po` | `list_po()` | List all POs with pagination (skip, limit) |
| 12 | `GET` | `/api/po/{po_id}` | `get_po()` | Get specific PO |
| 13 | `GET` | `/api/po/{po_id}/details` | `get_po_details()` | Get detailed PO information with line items |
| 14 | `POST` | `/api/projects/{project_id}/po` | `create_po()` | Create new PO within project (requires client_id query param) |
| 15 | `GET` | `/api/projects/{project_id}/po` | `get_project_pos()` | Get all POs for a project |
| 16 | `PUT` | `/api/po/{client_po_id}` | `update_po()` | Update PO details |
| 17 | `DELETE` | `/api/po/{client_po_id}` | `delete_po()` | Delete PO |
| 18 | `GET` | `/api/projects/{project_id}/po/enriched` | `get_project_po_enriched()` | Get POs with enriched data (vendor info, etc) |
| 19 | `POST` | `/api/projects/{project_id}/po/{client_po_id}/attach` | `attach_po()` | Attach existing PO to project |
| 20 | `PUT` | `/api/projects/{project_id}/po/{client_po_id}/set-primary` | `set_primary_po()` | Set PO as primary for project |

---

## Line Items

### Module: `app/apis/po_management.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 21 | `POST` | `/api/po/{client_po_id}/line-items` | `add_line_item()` | Add line item to PO |
| 22 | `GET` | `/api/po/{client_po_id}/line-items` | `get_line_items()` | Get all line items for PO |
| 23 | `PUT` | `/api/line-items/{line_item_id}` | `update_line_item()` | Update line item details |
| 24 | `DELETE` | `/api/line-items/{line_item_id}` | `delete_line_item()` | Delete line item from PO |

---

## Payments

### Module: `app/apis/payments.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 25 | `POST` | `/api/po/{po_id}/payments` | `create_po_payment()` | Record payment for PO |
| 26 | `GET` | `/api/po/{po_id}/payments` | `get_po_payments()` | Get all payments for PO |
| 27 | `PUT` | `/api/payments/{payment_id}` | `update_payment()` | Update payment details |
| 28 | `DELETE` | `/api/payments/{payment_id}` | `delete_payment()` | Delete payment |

---

## Vendors

### Module: `app/apis/vendors.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 29 | `POST` | `/api/vendors` | `create_vendor()` | Create new vendor |
| 30 | `GET` | `/api/vendors` | `list_vendors()` | List vendors with filters (status, name) and pagination (limit, offset) |
| 31 | `GET` | `/api/vendors/{vendor_id}` | `get_vendor()` | Get vendor details |
| 32 | `PUT` | `/api/vendors/{vendor_id}` | `update_vendor()` | Update vendor information |
| 33 | `DELETE` | `/api/vendors/{vendor_id}` | `delete_vendor()` | Delete vendor |
| 34 | `GET` | `/api/vendors/{vendor_id}/payments` | `get_vendor_payments()` | Get vendor payment history |
| 35 | `GET` | `/api/vendors/{vendor_id}/payment-summary` | `get_vendor_payment_summary()` | Get vendor payment summary and statistics |
| 36 | `GET` | `/api/projects/{project_id}/vendor-summary` | `get_project_vendor_summary()` | Get summary of all vendors in project |

---

## Vendor Orders

### Module: `app/apis/vendor_orders.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 37 | `POST` | `/api/projects/{project_id}/vendor-orders` | `create_vendor_order()` | Create vendor order for project |
| 38 | `POST` | `/api/projects/{project_id}/vendor-orders/bulk` | `create_bulk_vendor_orders()` | Bulk create vendor orders |
| 39 | `GET` | `/api/projects/{project_id}/vendor-orders` | `list_vendor_orders()` | List vendor orders for project |
| 40 | `GET` | `/api/vendor-orders/{vendor_order_id}` | `get_vendor_order()` | Get vendor order details |
| 41 | `PUT` | `/api/projects/{project_id}/vendor-orders/{vendor_order_id}` | `update_vendor_order()` | Update vendor order |
| 42 | `PUT` | `/api/vendor-orders/{vendor_order_id}/status` | `update_vendor_order_status()` | Update order status (pending, confirmed, delivered, etc) |
| 43 | `DELETE` | `/api/projects/{project_id}/vendor-orders/{vendor_order_id}` | `delete_vendor_order()` | Delete vendor order |
| 44 | `POST` | `/api/vendor-orders/{vendor_order_id}/line-items` | `add_vendor_order_line_item()` | Add line item to vendor order |
| 45 | `GET` | `/api/vendor-orders/{vendor_order_id}/line-items` | `get_vendor_order_line_items()` | Get line items for vendor order |
| 46 | `PUT` | `/api/vendor-line-items/{item_id}` | `update_vendor_line_item()` | Update vendor order line item |
| 47 | `DELETE` | `/api/vendor-line-items/{item_id}` | `delete_vendor_line_item()` | Delete vendor order line item |
| 48 | `POST` | `/api/vendor-orders/{vendor_order_id}/link-payment` | `link_payment_to_vendor_order()` | Link payment to vendor order |
| 49 | `GET` | `/api/vendor-orders/{vendor_order_id}/profit-analysis` | `get_vendor_order_profit_analysis()` | Get profit/cost analysis for vendor order |

---

## Vendor Payments

### Module: `app/apis/vendor_payments.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 50 | `POST` | `/api/vendor-orders/{vendor_order_id}/payments` | `create_vendor_payment()` | Record payment for vendor order |
| 51 | `GET` | `/api/vendor-orders/{vendor_order_id}/payments` | `get_vendor_payments()` | Get payments for vendor order |
| 52 | `PUT` | `/api/vendor-payments/{payment_id}` | `update_vendor_payment()` | Update vendor payment |
| 53 | `DELETE` | `/api/vendor-payments/{payment_id}` | `delete_vendor_payment()` | Delete vendor payment |
| 54 | `POST` | `/api/projects/{project_id}/vendor-payments` | `create_project_vendor_payment()` | Create vendor payment at project level |

---

## Vendor Payment Links

### Module: `app/apis/vendor_payment_links.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 55 | `POST` | `/api/vendor-orders/{vendor_order_id}/link-payment` | `link_payment()` | Link payment to vendor order (duplicate function) |
| 56 | `GET` | `/api/vendor-orders/{vendor_order_id}/linked-payments` | `get_linked_payments()` | Get all linked payments for vendor order |
| 57 | `GET` | `/api/vendor-orders/{vendor_order_id}/payment-summary` | `get_payment_summary()` | Get payment summary for vendor order |
| 58 | `DELETE` | `/api/vendor-orders/{vendor_order_id}/payments/{payment_id}` | `unlink_payment()` | Unlink payment from vendor order |

---

## Billing POs

### Module: `app/apis/billing_po.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 59 | `POST` | `/api/projects/{project_id}/billing-po` | `create_billing_po()` | Create billing PO for project |
| 60 | `GET` | `/api/billing-po/{billing_po_id}` | `get_billing_po()` | Get billing PO details |
| 61 | `PUT` | `/api/billing-po/{billing_po_id}` | `update_billing_po()` | Update billing PO |
| 62 | `POST` | `/api/billing-po/{billing_po_id}/approve` | `approve_billing_po()` | Approve billing PO |
| 63 | `POST` | `/api/billing-po/{billing_po_id}/line-items` | `add_billing_line_item()` | Add line item to billing PO |
| 64 | `GET` | `/api/billing-po/{billing_po_id}/line-items` | `get_billing_line_items()` | Get line items for billing PO |
| 65 | `DELETE` | `/api/billing-po/{billing_po_id}/line-items/{line_item_id}` | `delete_billing_line_item()` | Delete billing line item |
| 66 | `GET` | `/api/projects/{project_id}/billing-summary` | `get_billing_summary()` | Get billing summary for project |
| 67 | `GET` | `/api/projects/{project_id}/billing-pl-analysis` | `get_billing_pl_analysis()` | Get P&L analysis for project billing |
| 68 | `GET` | `/api/projects/{project_id}/pl-analysis` | `get_project_pl_analysis()` | Get project P&L analysis |

---

## Verbal Agreements

### Module: `app/apis/po_management.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 69 | `POST` | `/api/projects/{project_id}/verbal-agreement` | `create_verbal_agreement()` | Create verbal agreement (query param: client_id) |
| 70 | `GET` | `/api/projects/{project_id}/verbal-agreements` | `get_verbal_agreements()` | Get all verbal agreements for project |
| 71 | `PUT` | `/api/verbal-agreement/{agreement_id}/add-po` | `add_po_to_agreement()` | Add PO to verbal agreement |

---

## Financial Summary

### Module: `app/apis/po_management.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 72 | `GET` | `/api/projects/{project_id}/financial-summary` | `get_financial_summary()` | Get project financial summary with totals, payments, balance |

---

## Proforma Invoices

### Module: `app/apis/proforma_invoice.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 73 | `POST` | `/api/proforma-invoice/upload` | `upload_proforma_invoice()` | Upload and parse proforma invoice |
| 74 | `GET` | `/api/proforma-invoice/validate/{client_po_id}` | `validate_proforma_invoice()` | Validate proforma invoice |
| 75 | `POST` | `/api/proforma-invoice/bulk` | `bulk_upload_proforma()` | Bulk upload proforma invoices |

---

## Documents

### Module: `app/apis/documents.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 76 | `POST` | `/api/documents/upload` | `upload_document()` | Upload document (multipart/form-data) |
| 77 | `GET` | `/api/documents/project/{project_id}` | `get_project_documents()` | Get documents for project |
| 78 | `GET` | `/api/documents/po/{client_po_id}` | `get_po_documents()` | Get documents for PO |
| 79 | `GET` | `/api/documents/{doc_id}` | `get_document()` | Get document details |
| 80 | `GET` | `/api/documents/download/{doc_id}` | `download_document()` | Download document file |

---

## File Uploads

### Module: `app/modules/file_uploads/controllers/routes.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 81 | `POST` | `/api/uploads/session` | `create_upload_session()` | Create new upload session |
| 82 | `GET` | `/api/uploads/session/{session_id}` | `get_session()` | Get upload session details |
| 83 | `POST` | `/api/uploads/session/{session_id}/files` | `upload_file()` | Upload file to session (multipart/form-data) with auto-parse |
| 84 | `GET` | `/api/uploads/session/{session_id}/files` | `list_session_files()` | List files in session with pagination |
| 85 | `GET` | `/api/uploads/session/{session_id}/files/{file_id}/download` | `download_file()` | Download file from session |
| 86 | `DELETE` | `/api/uploads/session/{session_id}/files/{file_id}` | `delete_file()` | Delete file from session |
| 87 | `DELETE` | `/api/uploads/session/{session_id}` | `delete_session()` | Delete entire upload session |
| 88 | `GET` | `/api/uploads/session/{session_id}/stats` | `get_session_stats()` | Get session statistics (file count, size) |
| 89 | `POST` | `/api/uploads/po/upload` | `upload_po()` | Upload PO file with auto-parsing (query params: client_id, auto_save, project_id) |
| 90 | `GET` | `/api/uploads/po/{po_number}` | `get_po_uploaded_files()` | Get uploaded files for PO number |

---

## Misc Routes

### Module: `app/apis/po_management.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 91 | `POST` | `/api/projects` | `create_project_from_po()` | Create project from PO (duplicate function) |
| 92 | `DELETE` | `/api/projects` | `delete_all_projects()` | Delete all projects (dangerous - clears database) |

### Module: `app/apis/bajaj_po.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 93 | `POST` | `/api/bajaj-po/bulk` | `upload_bajaj_bulk_po()` | Bulk upload Bajaj POs |

### Module: `app/apis/client_po.py`

| # | Method | Endpoint | Function | Purpose |
|---|--------|----------|----------|---------|
| 94 | `POST` | `/api/po/upload` | `upload_po_file()` | Upload PO file from client (alternative endpoint) |

---

## Complete Route Summary by HTTP Method

### GET Routes (35 endpoints)
```
GET /api/health
GET /api/health/detailed
GET /api/clients
GET /api/client-po/{client_po_id}
GET /api/projects
GET /api/projects/{project_id}
GET /api/projects/search
GET /api/po
GET /api/po/{po_id}
GET /api/po/{po_id}/details
GET /api/projects/{project_id}/po
GET /api/projects/{project_id}/po/enriched
GET /api/po/{client_po_id}/line-items
GET /api/po/{po_id}/payments
GET /api/vendors
GET /api/vendors/{vendor_id}
GET /api/vendors/{vendor_id}/payments
GET /api/vendors/{vendor_id}/payment-summary
GET /api/projects/{project_id}/vendor-summary
GET /api/projects/{project_id}/vendor-orders
GET /api/vendor-orders/{vendor_order_id}
GET /api/vendor-orders/{vendor_order_id}/line-items
GET /api/vendor-orders/{vendor_order_id}/profit-analysis
GET /api/vendor-orders/{vendor_order_id}/payments
GET /api/vendor-orders/{vendor_order_id}/linked-payments
GET /api/vendor-orders/{vendor_order_id}/payment-summary
GET /api/billing-po/{billing_po_id}
GET /api/billing-po/{billing_po_id}/line-items
GET /api/projects/{project_id}/billing-summary
GET /api/projects/{project_id}/billing-pl-analysis
GET /api/projects/{project_id}/pl-analysis
GET /api/projects/{project_id}/verbal-agreements
GET /api/projects/{project_id}/financial-summary
GET /api/proforma-invoice/validate/{client_po_id}
GET /api/documents/project/{project_id}
GET /api/documents/po/{client_po_id}
GET /api/documents/{doc_id}
GET /api/documents/download/{doc_id}
GET /api/uploads/session/{session_id}
GET /api/uploads/session/{session_id}/files
GET /api/uploads/session/{session_id}/files/{file_id}/download
GET /api/uploads/session/{session_id}/stats
GET /api/uploads/po/{po_number}
```

### POST Routes (40 endpoints)
```
POST /api/projects
POST /api/projects/{project_id}/po
POST /api/po/{client_po_id}/line-items
POST /api/po/{po_id}/payments
POST /api/vendors
POST /api/projects/{project_id}/vendor-orders
POST /api/projects/{project_id}/vendor-orders/bulk
POST /api/vendor-orders/{vendor_order_id}/line-items
POST /api/vendor-orders/{vendor_order_id}/link-payment
POST /api/vendor-orders/{vendor_order_id}/payments
POST /api/projects/{project_id}/vendor-payments
POST /api/projects/{project_id}/verbal-agreement
POST /api/projects/{project_id}/billing-po
POST /api/billing-po/{billing_po_id}/line-items
POST /api/billing-po/{billing_po_id}/approve
POST /api/verbal-agreement/{agreement_id}/add-po
POST /api/proforma-invoice/upload
POST /api/proforma-invoice/bulk
POST /api/documents/upload
POST /api/uploads/session
POST /api/uploads/session/{session_id}/files
POST /api/uploads/po/upload
POST /api/po/upload
POST /api/bajaj-po/bulk
POST /api/projects/{project_id}/po/{client_po_id}/attach
```

### PUT Routes (13 endpoints)
```
PUT /api/projects/{project_id}
PUT /api/po/{client_po_id}
PUT /api/line-items/{line_item_id}
PUT /api/payments/{payment_id}
PUT /api/vendors/{vendor_id}
PUT /api/projects/{project_id}/vendor-orders/{vendor_order_id}
PUT /api/vendor-orders/{vendor_order_id}/status
PUT /api/vendor-line-items/{item_id}
PUT /api/vendor-payments/{payment_id}
PUT /api/billing-po/{billing_po_id}
PUT /api/projects/{project_id}/po/{client_po_id}/set-primary
```

### DELETE Routes (16 endpoints)
```
DELETE /api/projects/{project_id}
DELETE /api/po/{client_po_id}
DELETE /api/line-items/{line_item_id}
DELETE /api/payments/{payment_id}
DELETE /api/vendors/{vendor_id}
DELETE /api/projects/{project_id}/vendor-orders/{vendor_order_id}
DELETE /api/vendor-line-items/{item_id}
DELETE /api/vendor-payments/{payment_id}
DELETE /api/vendor-orders/{vendor_order_id}/payments/{payment_id}
DELETE /api/billing-po/{billing_po_id}/line-items/{line_item_id}
DELETE /api/uploads/session/{session_id}/files/{file_id}
DELETE /api/uploads/session/{session_id}
DELETE /api/projects
```

---

## Quick Stats

| Metric | Count |
|--------|-------|
| **Total Routes** | 94 |
| **GET Routes** | 42 |
| **POST Routes** | 25 |
| **PUT Routes** | 13 |
| **DELETE Routes** | 14 |
| **API Modules** | 15 |

---

## Authentication

All routes (except `/api/health`) require authentication:

```http
Authorization: Bearer {token}
```

---

## Common Query Parameters

### Pagination
```
skip: Integer (default: 0) - Number of records to skip
limit: Integer (default: 10) - Number of records to return
offset: Integer (default: 0) - Alias for skip
```

### Filtering
```
status: String - Filter by status
name: String - Filter by name
client_id: Integer - Filter by client
project_id: Integer - Filter by project
```

### File Upload
```
client_id: Integer - Required for upload sessions
auto_save: Boolean - Auto-save parsed data
project_id: Integer - Link to project
auto_parse: Boolean - Enable auto-parsing
```

---

## Response Formats

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

### List Response
```json
{
  "data": [ /* array of items */ ],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

---

## HTTP Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Successful, no body |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Auth required |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Backend error |

---

## Common File Upload Parameters

### Upload Session
- `client_id` - Required: Client identifier
- `metadata` - Optional: JSON metadata object
- `ttl_hours` - Optional: Session TTL (default: 24)

### File Upload
- `file` - Required: File to upload (multipart/form-data)
- `auto_parse` - Optional: Enable auto-parsing (default: false)
- `uploaded_by` - Optional: User identifier
- `po_number` - Optional: PO number reference

---

This document provides complete reference for all 94+ API routes with their functions, HTTP methods, endpoints, and purposes.
