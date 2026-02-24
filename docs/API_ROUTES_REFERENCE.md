# Nexgen ERP Finance API - Complete Route Reference

**Version**: 1.0.0 | **Last Updated**: February 17, 2026

---

## Quick Reference

**Base URL**: `http://localhost:8000/api`  
**Auth**: HTTP Basic Auth (Base64-encoded `username:password`)  
**Content-Type**: `application/json`

---

## Health & Status

### Get Health Status
```
GET /health
```
**Function**: Check if API is running  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "status": "UP",
    "service": "Nexgen ERP - Finance API",
    "database": "UP",
    "version": "1.0.0",
    "timestamp": "2026-02-17T10:30:00"
  }
}
```

### Get Detailed Health
```
GET /health/detailed
```
**Function**: Get detailed system metrics  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "status": "UP",
    "timestamp": "2026-02-17T10:30:00",
    "service": "Nexgen ERP - Finance API",
    "version": "1.0.0",
    "environment": "production",
    "components": {
      "api": "UP",
      "database": "UP"
    },
    "database_tables": 18
  }
}
```

---

## Clients

### Get Supported Clients
```
GET /clients
```
**Function**: Get list of supported PO clients  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "clients": [
      { "id": 1, "name": "Bajaj" },
      { "id": 2, "name": "Dava India" }
    ],
    "count": 2
  }
}
```

---

## File Upload & Sessions

### Create Upload Session
```
POST /uploads/session
```
**Function**: Create new file upload session  
**Request**:
```json
{
  "po_number": "PO-2026-001",
  "created_by": "user@example.com",
  "description": "Monthly PO batch"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "po_number": "PO-2026-001",
    "status": "active",
    "created_at": "2026-02-17T10:30:00",
    "file_count": 0
  }
}
```

### Upload File to Session
```
POST /uploads/session/{session_id}/files
```
**Function**: Upload file to session (multipart)  
**Request**:
```
Form Data:
- file: <binary file>
- uploaded_by: "user@example.com"
- po_number: "PO-2026-001"
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "file_id": "650e8400-e29b-41d4-a716-446655440001",
    "original_filename": "Bajaj_PO.xlsx",
    "size": 25000,
    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "upload_timestamp": "2026-02-17T10:30:00",
    "status": "success",
    "parsing_status": "completed",
    "parsed_data": {
      "po_number": "BJ-2026-001",
      "po_value": 500000,
      "vendor_name": "Bajaj Auto Ltd"
    }
  }
}
```

### Get Session Details
```
GET /uploads/session/{session_id}
```
**Function**: Get session and its files  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "po_number": "PO-2026-001",
    "status": "active",
    "created_at": "2026-02-17T10:30:00",
    "file_count": 2,
    "files": [
      {
        "file_id": "650e8400-e29b-41d4-a716-446655440001",
        "filename": "Bajaj_PO.xlsx",
        "size": 25000,
        "upload_timestamp": "2026-02-17T10:30:00"
      }
    ]
  }
}
```

### List Session Files
```
GET /uploads/session/{session_id}/files?skip=0&limit=50
```
**Function**: Paginated list of files in session  
**Request**: Query params: `skip`, `limit`  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "files": [
      {
        "file_id": "650e8400-e29b-41d4-a716-446655440001",
        "filename": "Bajaj_PO.xlsx",
        "size": 25000,
        "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "upload_timestamp": "2026-02-17T10:30:00",
        "parsing_status": "completed"
      }
    ],
    "total_count": 1,
    "skip": 0,
    "limit": 50
  }
}
```

### Download File
```
GET /uploads/session/{session_id}/files/{file_id}/download
```
**Function**: Download file (returns binary)  
**Request**: None  
**Response**: Binary file with `Content-Disposition: attachment`

### Delete File
```
DELETE /uploads/session/{session_id}/files/{file_id}
```
**Function**: Delete file from session  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "File deleted successfully"
  }
}
```

