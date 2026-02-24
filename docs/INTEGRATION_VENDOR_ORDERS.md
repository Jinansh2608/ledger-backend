# Vendor Orders (PO) Integration Guide

## Overview
Purchase Order management system handling creation, tracking, and reconciliation of vendor orders throughout their lifecycle.

## Architecture

```
Order Creation → Order Confirmation → Delivery → Invoice → Payment → Closure
       ↓                ↓              ↓         ↓         ↓          ↓
   Validate         Link vendor      Update   Link PO   Create    Archive
   Vendor          Set amount       status   amount  obligation
   Create PO#      Define terms     Receive            Record
```

---

## API Endpoints

### 1. Create Vendor Order
```http
POST /api/vendor-orders
Content-Type: application/json

{
  "vendor_id": 42,
  "po_number": "PO-2026-001",
  "amount": 500000,
  "status": "PENDING_CONFIRMATION",
  "order_date": "2026-02-17",
  "delivery_date": "2026-03-17",
  "description": "Monthly supplies",
  "terms": "NET_30",
  "line_items": [
    {
      "item_name": "Item A",
      "quantity": 100,
      "unit_price": 2500,
      "taxable_amount": 250000,
      "tax_rate": 18,
      "tax_amount": 45000
    },
    {
      "item_name": "Item B",
      "quantity": 50,
      "unit_price": 2000,
      "taxable_amount": 100000,
      "tax_rate": 18,
      "tax_amount": 18000
    }
  ]
}
```

**Response:**
```json
{
  "id": 5,
  "vendor_id": 42,
  "po_number": "PO-2026-001",
  "amount": 500000,
  "status": "PENDING_CONFIRMATION",
  "order_date": "2026-02-17",
  "delivery_date": "2026-03-17",
  "created_at": "2026-02-17T10:30:00",
  "updated_at": "2026-02-17T10:30:00",
  "subtotal": 350000,
  "tax_total": 63000,
  "grand_total": 413000
}
```

---

### 2. Get Vendor Order by ID
```http
GET /api/vendor-orders/{order_id}
```

**Response:**
```json
{
  "id": 5,
  "vendor_id": 42,
  "vendor_name": "Supplier Name",
  "po_number": "PO-2026-001",
  "amount": 500000,
  "status": "PENDING_CONFIRMATION",
  "order_date": "2026-02-17",
  "delivery_date": "2026-03-17",
  "description": "Monthly supplies",
  "terms": "NET_30",
  "line_items": [
    {
      "id": 101,
      "item_name": "Item A",
      "quantity": 100,
      "unit_price": 2500,
      "taxable_amount": 250000,
      "tax_amount": 45000
    }
  ],
  "created_at": "2026-02-17T10:30:00"
}
```

---

### 3. List Vendor Orders
```http
GET /api/vendor-orders?vendor_id=42&status=PENDING_CONFIRMATION&limit=10&offset=0
```

**Query Parameters:**
- `vendor_id` - Filter by vendor
- `status` - Filter by order status
- `po_number` - Search by PO number
- `date_from` - Filter from date
- `date_to` - Filter to date
- `min_amount` - Minimum order amount
- `max_amount` - Maximum order amount
- `limit` - Pagination limit (default: 50)
- `offset` - Pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": 5,
      "vendor_id": 42,
      "po_number": "PO-2026-001",
      "amount": 500000,
      "status": "PENDING_CONFIRMATION"
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

---

### 4. Update Vendor Order
```http
PUT /api/vendor-orders/{order_id}
Content-Type: application/json

{
  "status": "CONFIRMED",
  "delivery_date": "2026-03-20",
  "description": "Updated: Priority delivery"
}
```

**Response:**
```json
{
  "id": 5,
  "status": "CONFIRMED",
  "delivery_date": "2026-03-20",
  "updated_at": "2026-02-17T11:30:00"
}
```

---

### 5. Cancel Vendor Order
```http
DELETE /api/vendor-orders/{order_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Order cancelled successfully",
  "data": {"order_id": 5}
}
```

---

### 6. Get Order Status History
```http
GET /api/vendor-orders/{order_id}/history
```

