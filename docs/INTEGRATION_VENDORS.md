# Vendors Integration Guide

## Overview
Complete vendor management system for PO workflow. Handles vendor creation, order tracking, payment processing, and performance analytics.

## Architecture

```
Vendor Creation → Vendor Profile → Orders → Payments → Analytics
      ↓               ↓             ↓          ↓           ↓
  Validate        Store GST       Track      Record      Dashboard
  GSTIN           Email           PO Value   Amount      Reports
  Create          Contact         Due Date   Status      Performance
```

---

## API Endpoints

### 1. Create Vendor
```http
POST /api/vendors
Content-Type: application/json

{
  "name": "Supplier Name",
  "address": "123 Business Street, City, Country",
  "gstin": "18AABCU9603R1Z0",
  "contact_person": "John Doe",
  "email": "john@supplier.com",
  "phone": "+91-9876543210",
  "payment_terms": "NET_30",
  "status": "ACTIVE"
}
```

**Response:**
```json
{
  "id": 42,
  "name": "Supplier Name",
  "address": "123 Business Street",
  "gstin": "18AABCU9603R1Z0",
  "contact_person": "John Doe",
  "email": "john@supplier.com",
  "phone": "+91-9876543210",
  "payment_terms": "NET_30",
  "status": "ACTIVE",
  "created_at": "2026-02-17T10:30:00",
  "updated_at": "2026-02-17T10:30:00"
}
```

**Validation:**
- GSTIN format: 15-digit alphanumeric
- Email: Valid format
- Phone: Minimum 10 digits

---

### 2. Get Vendor by ID
```http
GET /api/vendors/{vendor_id}
```

**Response:**
```json
{
  "id": 42,
  "name": "Supplier Name",
  "address": "123 Business Street",
  "gstin": "18AABCU9603R1Z0",
  "contact_person": "John Doe",
  "email": "john@supplier.com",
  "phone": "+91-9876543210",
  "payment_terms": "NET_30",
  "status": "ACTIVE",
  "created_at": "2026-02-17T10:30:00",
  "updated_at": "2026-02-17T10:30:00"
}
```

---

### 3. List All Vendors (with filters)
```http
GET /api/vendors?status=ACTIVE&name=Supplier&limit=10&offset=0
```

