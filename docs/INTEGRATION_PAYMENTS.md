# Payments Integration Guide

## Overview
Complete payment processing system for vendor management. Handles payment recording, tracking, and reconciliation with comprehensive reporting.

## Architecture

```
Payment Obligation → Payment Queue → Payment Processing → Reconciliation
         ↓                ↓                   ↓                  ↓
   Created from PO   Schedule payment    Record transaction   Match records
   Link to invoice   Validate vendor     Update status        Generate report
   Set due date      Check balance       Send confirmation    Audit trail
```

---

## API Endpoints

### 1. Create Payment
```http
POST /api/payments
Content-Type: application/json

{
  "vendor_id": 42,
  "vendor_order_id": 5,
  "amount": 100000,
  "payment_date": "2026-02-20",
  "status": "PENDING",
  "reference_number": "NEFT-123456",
  "notes": "Payment for PO-2026-001"
}
```

**Response:**
```json
{
  "id": 1001,
  "vendor_id": 42,
  "vendor_order_id": 5,
  "amount": 100000,
  "payment_date": "2026-02-20",
  "status": "PENDING",
  "reference_number": "NEFT-123456",
  "notes": "Payment for PO-2026-001",
  "created_at": "2026-02-17T11:30:00",
  "updated_at": "2026-02-17T11:30:00"
}
```

---

### 2. Get Payment by ID
```http
GET /api/payments/{payment_id}
```

**Response:**
```json
{
  "id": 1001,
  "vendor_id": 42,
  "vendor_order_id": 5,
  "amount": 100000,
  "payment_date": "2026-02-20",
  "status": "PENDING",
  "reference_number": "NEFT-123456",
  "notes": "Payment for PO-2026-001",
  "created_at": "2026-02-17T11:30:00",
  "updated_at": "2026-02-17T11:30:00",
  "vendor_details": {
    "id": 42,
    "name": "Supplier Name",
    "email": "john@supplier.com"
  }
}
```

---

### 3. List Payments (with filters)
```http
GET /api/payments?vendor_id=42&status=PENDING&limit=10&offset=0
```