**Response:**
```json
{
  "order_id": 5,
  "history": [
    {
      "status": "PENDING_CONFIRMATION",
      "timestamp": "2026-02-17T10:30:00",
      "changed_by": "admin",
      "notes": "Order created"
    },
    {
      "status": "CONFIRMED",
      "timestamp": "2026-02-17T11:00:00",
      "changed_by": "procurement",
      "notes": "Vendor confirmed"
    },
    {
      "status": "DELIVERED",
      "timestamp": "2026-03-17T14:30:00",
      "changed_by": "warehouse",
      "notes": "Goods received"
    }
  ]
}
```

---

### 7. Link Invoice to Order
```http
POST /api/vendor-orders/{order_id}/invoice
Content-Type: application/json

{
  "invoice_number": "INV-2026-001",
  "invoice_date": "2026-02-18",
  "invoice_amount": 413000,
  "invoice_file_id": "file_abc123"
}
```

**Response:**
```json
{
  "order_id": 5,
  "invoice_id": 201,
  "invoice_number": "INV-2026-001",
  "status": "INVOICE_RECEIVED"
}
```

---

### 8. Record Delivery
```http
POST /api/vendor-orders/{order_id}/delivery
Content-Type: application/json

{
  "delivery_date": "2026-03-17",
  "received_by": "warehouse_manager",
  "quantity_received": 150,
  "quantity_variance": 0,
  "inspection_status": "PASS",
  "notes": "All items received in good condition"
}
```

**Response:**
```json
{
  "order_id": 5,
  "delivery_id": 301,
  "status": "DELIVERED",
  "delivery_date": "2026-03-17T14:30:00"
}
```

---

## Database Schema

### vendor_order table
```sql
CREATE TABLE vendor_order (
  id BIGSERIAL PRIMARY KEY,
  vendor_id BIGINT NOT NULL,
  po_number VARCHAR(100) UNIQUE NOT NULL,
  amount NUMERIC(15, 2) NOT NULL,
  status VARCHAR(50),
  order_date DATE,
  delivery_date DATE,
  description TEXT,
  terms VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (vendor_id) REFERENCES vendor(id),
  INDEX idx_po_vendor (vendor_id),
  INDEX idx_po_status (status),
  INDEX idx_po_date (order_date)
);
```

### vendor_order_line_item table
```sql
CREATE TABLE vendor_order_line_item (
  id BIGSERIAL PRIMARY KEY,
  vendor_order_id BIGINT NOT NULL,
  item_name VARCHAR(255),
  quantity INT,
  unit_price NUMERIC(15, 2),
  taxable_amount NUMERIC(15, 2),
  tax_rate NUMERIC(5, 2),
  tax_amount NUMERIC(15, 2),
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (vendor_order_id) REFERENCES vendor_order(id)
);
```

---

## Order Status Workflow

```
PENDING_CONFIRMATION
        ↓
    CONFIRMED
        ↓
    IN_TRANSIT
        ↓
    DELIVERED
        ↓
    INVOICE_RECEIVED
        ↓
    PAYMENT_PROCESSED
        ↓
    COMPLETED
```

**Status Definitions:**
- `PENDING_CONFIRMATION` - Order created, awaiting vendor confirmation
- `CONFIRMED` - Vendor has confirmed the order
- `IN_TRANSIT` - Order dispatched from vendor
- `DELIVERED` - Goods received at warehouse
- `INVOICE_RECEIVED` - Invoice received from vendor
- `PAYMENT_PROCESSED` - Payment completed
- `COMPLETED` - Order closed
- `CANCELLED` - Order cancelled

---

## Implementation Example

