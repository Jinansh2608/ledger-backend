# Billing & Purchase Order (PO) Integration Guide

## Overview
Complete billing and PO management system for tracking client purchase orders, payments, and billing cycles. Integrates auto-parsing of client documents with payment reconciliation.

## Architecture

```
Client PO Upload → Auto Parse → Create Billing PO → Link Payments → Generate Invoice
        ↓              ↓               ↓                 ↓              ↓
  Store file      Extract data    Store record      Record amount    Send to client
  Session mgmt    Validate        Set dates         Track paid       Archive
  Compression     Transform       Link vendor       Reconciliation   Report
```

---

## API Endpoints

### 1. Create Billing PO
```http
POST /api/billing/pos
Content-Type: application/json

{
  "client_id": 1,
  "po_number": "BAJAJ-PO-2026-001",
  "po_date": "2026-02-17",
  "vendor_id": 42,
  "subtotal": 500000,
  "cgst": 45000,
  "sgst": 45000,
  "igst": 0,
  "total": 590000,
  "line_items": [
    {
      "description": "Item 1",
      "quantity": 100,
      "unit": "pcs",
      "unit_price": 2500,
      "tax_rate": 18
    }
  ],
  "source": "UPLOADED_FILE",
  "file_id": "file_abc123"
}
```

**Response:**
```json
{
  "id": 42,
  "client_id": 1,
  "po_number": "BAJAJ-PO-2026-001",
  "po_date": "2026-02-17",
  "vendor_id": 42,
  "vendor_name": "Supplier Name",
  "subtotal": 500000,
  "cgst": 45000,
  "sgst": 45000,
  "igst": 0,
  "total": 590000,
  "status": "ACTIVE",
  "created_at": "2026-02-17T10:30:00"
}
```

---

### 2. Get Billing PO by ID
```http
GET /api/billing/pos/{po_id}
```

**Response:**
```json
{
  "id": 42,
  "client_id": 1,
  "client_name": "Bajaj",
  "po_number": "BAJAJ-PO-2026-001",
  "po_date": "2026-02-17",
  "vendor_id": 42,
  "vendor_name": "Supplier Name",
  "subtotal": 500000,
  "cgst": 45000,
  "sgst": 45000,
  "igst": 0,
  "total": 590000,
  "status": "ACTIVE",
  "line_items": [
    {
      "id": 1,
      "description": "Item 1",
      "quantity": 100,
      "unit": "pcs",
      "unit_price": 2500,
      "tax_rate": 18,
      "line_total": 2950
    }
  ],
  "file_info": {
    "file_id": "file_abc123",
    "filename": "BAJAJ_PO.xlsx",
    "upload_date": "2026-02-17T10:30:00"
  }
}
```

---

### 3. List Billing POs
```http
GET /api/billing/pos?client_id=1&vendor_id=42&status=ACTIVE&limit=10
```

**Query Parameters:**
- `client_id` - Filter by client
- `vendor_id` - Filter by vendor
- `po_number` - Search by PO number
- `status` - Filter by status
- `date_from` - Filter from date
- `date_to` - Filter to date
- `limit` - Pagination limit (default: 50)
- `offset` - Pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": 42,
      "client_name": "Bajaj",
      "po_number": "BAJAJ-PO-2026-001",
      "vendor_name": "Supplier Name",
      "total": 590000,
      "status": "ACTIVE"
    }
  ],
  "total": 15,
  "limit": 10
}
```

---

### 4. Update Billing PO
```http
PUT /api/billing/pos/{po_id}
Content-Type: application/json

{
  "status": "COMPLETED",
  "notes": "PO fulfilled"
}
```

**Response:**
```json
{
  "id": 42,
  "status": "COMPLETED",
  "updated_at": "2026-02-17T11:30:00"
}
```

---

### 5. Link Payment to Billing PO
```http
POST /api/billing/pos/{po_id}/payments
Content-Type: application/json

{
  "amount": 590000,
  "payment_date": "2026-02-18",
  "reference_number": "TXN-123456",
  "notes": "Full payment"
}
```

**Response:**
```json
{
  "po_id": 42,
  "payment_id": 101,
  "amount": 590000,
  "status": "RECORDED"
}
```

---

### 6. Get Billing PO Payments
```http
GET /api/billing/pos/{po_id}/payments
```

**Response:**
```json
{
  "po_id": 42,
  "po_number": "BAJAJ-PO-2026-001",
  "total_po_value": 590000,
  "total_paid": 590000,
  "payments": [
    {
      "id": 101,
      "amount": 590000,
      "payment_date": "2026-02-18",
      "reference_number": "TXN-123456",
      "status": "COMPLETED"
    }
  ]
}
```

---

### 7. Get Client Billing Summary
```http
GET /api/billing/clients/{client_id}/summary?start_date=2026-01-01&end_date=2026-02-28
```

**Response:**
```json
{
  "client_id": 1,
  "client_name": "Bajaj",
  "period": "2026-01-01 to 2026-02-28",
  "total_pos": 15,
  "total_po_value": 8750000,
  "total_paid": 7200000,
  "total_pending": 1550000,
  "payment_completion_percent": 82.3,
  "average_po_value": 583333,
  "pos": [
    {
      "po_number": "BAJAJ-PO-2026-001",
      "vendor_name": "Supplier Name",
      "total": 590000,
      "paid": 590000,
      "status": "COMPLETED"
    }
  ]
}
```

---

### 8. Generate Invoice from PO
```http
POST /api/billing/pos/{po_id}/invoice
Content-Type: application/json