**Query Parameters:**
- `vendor_id` - Filter by vendor ID
- `status` - Filter by payment status (PENDING, COMPLETED, FAILED, CANCELLED)
- `payment_date_from` - Filter payments from date (YYYY-MM-DD)
- `payment_date_to` - Filter payments to date (YYYY-MM-DD)
- `min_amount` - Filter by minimum amount
- `max_amount` - Filter by maximum amount
- `limit` - Pagination limit (default: 50)
- `offset` - Pagination offset (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": 1001,
      "vendor_id": 42,
      "amount": 100000,
      "payment_date": "2026-02-20",
      "status": "PENDING",
      "reference_number": "NEFT-123456"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

---

### 4. Update Payment
```http
PUT /api/payments/{payment_id}
Content-Type: application/json

{
  "status": "COMPLETED",
  "payment_date": "2026-02-18",
  "reference_number": "NEFT-654321",
  "notes": "Payment processed successfully"
}
```

**Response:**
```json
{
  "id": 1001,
  "vendor_id": 42,
  "amount": 100000,
  "status": "COMPLETED",
  "payment_date": "2026-02-18",
  "updated_at": "2026-02-17T12:00:00"
}
```

---

### 5. Delete Payment
```http
DELETE /api/payments/{payment_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Payment deleted successfully",
  "data": {"payment_id": 1001}
}
```

---

### 6. Get Payment Summary
```http
GET /api/payments/summary/by-vendor?start_date=2026-01-01&end_date=2026-02-28
```

**Response:**
```json
{
  "total_amount": 5000000,
  "total_pending": 450000,
  "total_completed": 4550000,
  "total_failed": 0,
  "pending_count": 5,
  "completed_count": 48,
  "average_payment_amount": 101010,
  "vendors": [
    {
      "vendor_id": 42,
      "vendor_name": "Supplier Name",
      "total_paid": 1000000,
      "pending_payment": 100000,
      "payment_completion_percent": 90.91
    }
  ]
}
```

---

### 7. Get Payment Status
```http
GET /api/payments/{payment_id}/status
```

**Response:**
```json
{
  "payment_id": 1001,
  "current_status": "COMPLETED",
  "status_history": [
    {
      "status": "PENDING",
      "timestamp": "2026-02-17T11:30:00",
      "changed_by": "admin",
      "notes": "Payment created"
    },
    {
      "status": "PROCESSING",
      "timestamp": "2026-02-18T09:00:00",
      "changed_by": "system",
      "notes": "Batch processed"
    },
    {
      "status": "COMPLETED",
      "timestamp": "2026-02-18T15:30:00",
      "changed_by": "system",
      "notes": "Successfully transferred"
    }
  ]
}
```

---

### 8. Bulk Payment Processing
```http
POST /api/payments/bulk-process
Content-Type: application/json

{
  "payment_ids": [1001, 1002, 1003],
  "batch_reference": "BATCH-2026-002",
  "processing_date": "2026-02-20",
  "notes": "Weekly payment batch"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Batch processing initiated",
  "data": {
    "batch_id": "BATCH-2026-002",
    "total_amount": 300000,
    "payment_count": 3,
    "processing_date": "2026-02-20",
    "queue_position": 1
  }
}
```

---

## Database Schema

### vendor_payment table
```sql
CREATE TABLE vendor_payment (
  id BIGSERIAL PRIMARY KEY,
  vendor_id BIGINT NOT NULL,
  vendor_order_id BIGINT,
  amount NUMERIC(15, 2) NOT NULL,
  payment_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL,
  reference_number VARCHAR(100),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (vendor_id) REFERENCES vendor(id),
  FOREIGN KEY (vendor_order_id) REFERENCES vendor_order(id),
  INDEX idx_vendor_payment_vendor_id (vendor_id),
  INDEX idx_vendor_payment_status (status),
  INDEX idx_vendor_payment_date (payment_date)
);
```

### payment_status_history table (optional)
```sql
CREATE TABLE payment_status_history (
  id BIGSERIAL PRIMARY KEY,
  payment_id BIGINT NOT NULL,
  old_status VARCHAR(50),
  new_status VARCHAR(50) NOT NULL,
  changed_by VARCHAR(100),
  changed_at TIMESTAMP DEFAULT NOW(),
  notes TEXT,
  FOREIGN KEY (payment_id) REFERENCES vendor_payment(id)
);
```

---

## Payment Status Workflow

```
PENDING
   ↓
PROCESSING (batch processing initiated)
   ↓
COMPLETED (payment successful) or FAILED (payment failed)
   ↓
RECONCILED (matched with bank statement - optional)
```

**Status Definitions:**
- `PENDING` - Payment created, awaiting processing
- `PROCESSING` - Payment in batch queue, being processed
- `COMPLETED` - Payment successfully transferred
- `FAILED` - Payment transfer failed
- `CANCELLED` - Payment cancelled by user
- `RECONCILED` - Payment matched with bank records

---

## Implementation Example

### Python (requests)
```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Create payment
payment_data = {
    "vendor_id": 42,
    "vendor_order_id": 5,
    "amount": 100000,
    "payment_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
    "status": "PENDING",
    "reference_number": "NEFT-123456",
    "notes": "Payment for PO-2026-001"
}

payment_resp = requests.post(
    f"{BASE_URL}/api/payments",
    json=payment_data
)
payment = payment_resp.json()
payment_id = payment["id"]

# 2. List pending payments
pending_resp = requests.get(
    f"{BASE_URL}/api/payments?status=PENDING&vendor_id=42"
)
pending_payments = pending_resp.json()["data"]
print(f"Pending payments: {len(pending_payments)}")

# 3. Get payment summary
summary_resp = requests.get(
    f"{BASE_URL}/api/payments/summary/by-vendor"
)
summary = summary_resp.json()
print(f"Total pending: ₹{summary['total_pending']}")
print(f"Total completed: ₹{summary['total_completed']}")

# 4. Update payment to COMPLETED
update_data = {
    "status": "COMPLETED",
    "payment_date": datetime.now().strftime("%Y-%m-%d"),
    "reference_number": "NEFT-654321"
}
requests.put(
    f"{BASE_URL}/api/payments/{payment_id}",
    json=update_data
)

# 5. Get payment status history
status_resp = requests.get(
    f"{BASE_URL}/api/payments/{payment_id}/status"
)
history = status_resp.json()["status_history"]
for record in history:
    print(f"{record['status']} at {record['timestamp']}")

# 6. Bulk process payments
bulk_data = {
    "payment_ids": [1001, 1002, 1003],
    "batch_reference": "BATCH-2026-003",
    "processing_date": datetime.now().strftime("%Y-%m-%d"),
    "notes": "Weekly payment batch"
}
bulk_resp = requests.post(
    f"{BASE_URL}/api/payments/bulk-process",
    json=bulk_data
)
result = bulk_resp.json()
print(f"Batch ID: {result['data']['batch_id']}")
```

### JavaScript (fetch)
```javascript
const BASE_URL = "http://localhost:8000";

// 1. Create payment
async function createPayment() {
  const response = await fetch(`${BASE_URL}/api/payments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      vendor_id: 42,
      vendor_order_id: 5,
      amount: 100000,
      payment_date: new Date(Date.now() + 3*24*60*60*1000)
        .toISOString().split('T')[0],
      status: "PENDING",
      reference_number: "NEFT-123456",
      notes: "Payment for PO-2026-001"
    })
  });
  return response.json();
}