### Delete Session
```
DELETE /uploads/session/{session_id}
```
**Function**: Delete entire session  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "Session deleted successfully"
  }
}
```

---

## Purchase Orders (PO)

### Upload & Parse PO
```
POST /po/upload?client_id=1&project_id=3&auto_save=true
```
**Function**: Upload and auto-parse PO (Bajaj: client_id=1, Dava India: client_id=2)  
**Request**: Multipart form
```
Form Data:
- file: <binary PO file>
- client_id: 1 (Bajaj) or 2 (Dava India)
- project_id: 3 (optional)
- auto_save: true/false
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "status": "success",
    "client_id": 1,
    "client_name": "Bajaj",
    "po_details": {
      "po_number": "BJ-2026-001",
      "po_date": "2026-02-15",
      "po_value": 500000,
      "vendor_name": "Bajaj Auto Ltd"
    },
    "line_items": [
      {
        "description": "Item 1",
        "quantity": 100,
        "unit_price": 5000,
        "amount": 500000
      }
    ],
    "client_po_id": 42,
    "parsing_status": "completed"
  }
}
```

### Get All POs
```
GET /po?skip=0&limit=50
```
**Function**: List all POs with pagination  
**Request**: Query params: `skip`, `limit`  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "pos": [
      {
        "id": 42,
        "po_number": "BJ-2026-001",
        "po_date": "2026-02-15",
        "po_value": 500000,
        "vendor_name": "Bajaj Auto Ltd",
        "client_id": 1,
        "status": "active",
        "created_at": "2026-02-17T10:30:00",
        "updated_at": "2026-02-17T10:30:00"
      }
    ],
    "total_count": 1
  }
}
```

### Get PO Details
```
GET /client-po/{client_po_id}
```
**Function**: Get PO with line items  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 42,
    "po_number": "BJ-2026-001",
    "po_date": "2026-02-15",
    "po_value": 500000,
    "vendor_name": "Bajaj Auto Ltd",
    "line_items": [
      {
        "id": 101,
        "description": "Item 1",
        "quantity": 100,
        "unit_price": 5000,
        "amount": 500000
      }
    ]
  }
}
```

### Create PO
```
POST /po
```
**Function**: Create new PO  
**Request**:
```json
{
  "po_number": "BJ-2026-002",
  "po_date": "2026-02-16",
  "po_value": 250000,
  "vendor_name": "Supplier Ltd",
  "client_id": 1,
  "description": "Monthly order"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 43,
    "po_number": "BJ-2026-002",
    "po_date": "2026-02-16",
    "po_value": 250000,
    "vendor_name": "Supplier Ltd",
    "status": "active",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Update PO
```
PUT /po/{po_id}
```
**Function**: Update PO details  
**Request**:
```json
{
  "po_number": "BJ-2026-002",
  "po_value": 275000,
  "status": "completed"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 43,
    "po_number": "BJ-2026-002",
    "po_value": 275000,
    "status": "completed",
    "updated_at": "2026-02-17T10:35:00"
  }
}
```

### Delete PO
```
DELETE /po/{po_id}
```
**Function**: Delete PO  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "PO deleted",
    "client_po_id": 43
  }
}
```

---

## Line Items

### Add Line Item
```
POST /po/{client_po_id}/line-items
```
**Function**: Add line item to PO  
**Request**:
```json
{
  "description": "Steel Rods",
  "quantity": 50,
  "unit_price": 1000,
  "amount": 50000
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 102,
    "client_po_id": 42,
    "description": "Steel Rods",
    "quantity": 50,
    "unit_price": 1000,
    "amount": 50000,
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Get Line Items
```
GET /po/{client_po_id}/line-items
```
**Function**: Get all line items for PO  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": [
    {
      "id": 101,
      "description": "Item 1",
      "quantity": 100,
      "unit_price": 5000,
      "amount": 500000
    }
  ]
}
```

### Update Line Item
```
PUT /line-items/{line_item_id}
```
**Function**: Update line item  
**Request**:
```json
{
  "quantity": 75,
  "amount": 75000
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 101,
    "quantity": 75,
    "amount": 75000,
    "updated_at": "2026-02-17T10:35:00"
  }
}
```

### Delete Line Item
```
DELETE /line-items/{line_item_id}
```
**Function**: Delete line item  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "Line item deleted"
  }
}
```

---

## Projects

### Get All Projects
```
GET /projects?skip=0&limit=50
```
**Function**: List all projects  
**Request**: Query params: `skip`, `limit`  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "projects": [
      {
        "id": 1,
        "name": "Mumbai Office",
        "client_id": 5,
        "location": "Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "status": "active",
        "created_at": "2026-02-01T00:00:00"
      }
    ],
    "project_count": 1
  }
}
```

### Get Project Details
```
GET /projects/{project_id}
```
**Function**: Get single project  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 1,
    "name": "Mumbai Office",
    "client_id": 5,
    "location": "Mumbai",
    "city": "Mumbai",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "status": "active"
  }
}
```