**Query Parameters:**
- `status` - Filter by vendor status (ACTIVE, INACTIVE, SUSPENDED)
- `name` - Search by vendor name
- `gstin` - Filter by GSTIN
- `limit` - Pagination limit (default: 50)
- `offset` - Pagination offset (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": 42,
      "name": "Supplier Name",
      "email": "john@supplier.com",
      "phone": "+91-9876543210",
      "status": "ACTIVE"
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

---

### 4. Update Vendor
```http
PUT /api/vendors/{vendor_id}
Content-Type: application/json

{
  "name": "Updated Supplier Name",
  "phone": "+91-9876543211",
  "email": "newemail@supplier.com",
  "payment_terms": "NET_45",
  "status": "INACTIVE"
}
```

**Response:**
```json
{
  "id": 42,
  "name": "Updated Supplier Name",
  "email": "newemail@supplier.com",
  "phone": "+91-9876543211",
  "payment_terms": "NET_45",
  "status": "INACTIVE",
  "updated_at": "2026-02-17T11:30:00"
}
```

---

### 5. Delete Vendor
```http
DELETE /api/vendors/{vendor_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Vendor deleted successfully",
  "data": {"vendor_id": 42}
}
```

---

### 6. Get Vendor Details (with orders & payments)
```http
GET /api/vendors/{vendor_id}/details
```

**Response:**
```json
{
  "vendor": {
    "id": 42,
    "name": "Supplier Name",
    "gstin": "18AABCU9603R1Z0",
    "email": "john@supplier.com",
    "phone": "+91-9876543210"
  },
  "total_orders": 25,
  "total_order_value": 2500000,
  "avg_order_value": 100000,
  "pending_payment": 450000,
  "total_paid": 2050000,
  "recent_orders": [
    {
      "po_number": "PO-2026-001",
      "amount": 100000,
      "status": "PENDING_PAYMENT"
    }
  ],
  "payment_health": "GOOD"
}
```

---

### 7. Get Vendor Payments
```http
GET /api/vendors/{vendor_id}/payments?limit=20&offset=0
```

**Response:**
```json
[
  {
    "id": 1001,
    "vendor_id": 42,
    "vendor_order_id": 5,
    "amount": 100000,
    "payment_date": "2026-02-17",
    "status": "COMPLETED",
    "created_at": "2026-02-17T10:30:00"
  },
  {
    "id": 1002,
    "vendor_id": 42,
    "vendor_order_id": 6,
    "amount": 50000,
    "payment_date": "2026-02-16",
    "status": "PENDING",
    "created_at": "2026-02-16T10:30:00"
  }
]
```

---

### 8. Get Vendor Payment Summary
```http
GET /api/vendors/{vendor_id}/payment-summary
```

**Response:**
```json
{
  "vendor_id": 42,
  "vendor_name": "Supplier Name",
  "total_order_value": 2500000,
  "total_paid": 2050000,
  "payable_amount": 450000,
  "payment_completion_percent": 82,
  "average_payment_days": 15,
  "last_payment": {
    "date": "2026-02-17",
    "amount": 100000,
    "status": "COMPLETED"
  },
  "upcoming_due": [
    {
      "vendor_order_id": 10,
      "po_number": "PO-2026-005",
      "amount": 150000,
      "due_date": "2026-02-28"
    }
  ]
}
```

---

## Database Schema

### vendor table
```sql
CREATE TABLE vendor (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  address TEXT,
  gstin VARCHAR(15) UNIQUE,
  contact_person VARCHAR(255),
  email VARCHAR(255),
  phone VARCHAR(20),
  payment_terms VARCHAR(50),
  status VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### vendor_order table
```sql
CREATE TABLE vendor_order (
  id BIGSERIAL PRIMARY KEY,
  vendor_id BIGINT NOT NULL,
  po_number VARCHAR(100) UNIQUE,
  amount NUMERIC(15, 2),
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (vendor_id) REFERENCES vendor(id)
);
```

### vendor_payment table
```sql
CREATE TABLE vendor_payment (
  id BIGSERIAL PRIMARY KEY,
  vendor_id BIGINT NOT NULL,
  vendor_order_id BIGINT,
  amount NUMERIC(15, 2),
  payment_date DATE,
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (vendor_id) REFERENCES vendor(id),
  FOREIGN KEY (vendor_order_id) REFERENCES vendor_order(id)
);
```

---

## Implementation Example

### Python (requests)
```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Create vendor
vendor_data = {
    "name": "Premium Supplier Ltd",
    "address": "42 Industrial Area, Mumbai",
    "gstin": "27AABFU6954R1Z1",
    "contact_person": "Rajesh Kumar",
    "email": "rajesh@premium.com",
    "phone": "+91-9876543210",
    "payment_terms": "NET_30",
    "status": "ACTIVE"
}

vendor_resp = requests.post(
    f"{BASE_URL}/api/vendors",
    json=vendor_data
)
vendor = vendor_resp.json()
vendor_id = vendor["id"]

# 2. Get vendor details
details_resp = requests.get(
    f"{BASE_URL}/api/vendors/{vendor_id}/details"
)
details = details_resp.json()
print(f"Total Orders: {details['total_orders']}")
print(f"Pending Payment: {details['pending_payment']}")

# 3. Get vendor payments
payments_resp = requests.get(
    f"{BASE_URL}/api/vendors/{vendor_id}/payments"
)
payments = payments_resp.json()
for payment in payments:
    print(f"Payment {payment['id']}: ₹{payment['amount']} - {payment['status']}")

# 4. Get payment summary
summary_resp = requests.get(
    f"{BASE_URL}/api/vendors/{vendor_id}/payment-summary"
)
summary = summary_resp.json()
print(f"Payment Completion: {summary['payment_completion_percent']}%")

# 5. Update vendor
update_data = {
    "payment_terms": "NET_45",
    "phone": "+91-9876543211"
}
requests.put(f"{BASE_URL}/api/vendors/{vendor_id}", json=update_data)
```

### JavaScript (fetch)
```javascript
const BASE_URL = "http://localhost:8000";

// 1. Create vendor
async function createVendor() {
  const response = await fetch(`${BASE_URL}/api/vendors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: "Premium Supplier Ltd",
      address: "42 Industrial Area, Mumbai",
      gstin: "27AABFU6954R1Z1",
      contact_person: "Rajesh Kumar",
      email: "rajesh@premium.com",
      phone: "+91-9876543210",
      payment_terms: "NET_30",
      status: "ACTIVE"
    })
  });
  return response.json();
}

// 2. Get vendor details
async function getVendorDetails(vendorId) {
  const response = await fetch(
    `${BASE_URL}/api/vendors/${vendorId}/details`
  );
  const details = await response.json();
  console.log(`Total Orders: ${details.total_orders}`);
  console.log(`Pending Payment: ₹${details.pending_payment}`);
}

// 3. Get payment summary
async function getPaymentSummary(vendorId) {
  const response = await fetch(
    `${BASE_URL}/api/vendors/${vendorId}/payment-summary`
  );
  const summary = await response.json();
  console.log(`Payment Completion: ${summary.payment_completion_percent}%`);
  console.log(`Payable Amount: ₹${summary.payable_amount}`);
}

// 4. List vendors with filter
async function listVendors() {
  const response = await fetch(
    `${BASE_URL}/api/vendors?status=ACTIVE&limit=20`
  );
  const { data, total } = await response.json();
  console.log(`Total vendors: ${total}`);
  data.forEach(v => console.log(`${v.name} - ${v.email}`));
}
```

---

## Payment Terms Reference

Standard payment terms:
- `NET_15` - Payment due 15 days after invoice
- `NET_30` - Payment due 30 days after invoice (most common)
- `NET_45` - Payment due 45 days after invoice
- `NET_60` - Payment due 60 days after invoice
- `COD` - Cash on delivery
- `ADVANCE` - Advance payment required

---

## Vendor Status Values

- `ACTIVE` - Vendor is active and can receive orders
- `INACTIVE` - Vendor is inactive but records are kept
- `SUSPENDED` - Vendor is under review, no new orders
- `BLACKLISTED` - Vendor is permanently blocked

---

## Workflows

### Complete Vendor Onboarding
```
1. Create vendor (POST /api/vendors)
2. Verify GSTIN with tax authority
3. Set up bank account details
4. Configure payment terms
5. Create first purchase order
6. Receive goods and create payment
7. Process payment
8. Mark order as completed
```

### Payment Processing Workflow
```
1. Receive vendor invoice
2. Match with PO (three-way match)
3. Record payment obligation
4. Process payment on due date
5. Record payment completion
6. Generate payment certificate
```

---

## Error Handling

### Common Errors

**400 Bad Request - Invalid GSTIN**
```json
{
  "status": "ERROR",
  "error_code": "INVALID_GSTIN",
  "message": "GSTIN must be 15-digit",
  "field": "gstin"
}
```

**404 Not Found - Vendor Missing**
```json
{
  "status": "ERROR",
  "error_code": "NOT_FOUND",
  "message": "Vendor with ID 999 not found"
}
```

**409 Conflict - Duplicate GSTIN**
```json
{
  "status": "ERROR",
  "error_code": "DUPLICATE_GSTIN",
  "message": "Vendor with GSTIN already exists"
}
```

---

## Best Practices

1. **Data Validation**
   - Always verify GSTIN format
   - Validate email addresses
   - Ensure phone numbers are realistic

2. **Vendor Management**
   - Maintain vendor hierarchy for parent-subsidiary relationships
   - Track vendor rating and performance
   - Implement vendor scorecards

3. **Payment Management**
   - Always perform three-way matching
   - Set payment reminders based on due dates
   - Maintain audit trail for all changes

4. **Reporting**
   - Generate aging reports for payables
   - Track vendor on-time delivery
   - Monitor payment terms compliance

5. **Compliance**
   - Store GST compliance documents
   - Maintain vendor agreement copies
   - Track vendor certifications

---

## Performance Considerations

- Index on vendor.gstin for quick lookups
- Index on vendor_order.vendor_id for order queries
- Index on vendor_payment.vendor_id for payment reconciliation
- Archive old payments for faster queries
- Use pagination for large vendor lists