{
  "invoice_number": "INV-2026-001",
  "invoice_date": "2026-02-20",
  "due_date": "2026-03-20",
  "include_line_items": true
}
```

**Response:**
```json
{
  "invoice_id": 201,
  "invoice_number": "INV-2026-001",
  "po_id": 42,
  "invoice_url": "https://api.example.com/api/billing/invoices/201/download"
}
```

---

### 9. Get Billing Statistics
```http
GET /api/billing/statistics?start_date=2026-01-01&end_date=2026-02-28
```

**Response:**
```json
{
  "period": "2026-01-01 to 2026-02-28",
  "total_clients": 2,
  "total_vendors": 15,
  "total_pos": 45,
  "total_value": 25000000,
  "top_clients": [
    {
      "client_id": 1,
      "client_name": "Bajaj",
      "po_count": 25,
      "total_value": 15000000
    },
    {
      "client_id": 2,
      "client_name": "Dava India",
      "po_count": 20,
      "total_value": 10000000
    }
  ],
  "top_vendors": [
    {
      "vendor_id": 42,
      "vendor_name": "Supplier Name",
      "po_count": 12,
      "total_value": 5000000
    }
  ]
}
```

---

## Database Schema

### client_po table (also called billing_po)
```sql
CREATE TABLE client_po (
  id BIGSERIAL PRIMARY KEY,
  client_id BIGINT NOT NULL,
  po_number VARCHAR(100) NOT NULL,
  po_date DATE NOT NULL,
  vendor_id BIGINT,
  subtotal NUMERIC(15, 2),
  cgst NUMERIC(15, 2),
  sgst NUMERIC(15, 2),
  igst NUMERIC(15, 2),
  total NUMERIC(15, 2) NOT NULL,
  status VARCHAR(50),
  source VARCHAR(50),
  file_id VARCHAR(255),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (client_id, po_number),
  FOREIGN KEY (vendor_id) REFERENCES vendor(id),
  INDEX idx_client_po_client (client_id),
  INDEX idx_client_po_vendor (vendor_id),
  INDEX idx_client_po_status (status),
  INDEX idx_client_po_date (po_date)
);
```

### client_po_line_item table
```sql
CREATE TABLE client_po_line_item (
  id BIGSERIAL PRIMARY KEY,
  client_po_id BIGINT NOT NULL,
  description VARCHAR(500),
  quantity INT,
  unit VARCHAR(50),
  unit_price NUMERIC(15, 2),
  tax_rate NUMERIC(5, 2),
  line_total NUMERIC(15, 2),
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (client_po_id) REFERENCES client_po(id)
);
```

### client_po_payment table
```sql
CREATE TABLE client_po_payment (
  id BIGSERIAL PRIMARY KEY,
  client_po_id BIGINT NOT NULL,
  amount NUMERIC(15, 2),
  payment_date DATE,
  reference_number VARCHAR(100),
  status VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (client_po_id) REFERENCES client_po(id),
  INDEX idx_payment_po (client_po_id),
  INDEX idx_payment_status (status)
);
```

---

## Implementation Example

### Python
```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Create billing PO
po_data = {
    "client_id": 1,
    "po_number": "BAJAJ-PO-2026-001",
    "po_date": datetime.now().strftime("%Y-%m-%d"),
    "vendor_id": 42,
    "subtotal": 500000,
    "cgst": 45000,
    "sgst": 45000,
    "igst": 0,
    "total": 590000,
    "line_items": [
        {
            "description": "Item 1",
            "quantity": 100,
            "unit": "pcs",
            "unit_price": 2500,
            "tax_rate": 18
        }
    ],
    "source": "UPLOADED_FILE",
    "file_id": "file_abc123"
}

po_resp = requests.post(
    f"{BASE_URL}/api/billing/pos",
    json=po_data
)
po = po_resp.json()
po_id = po["id"]

# 2. Link payment to PO
payment_resp = requests.post(
    f"{BASE_URL}/api/billing/pos/{po_id}/payments",
    json={
        "amount": 590000,
        "payment_date": datetime.now().strftime("%Y-%m-%d"),
        "reference_number": "TXN-123456",
        "notes": "Full payment"
    }
)