### Create Project
```
POST /projects
```
**Function**: Create new project  
**Request**:
```json
{
  "name": "Delhi Warehouse",
  "client_id": 5,
  "location": "Noida",
  "city": "Delhi",
  "state": "Delhi",
  "latitude": 28.5355,
  "longitude": 77.3910
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 2,
    "name": "Delhi Warehouse",
    "location": "Noida",
    "status": "active",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Update Project
```
PUT /projects/{project_id}
```
**Function**: Update project  
**Request**:
```json
{
  "name": "Delhi Warehouse Phase 2",
  "status": "on-hold"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 2,
    "name": "Delhi Warehouse Phase 2",
    "status": "on-hold"
  }
}
```

### Delete Project
```
DELETE /projects/{project_id}
```
**Function**: Delete project  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "Project deleted"
  }
}
```

### Get Project POs
```
GET /projects/{project_id}/po
```
**Function**: Get all POs for project  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "pos": [
      {
        "id": 42,
        "po_number": "BJ-2026-001",
        "po_value": 500000
      }
    ],
    "total_project_value": 500000
  }
}
```

### Create Project PO
```
POST /projects/{project_id}/po
```
**Function**: Create PO for project  
**Request**:
```json
{
  "po_number": "PROJ-2026-001",
  "po_date": "2026-02-16",
  "po_value": 300000,
  "vendor_name": "Vendor Name"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 44,
    "project_id": 1,
    "po_number": "PROJ-2026-001",
    "po_value": 300000
  }
}
```

### Get Financial Summary
```
GET /projects/{project_id}/financial-summary
```
**Function**: Get project financial data  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "project_id": 1,
    "total_po_value": 500000,
    "total_billing_value": 450000,
    "total_vendor_order_value": 200000,
    "total_payments": 450000,
    "remaining_payable": 50000,
    "profit_loss": 250000
  }
}
```

### Search Projects
```
GET /projects/search?q=Mumbai
```
**Function**: Search projects by name  
**Request**: Query param: `q` (search term)  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "projects": [
      {
        "id": 1,
        "name": "Mumbai Office"
      }
    ],
    "project_count": 1
  }
}
```

---

## Vendors

### Get All Vendors
```
GET /vendors?status=active
```
**Function**: List all vendors  
**Request**: Query param: `status` (optional)  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "vendors": [
      {
        "id": 10,
        "name": "ABC Supplies",
        "email": "contact@abc.com",
        "phone": "+91-9876543210",
        "status": "active"
      }
    ],
    "vendor_count": 1
  }
}
```

### Get Vendor Details
```
GET /vendors/{vendor_id}
```
**Function**: Get single vendor  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 10,
    "name": "ABC Supplies",
    "email": "contact@abc.com",
    "phone": "+91-9876543210",
    "address": "Mumbai",
    "payment_terms": "Net 30",
    "active_orders": 5,
    "total_payable": 500000,
    "total_paid": 250000
  }
}
```

### Create Vendor
```
POST /vendors
```
**Function**: Create new vendor  
**Request**:
```json
{
  "name": "XYZ Ltd",
  "email": "info@xyz.com",
  "phone": "+91-8765432109",
  "address": "Delhi",
  "payment_terms": "Net 45"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 11,
    "name": "XYZ Ltd",
    "email": "info@xyz.com",
    "status": "active",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Update Vendor
```
PUT /vendors/{vendor_id}
```
**Function**: Update vendor  
**Request**:
```json
{
  "phone": "+91-7654321098",
  "payment_terms": "Net 60"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 10,
    "name": "ABC Supplies",
    "phone": "+91-7654321098",
    "payment_terms": "Net 60"
  }
}
```

### Delete Vendor
```
DELETE /vendors/{vendor_id}
```
**Function**: Delete vendor  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "Vendor deleted"
  }
}
```

### Get Vendor Payments
```
GET /vendors/{vendor_id}/payments
```
**Function**: Get vendor payment history  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "payments": [
      {
        "id": 50,
        "amount": 100000,
        "payment_date": "2026-02-10",
        "status": "completed"
      }
    ],
    "payment_count": 1
  }
}
```

---

## Vendor Orders