// 2. Get pending payments
async function getPendingPayments() {
  const response = await fetch(
    `${BASE_URL}/api/payments?status=PENDING&vendor_id=42`
  );
  const { data, total } = await response.json();
  console.log(`Total pending: ${data.length}`);
  return data;
}

// 3. Update payment status
async function updatePaymentStatus(paymentId, newStatus) {
  const response = await fetch(
    `${BASE_URL}/api/payments/${paymentId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: newStatus,
        payment_date: new Date().toISOString().split('T')[0],
        reference_number: "NEFT-654321"
      })
    }
  );
  return response.json();
}

// 4. Get payment status history
async function getPaymentHistory(paymentId) {
  const response = await fetch(
    `${BASE_URL}/api/payments/${paymentId}/status`
  );
  const { status_history } = await response.json();
  status_history.forEach(record => {
    console.log(`${record.status} at ${record.timestamp}`);
  });
}

// 5. Bulk process payments
async function bulkProcess() {
  const response = await fetch(
    `${BASE_URL}/api/payments/bulk-process`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payment_ids: [1001, 1002, 1003],
        batch_reference: "BATCH-2026-003",
        processing_date: new Date().toISOString().split('T')[0],
        notes: "Weekly payment batch"
      })
    }
  );
  return response.json();
}
```

---

## Payment Processing Workflows

### Standard Payment Workflow
```
1. Create vendor
2. Receive PO from vendor
3. Record PO as vendor_order
4. Create payment obligation (vendor_payment record)
5. On due date - create payment record
6. Process payment (update status to PROCESSING)
7. Record successful transfer (update status to COMPLETED)
8. Reconcile with bank statement
```

### Partial Payment Workflow
```
1. PO Amount: ₹1,00,000
2. Advance Payment (30%): ₹30,000 - COMPLETED
3. On Delivery (50%): ₹50,000 - COMPLETED
4. Final Settlement (20%): ₹20,000 - PENDING
```

### Batch Payment Processing
```
1. Collect all due payments from multiple vendors
2. Create batch with reference number
3. Validate all payments
4. Generate payment file for bank
5. Submit to payment gateway
6. Monitor processing status
7. Reconcile with bank reports
8. Update statuses
9. Generate payment certificates
```

---

## Error Handling

### Common Errors

**400 Bad Request - Invalid Amount**
```json
{
  "status": "ERROR",
  "error_code": "INVALID_AMOUNT",
  "message": "Payment amount must be greater than 0"
}
```

**404 Not Found - Vendor Order Missing**
```json
{
  "status": "ERROR",
  "error_code": "NOT_FOUND",
  "message": "Vendor order with ID 999 not found"
}
```

**409 Conflict - Duplicate Payment**
```json
{
  "status": "ERROR",
  "error_code": "DUPLICATE_PAYMENT",
  "message": "Payment with reference NEFT-123456 already exists"
}
```

**422 Unprocessable Entity - Insufficient Funds**
```json
{
  "status": "ERROR",
  "error_code": "INSUFFICIENT_FUNDS",
  "message": "Payment amount exceeds vendor credit limit",
  "available_credit": 50000,
  "requested_amount": 100000
}
```

---

## Best Practices

1. **Payment Validation**
   - Always validate vendor exists before payment
   - Check three-way match (PO, Invoice, Receipt)
   - Verify payment amount matches invoice
   - Validate payment date isn't in past

2. **Payment Processing**
   - Process payments at fixed intervals (daily/weekly)
   - Use batch processing for efficiency
   - Maintain audit trail of all changes
   - Implement approval workflows for large payments

3. **Reconciliation**
   - Reconcile payments with bank statements
   - Match payment date with transaction date
   - Track discrepancies and follow up
   - Generate reconciliation reports

4. **Compliance**
   - Maintain payment audit logs
   - Ensure separation of duties
   - Archive payment records
   - Generate tax compliance reports

5. **Monitoring**
   - Track payment cycles
   - Monitor overdue payments
   - Alert for failed payments
   - Generate performance dashboards

---

## Performance Considerations

- Index on vendor_payment.status for filtering
- Index on vendor_payment.payment_date for date queries
- Index on vendor_payment.vendor_id for vendor queries
- Archive old completed payments (> 1 year) for faster queries
- Use pagination for large payment lists
- Batch insert for bulk operations
- Cache vendor payment summary for dashboard