# 3. Get client billing summary
summary_resp = requests.get(
    f"{BASE_URL}/api/billing/clients/1/summary"
)
summary = summary_resp.json()
print(f"Total POs: {summary['total_pos']}")
print(f"Total Value: ₹{summary['total_po_value']}")
print(f"Paid: ₹{summary['total_paid']}")
print(f"Pending: ₹{summary['total_pending']}")

# 4. Generate invoice
invoice_resp = requests.post(
    f"{BASE_URL}/api/billing/pos/{po_id}/invoice",
    json={
        "invoice_number": "INV-2026-001",
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    }
)
invoice = invoice_resp.json()
print(f"Invoice URL: {invoice['invoice_url']}")

# 5. Get billing statistics
stats_resp = requests.get(
    f"{BASE_URL}/api/billing/statistics?start_date=2026-01-01&end_date=2026-02-28"
)
stats = stats_resp.json()
print(f"Total POs: {stats['total_pos']}")
for client in stats['top_clients']:
    print(f"{client['client_name']}: {client['po_count']} POs")
```

### JavaScript
```javascript
const BASE_URL = "http://localhost:8000";

// 1. Create billing PO
async function createBillingPO() {
  const response = await fetch(`${BASE_URL}/api/billing/pos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: 1,
      po_number: "BAJAJ-PO-2026-001",
      po_date: new Date().toISOString().split('T')[0],
      vendor_id: 42,
      subtotal: 500000,
      cgst: 45000,
      sgst: 45000,
      igst: 0,
      total: 590000,
      line_items: [
        {
          description: "Item 1",
          quantity: 100,
          unit: "pcs",
          unit_price: 2500,
          tax_rate: 18
        }
      ],
      source: "UPLOADED_FILE",
      file_id: "file_abc123"
    })
  });
  return response.json();
}

// 2. Get client billing summary
async function getClientInvoices() {
  const response = await fetch(
    `${BASE_URL}/api/billing/clients/1/summary`
  );
  const summary = await response.json();
  console.log(`Total POs: ${summary.total_pos}`);
  console.log(`Total Value: ₹${summary.total_po_value}`);
  console.log(`Paid: ₹${summary.total_paid}`);
}

// 3. Link payment to PO
async function linkPayment(poId) {
  const response = await fetch(
    `${BASE_URL}/api/billing/pos/${poId}/payments`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: 590000,
        payment_date: new Date().toISOString().split('T')[0],
        reference_number: "TXN-123456",
        notes: "Full payment"
      })
    }
  );
  return response.json();
}

// 4. Generate invoice
async function generateInvoice(poId) {
  const response = await fetch(
    `${BASE_URL}/api/billing/pos/${poId}/invoice`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        invoice_number: "INV-2026-001",
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: new Date(Date.now() + 30*24*60*60*1000)
          .toISOString().split('T')[0]
      })
    }
  );
  return response.json();
}
```

---

## Auto-Parsing Workflow

When file is uploaded with client_id=1 (Bajaj):

1. **File Upload** - Session captures file
2. **Parser Selection** - Bajaj PO Parser selected
3. **Data Extraction**:
   ```json
   {
     "po_number": "BAJAJ-PO-2026-001",
     "po_date": "2026-02-17",
     "vendor_name": "Supplier Name",
     "subtotal": 500000,
     "cgst": 45000,
     "sgst": 45000,
     "total": 590000,
     "line_items": [...]
   }
   ```
4. **Vendor Matching** - Links to existing vendor
5. **PO Creation** - Creates billing_po record
6. **File Linking** - Links original file to PO

---

## Billing Workflows

### Complete Billing Cycle
```
1. Receive PO from client
2. Process PO (auto or manual)
3. Create billing PO record
4. Link to vendor
5. Receive payment from client
6. Record payment
7. Generate invoice for client
8. Archive record
```

### Client Invoice Workflow
```
1. For each billing PO with amount due
2. Group by client
3. Generate invoice
4. Send to client
5. Track payment
6. Reconcile with accounting
```

---

## Error Handling

**409 Conflict - Duplicate PO Number for Client**
```json
{
  "status": "ERROR",
  "error_code": "DUPLICATE_PO",
  "message": "PO BAJAJ-PO-2026-001 already exists for this client"
}
```

---

## Best Practices

1. **PO Processing**
   - Enable auto-parsing for supported clients
   - Validate vendor information
   - Link to vendor correctly
   - Store original file

2. **Payment Reconciliation**
   - Record all client payments
   - Match payments to billing POs
   - Track pending amounts
   - Generate aging reports

3. **Invoicing**
   - Generate invoices at regular intervals
   - Include all required details
   - Send to client promptly
   - Track payment status