### Create Vendor Order
```
POST /projects/{project_id}/vendor-orders
```
**Function**: Create vendor order for project  
**Request**:
```json
{
  "vendor_id": 10,
  "po_number": "VO-2026-001",
  "amount": 50000,
  "description": "Material supply"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 30,
    "project_id": 1,
    "vendor_id": 10,
    "po_number": "VO-2026-001",
    "amount": 50000,
    "status": "pending",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Get Project Vendor Orders
```
GET /projects/{project_id}/vendor-orders
```
**Function**: List vendor orders for project  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": [
    {
      "id": 30,
      "vendor_id": 10,
      "po_number": "VO-2026-001",
      "amount": 50000,
      "status": "pending"
    }
  ]
}
```

### Get Vendor Order Details
```
GET /vendor-orders/{vendor_order_id}
```
**Function**: Get single vendor order  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 30,
    "project_id": 1,
    "vendor_id": 10,
    "po_number": "VO-2026-001",
    "amount": 50000,
    "status": "pending"
  }
}
```

### Update Vendor Order
```
PUT /projects/{project_id}/vendor-orders/{vendor_order_id}
```
**Function**: Update vendor order  
**Request**:
```json
{
  "amount": 60000,
  "description": "Updated supply"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 30,
    "amount": 60000,
    "updated_at": "2026-02-17T10:35:00"
  }
}
```

### Update Vendor Order Status
```
PUT /vendor-orders/{vendor_order_id}/status
```
**Function**: Update order status  
**Request**:
```json
{
  "status": "completed"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 30,
    "status": "completed"
  }
}
```

### Delete Vendor Order
```
DELETE /projects/{project_id}/vendor-orders/{vendor_order_id}
```
**Function**: Delete vendor order  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "Vendor order deleted"
  }
}
```

### Add Vendor Order Line Item
```
POST /vendor-orders/{vendor_order_id}/line-items
```
**Function**: Add line item to vendor order  
**Request**:
```json
{
  "description": "Steel Beams",
  "quantity": 25,
  "unit_price": 2000,
  "amount": 50000
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 90,
    "vendor_order_id": 30,
    "description": "Steel Beams",
    "quantity": 25,
    "unit_price": 2000,
    "amount": 50000
  }
}
```

---

## Payments

### Create Payment
```
POST /po/{po_id}/payments
```
**Function**: Add payment for PO  
**Request**:
```json
{
  "amount": 100000,
  "payment_date": "2026-02-17",
  "payment_method": "Bank Transfer",
  "reference_number": "TXN-12345",
  "notes": "50% advance"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 50,
    "po_id": 42,
    "amount": 100000,
    "payment_date": "2026-02-17",
    "payment_method": "Bank Transfer",
    "status": "completed",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Get PO Payments
```
GET /po/{po_id}/payments
```
**Function**: Get all payments for PO  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": [
    {
      "id": 50,
      "amount": 100000,
      "payment_date": "2026-02-17",
      "status": "completed"
    }
  ]
}
```

### Update Payment
```
PUT /payments/{payment_id}
```
**Function**: Update payment details  
**Request**:
```json
{
  "amount": 110000,
  "status": "failed"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 50,
    "amount": 110000,
    "status": "failed"
  }
}
```

### Delete Payment
```
DELETE /payments/{payment_id}
```
**Function**: Delete payment  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "success": true,
    "message": "Payment deleted"
  }
}
```

---

## Billing POs

### Create Billing PO
```
POST /projects/{project_id}/billing-po
```
**Function**: Create billing PO for project  
**Request**:
```json
{
  "po_number": "BILL-2026-001",
  "amount": 450000,
  "status": "pending"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": "bill-uuid-123",
    "project_id": 1,
    "po_number": "BILL-2026-001",
    "amount": 450000,
    "status": "pending",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Get Billing PO Details
```
GET /billing-po/{billing_po_id}
```
**Function**: Get billing PO with line items  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": "bill-uuid-123",
    "po_number": "BILL-2026-001",
    "amount": 450000,
    "line_items": [
      {
        "id": "item-uuid-1",
        "description": "Service Charges",
        "amount": 450000
      }
    ]
  }
}
```

### Get Project Billing Summary
```
GET /projects/{project_id}/billing-summary
```
**Function**: Get billing statistics for project  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "project_id": 1,
    "total_billing_value": 450000,
    "billing_count": 1,
    "approved_billing": 0,
    "pending_approval": 1
  }
}
```