### Python
```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Create vendor order
order_data = {
    "vendor_id": 42,
    "po_number": f"PO-{datetime.now().strftime('%Y%m%d')}-001",
    "amount": 500000,
    "status": "PENDING_CONFIRMATION",
    "order_date": datetime.now().strftime("%Y-%m-%d"),
    "delivery_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    "description": "Monthly supplies",
    "terms": "NET_30",
    "line_items": [
        {
            "item_name": "Item A",
            "quantity": 100,
            "unit_price": 2500,
            "taxable_amount": 250000,
            "tax_rate": 18,
            "tax_amount": 45000
        }
    ]
}

order_resp = requests.post(
    f"{BASE_URL}/api/vendor-orders",
    json=order_data
)
order = order_resp.json()
order_id = order["id"]

# 2. Confirm order
confirm_resp = requests.put(
    f"{BASE_URL}/api/vendor-orders/{order_id}",
    json={"status": "CONFIRMED"}
)

# 3. Record delivery
delivery_resp = requests.post(
    f"{BASE_URL}/api/vendor-orders/{order_id}/delivery",
    json={
        "delivery_date": datetime.now().strftime("%Y-%m-%d"),
        "received_by": "warehouse_manager",
        "quantity_received": 100,
        "inspection_status": "PASS",
        "notes": "All items received"
    }
)

# 4. Link invoice
invoice_resp = requests.post(
    f"{BASE_URL}/api/vendor-orders/{order_id}/invoice",
    json={
        "invoice_number": "INV-2026-001",
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "invoice_amount": 413000
    }
)

# 5. Get order history
history_resp = requests.get(
    f"{BASE_URL}/api/vendor-orders/{order_id}/history"
)
history = history_resp.json()["history"]
for record in history:
    print(f"{record['status']} - {record['notes']}")
```

### JavaScript
```javascript
const BASE_URL = "http://localhost:8000";

// 1. Create vendor order
async function createVendorOrder() {
  const response = await fetch(`${BASE_URL}/api/vendor-orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      vendor_id: 42,
      po_number: `PO-${new Date().toISOString().split('T')[0]}-001`,
      amount: 500000,
      status: "PENDING_CONFIRMATION",
      order_date: new Date().toISOString().split('T')[0],
      delivery_date: new Date(Date.now() + 30*24*60*60*1000)
        .toISOString().split('T')[0],
      description: "Monthly supplies",
      terms: "NET_30",
      line_items: [
        {
          item_name: "Item A",
          quantity: 100,
          unit_price: 2500,
          taxable_amount: 250000,
          tax_rate: 18,
          tax_amount: 45000
        }
      ]
    })
  });
  return response.json();
}

// 2. Confirm order
async function confirmOrder(orderId) {
  const response = await fetch(
    `${BASE_URL}/api/vendor-orders/${orderId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "CONFIRMED" })
    }
  );
  return response.json();
}

// 3. Record delivery
async function recordDelivery(orderId) {
  const response = await fetch(
    `${BASE_URL}/api/vendor-orders/${orderId}/delivery`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        delivery_date: new Date().toISOString().split('T')[0],
        received_by: "warehouse_manager",
        quantity_received: 100,
        inspection_status: "PASS",
        notes: "All items received"
      })
    }
  );
  return response.json();
}
```

---

## Workflows

### Complete PO Lifecycle
```
1. Identify requirement
2. Create vendor order (PO)
3. Send to vendor
4. Vendor confirms
5. Vendor ships
6. Receive goods
7. Receive invoice
8. Process payment
9. Close order
10. Archive record
```

### Three-Way Match Process
```
1. Match PO quantity with Receipt Quantity
2. Match Invoice quantity with Receipt Quantity  
3. Match Invoice amount with PO amount
                    ↓
        All match = Process Payment
        Discrepancy = Flag for review
```

---

## Error Handling

**400 Bad Request - Duplicate PO Number**
```json
{
  "status": "ERROR",
  "error_code": "DUPLICATE_PO_NUMBER",
  "message": "PO-2026-001 already exists"
}
```

**404 Not Found - Vendor Missing**
```json
{
  "status": "ERROR",
  "error_code": "VENDOR_NOT_FOUND",
  "message": "Vendor with ID 999 not found"
}
```

---

## Best Practices

1. **PO Generation**
   - Use sequential numbering system
   - Include company details in PO
   - Clearly specify terms and conditions
   - Define delivery location and date

2. **Order Tracking**
   - Update status regularly
   - Record all changes with timestamps
   - Maintain communication trail
   - Flag delays immediately

3. **Reconciliation**
   - Always perform three-way match
   - Flag discrepancies quickly
   - Follow up on exceptions
   - Maintain reconciliation reports

4. **Document Management**
   - Attach all supporting documents
   - Maintain digital archive
   - Generate audit trail
   - Enable easy retrieval