### Add Billing Line Item
```
POST /billing-po/{billing_po_id}/line-items
```
**Function**: Add line item to billing PO  
**Request**:
```json
{
  "item_description": "Labour Cost - Phase 1",
  "quantity": 1,
  "unit_price": 450000,
  "amount": 450000
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": "item-uuid-1",
    "billing_po_id": "bill-uuid-123",
    "item_description": "Labour Cost - Phase 1",
    "amount": 450000
  }
}
```

### Get Billing Line Items
```
GET /billing-po/{billing_po_id}/line-items
```
**Function**: Get line items for billing PO  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": [
    {
      "id": "item-uuid-1",
      "item_description": "Labour Cost - Phase 1",
      "amount": 450000
    }
  ]
}
```

### Update Billing PO
```
PUT /billing-po/{billing_po_id}
```
**Function**: Update billing PO  
**Request**:
```json
{
  "po_number": "BILL-2026-001-REV",
  "amount": 500000
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": "bill-uuid-123",
    "po_number": "BILL-2026-001-REV",
    "amount": 500000
  }
}
```

### Approve Billing PO
```
POST /billing-po/{billing_po_id}/approve
```
**Function**: Approve billing PO  
**Request**:
```json
{
  "approved_by": "manager@example.com"
}
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": "bill-uuid-123",
    "status": "approved",
    "approved_by": "manager@example.com",
    "approved_at": "2026-02-17T10:35:00"
  }
}
```

### Get Project P&L Analysis
```
GET /projects/{project_id}/billing-pl-analysis
```
**Function**: Get profit & loss analysis  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "project_id": 1,
    "total_revenue": 450000,
    "total_cost": 200000,
    "gross_profit": 250000,
    "profit_margin": 55.56
  }
}
```

---

## Documents

### Upload Document
```
POST /documents/upload
```
**Function**: Upload project/PO document  
**Request**: Multipart form
```
Form Data:
- file: <binary file>
- project_id: 1 (optional)
- client_po_id: 42 (optional)
- po_number: "BJ-2026-001" (optional)
- description: "Invoice copy"
```
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 200,
    "document_name": "Invoice.pdf",
    "document_path": "/documents/invoice.pdf",
    "compressed_filename": "invoice_compressed.pdf",
    "download_url": "/api/documents/download/200",
    "file_size": 50000,
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Get Project Documents
```
GET /documents/project/{project_id}
```
**Function**: Get all documents for project  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "documents": [
      {
        "id": 200,
        "document_name": "Invoice.pdf",
        "file_size": 50000,
        "created_at": "2026-02-17T10:30:00"
      }
    ]
  }
}
```

### Get PO Documents
```
GET /documents/po/{client_po_id}
```
**Function**: Get documents for PO  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "documents": [
      {
        "id": 200,
        "document_name": "PO_Copy.pdf",
        "file_size": 50000
      }
    ]
  }
}
```

### Get Document Details
```
GET /documents/{doc_id}
```
**Function**: Get single document  
**Request**: None  
**Response**:
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 200,
    "document_name": "Invoice.pdf",
    "file_size": 50000,
    "download_url": "/api/documents/download/200",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

### Download Document
```
GET /documents/download/{doc_id}
```
**Function**: Download document (returns binary)  
**Request**: None  
**Response**: Binary file with `Content-Disposition: attachment`

---

## Error Responses

### Standard Error
```json
{
  "status": "ERROR",
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input provided",
  "path": "/api/projects",
  "errors": [
    {
      "field": "name",
      "message": "Name is required",
      "type": "string"
    }
  ]
}
```

### Not Found Error
```json
{
  "status": "ERROR",
  "error_code": "NOT_FOUND",
  "message": "Resource not found",
  "path": "/api/projects/999"
}
```

### Unauthorized Error
```json
{
  "status": "ERROR",
  "error_code": "UNAUTHORIZED",
  "message": "Authentication required",
  "path": "/api/projects"
}
```

### Server Error
```json
{
  "status": "ERROR",
  "error_code": "SERVER_ERROR",
  "message": "Internal server error",
  "path": "/api/projects"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

**Version**: 1.0.0 | **Last Updated**: February 17, 2026  
**Base URL**: `http://localhost:8000/api`  
**Auth**: HTTP Basic Auth
