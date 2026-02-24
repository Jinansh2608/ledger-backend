# Frontend Integration Guide - Updated API Routes

## Quick Start

All API endpoints are now fully aligned with frontend expectations. Below is the updated guide for integration.

---

## 1. Purchase Orders API

### Get All POs
**Endpoint:** `GET /api/po`
**Query Params:** `client_id` (optional)
**Response:**
```json
{
  "status": "SUCCESS",
  "data": {
    "pos": [
      {
        "id": 1,
        "client_po_id": 1,
        "po_number": "PO-2024-001",
        "po_date": "2024-01-15",
        "po_value": 100000,
        "receivable_amount": 100000,
        "status": "pending",
        "po_type": "standard",
        "notes": "Sample PO"
      }
    ],
    "total_count": 5,
    "total_value": 500000
  }
}
```

### Get Single PO
**Endpoint:** `GET /api/po/{poId}`
**Response:**
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 1,
    "po_number": "PO-2024-001",
    "po_date": "2024-01-15",
    "po_value": 100000,
    "line_items": [
      {
        "item_name": "Item 1",
        "quantity": 10,
        "unit_price": 5000,
        "total_price": 50000
      }
    ],
    "line_item_count": 2
  }
}
```

### Get PO with Payment Details
**Endpoint:** `GET /api/po/{poId}/details` ⭐ **NEW**
**Response:**
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 1,
    "po_number": "PO-2024-001",
    "po_value": 100000,
    "payment_status": "partial",
    "total_paid": 60000,
    "total_tds": 5000,
    "outstanding_amount": 40000,
    "line_items": [...]
  }
}
```

### Get Project POs
**Endpoint:** `GET /api/projects/{projectId}/po`
**Response:**
```json
{
  "status": "SUCCESS",
  "project_id": 10,
  "pos": [...],
  "total_po_count": 3,
  "total_project_value": 300000,
  "primary_po": { /* PO Object */ }
}
```

### Get Enriched POs (with Payment Data)
**Endpoint:** `GET /api/projects/{projectId}/po/enriched`
**Response:**
```json
{
  "status": "SUCCESS",
  "project_id": 10,
  "pos": [
    {
      "po_id": 1,
      "po_number": "PO-001",
      "po_value": 100000,
      "payment_status": "paid",
      "total_paid": 100000,
      "receivable_amount": 0,
      "total_tds": 5000
    }
  ],
  "total_po_count": 3,
  "total_project_value": 300000,
  "summary": {
    "paid_count": 2,
    "partial_count": 1,
    "pending_count": 0
  }
}
```

### Create PO for Project
**Endpoint:** `POST /api/projects/{projectId}/po?client_id={clientId}`
**Body:**
```json
{
  "po_number": "PO-2024-002",
  "po_date": "2024-01-15",
  "po_value": 150000,
  "po_type": "standard",
  "parent_po_id": null,
  "notes": "Optional notes"
}
```

### Update PO
**Endpoint:** `PUT /api/po/{poId}`
**Body:**
```json
{
  "po_number": "PO-2024-002",
  "po_date": "2024-01-15",
  "po_value": 150000,
  "pi_number": "PI-2024-001",
  "pi_date": "2024-01-15",
  "notes": "Updated notes",
  "status": "completed"
}
```

### Delete PO
**Endpoint:** `DELETE /api/po/{poId}`
**Response:**
```json
{
  "status": "SUCCESS",
  "message": "PO and associated data deleted",
  "client_po_id": 1
}
```

---

## 2. Billing POs API

### Create Billing PO
**Endpoint:** `POST /api/projects/{projectId}/billing-po`
**Body:**
```json
{
  "client_po_id": 1,
  "billed_value": 100000,
  "billed_gst": 18000,
  "billing_notes": "Final bill"
}
```

### Get Billing PO
**Endpoint:** `GET /api/billing-po/{billingPoId}`
**Response:**
```json
{
  "status": "SUCCESS",
  "billing_po": { /* details */ },
  "line_items": [ /* items */ ]
}
```

### Approve Billing PO ⭐ **NEW**
**Endpoint:** `POST /api/billing-po/{billingPoId}/approve`
**Body:**
```json
{
  "notes": "Approved for payment"
}
```
**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Billing PO approved",
  "data": {
    "billing_po_id": "abc-123",
    "status": "APPROVED",
    "billed_value": 100000,
    "billed_gst": 18000,
    "billed_total": 118000
  }
}
```

### Get Billing Summary
**Endpoint:** `GET /api/projects/{projectId}/billing-summary`
**Response:**
```json
{
  "status": "SUCCESS",
  "data": {
    "original_po": {
      "value": 500000,
      "gst": 90000,
      "total": 590000
    },
    "billing_po": {
      "value": 520000,
      "gst": 93600,
      "total": 613600
    },
    "financial_summary": {
      "delta_value": 20000,
      "delta_percent": 3.39,
      "final_revenue": 613600,
      "vendor_costs": 350000,
      "profit": 263600,
      "profit_margin_percent": 43.0
    }
  }
}
```

### Get P&L Analysis ⭐ **NEW**
**Endpoint:** `GET /api/projects/{projectId}/pl-analysis`
**Response:**
```json
{
  "status": "SUCCESS",
  "project_id": 10,
  "data": {
    "total_po_value": 500000,
    "total_billed": 520000,
    "total_vendor_costs": 350000,
    "net_profit": 170000,
    "profit_margin_percentage": 32.69,
    "variance": 20000,
    "variance_percentage": 4
  }
}
```

---

## 3. Vendors API

### Get Vendors
**Endpoint:** `GET /api/vendors?status=active`
**Query Params:** `status` (optional) - 'active' or 'inactive'
**Response:**
```json
{
  "status": "SUCCESS",
  "vendor_count": 5,
  "vendors": [
    {
      "id": 1,
      "name": "Vendor ABC",
      "email": "vendor@abc.com",
      "phone": "9876543210",
      "address": "123 Street",
      "status": "active"
    }
  ]
}
```

### Get Single Vendor
**Endpoint:** `GET /api/vendors/{vendorId}`

### Create Vendor
**Endpoint:** `POST /api/vendors`
**Body:**
```json
{
  "name": "New Vendor",
  "contact_person": "John Doe",
  "email": "john@vendor.com",
  "phone": "9876543210",
  "address": "123 Street",
  "payment_terms": "Net 30"
}
```

### Update Vendor
**Endpoint:** `PUT /api/vendors/{vendorId}`
**Body:** Same as Create

### Delete Vendor
**Endpoint:** `DELETE /api/vendors/{vendorId}`

---

## 4. Vendor Orders API

### Get Project Vendor Orders
**Endpoint:** `GET /api/projects/{projectId}/vendor-orders`
**Response:**
```json
{
  "status": "SUCCESS",
  "vendor_order_count": 3,
  "vendor_orders": [...]
}
```

### Create Vendor Order
**Endpoint:** `POST /api/projects/{projectId}/vendor-orders`
**Body:**
```json
{
  "vendor_id": 1,
  "po_number": "VO-001",
  "po_date": "2024-01-15",
  "po_value": 50000,
  "due_date": "2024-02-15",
  "description": "Order details"
}
```

### Link Payment to Vendor Order ⭐ **NEW**
**Endpoint:** `POST /api/vendor-orders/{vendorOrderId}/link-payment`
**Body:**
```json
{
  "link_type": "incoming",
  "amount": 25000,
  "payment_id": "payment-123"
}
```
**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Payment linked to vendor order",
  "data": {
    "link_id": "link-123",
    "vendor_order_id": 456,
    "link_type": "incoming",
    "amount": 25000
  }
}
```

---

## 5. Payments API

### Get PO Payments
**Endpoint:** `GET /api/po/{poId}/payments`
**Response:**
```json
{
  "status": "SUCCESS",
  "po_id": 1,
  "payments": [
    {
      "id": 1,
      "amount": 50000,
      "payment_date": "2024-01-20",
      "status": "cleared",
      "payment_mode": "bank_transfer"
    }
  ],
  "payment_count": 3,
  "summary": {
    "total_paid": 150000,
    "total_tds": 7500,
    "cleared_count": 3,
    "pending_count": 0,
    "bounced_count": 0
  }
}
```

### Create Payment
**Endpoint:** `POST /api/po/{poId}/payments`
**Body:**
```json
{
  "payment_date": "2024-01-20",
  "amount": 50000,
  "payment_mode": "bank_transfer",
  "status": "cleared",
  "payment_stage": "advance",
  "transaction_type": "credit",
  "is_tds_deducted": true,
  "tds_amount": 2500
}
```

---

## 6. Projects API

### Get All Projects
**Endpoint:** `GET /api/projects`
**Query Params:** `skip=0, limit=50`
**Response:**
```json
{
  "status": "SUCCESS",
  "project_count": 10,
  "projects": [...]
}
```

### Get Single Project
**Endpoint:** `GET /api/projects/{projectId}`

### Create Project
**Endpoint:** `POST /api/projects`
**Body:**
```json
{
  "name": "New Project",
  "location": "Mumbai",
  "city": "Mumbai",
  "state": "Maharashtra",
  "country": "India",
  "latitude": 19.0760,
  "longitude": 72.8777
}
```

### Get Financial Summary
**Endpoint:** `GET /api/projects/{projectId}/financial-summary`
**Response:**
```json
{
  "status": "SUCCESS",
  "project_id": 10,
  "financial_summary": {
    "total_po_value": 500000,
    "total_agreement_value": 100000,
    "total_project_value": 600000,
    "documents": 5,
    "verbal_agreements": 2,
    "total_collected": 400000,
    "outstanding_amount": 200000,
    "net_profit": 100000,
    "profit_margin_percentage": 25.0,
    "active_orders": 3
  }
}
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 201  | Created |
| 400  | Bad Request |
| 404  | Not Found |
| 409  | Conflict (Already Exists) |
| 500  | Server Error |

---

## Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limits & Pagination

- **Default limit:** 50 items per page
- **Max limit:** 100 items per page
- **Query params:** `skip` and `limit`

Example: `GET /api/projects?skip=0&limit=25`

---

## Integration Checklist

- [ ] Update API client to use `/api/po` for listing (note the new `data` wrapper)
- [ ] Update UI to use `GET /api/po/{poId}` for single PO view
- [ ] Integrate new payment details from `GET /api/po/{poId}/details`
- [ ] Add billing PO approval workflow using `POST /api/billing-po/{billingPoId}/approve`
- [ ] Integrate P&L analysis using `GET /api/projects/{projectId}/pl-analysis`
- [ ] Add vendor order payment linking using `POST /api/vendor-orders/{vendorOrderId}/link-payment`
- [ ] Test all endpoints with sample data
- [ ] Update error handling for new response formats
- [ ] Document any custom business logic

---

## Common Integration Patterns

### Get PO and Display Details
```javascript
// 1. Get all POs
const poList = await fetch('/api/po');

// 2. Click on a PO to view details
const poDetails = await fetch(`/api/po/${poId}/details`);

// 3. Display data with payment status
```

### Create Billing PO and Get Analysis
```javascript
// 1. Create billing PO
const billing = await fetch('/api/projects/10/billing-po', 
  { method: 'POST', body: {...} });

// 2. Get P&L analysis
const analysis = await fetch('/api/projects/10/pl-analysis');

// 3. Show financial metrics
```

### Link Vendor Order Payments
```javascript
// 1. Create vendor order
const order = await fetch('/api/projects/10/vendor-orders',
  { method: 'POST', body: {...} });

// 2. Link payment
const link = await fetch(`/api/vendor-orders/${orderId}/link-payment`,
  { method: 'POST', body: { link_type: 'incoming', amount: 50000 } });
```

---

## Support & Troubleshooting

### Common Issues

**Q: Getting 404 on /api/po/{poId}**
- A: Ensure the poId is valid. Use `/api/po` first to get list of IDs.

**Q: /api/po returning empty data object**
- A: Check if there are POs in the database. New projects may not have any POs.

**Q: Payment status shows as "pending" even after payment**
- A: Verify payment status is set correctly in the database.

**Q: P&L analysis not showing profit/loss**
- A: Ensure billing PO and vendor orders are created for the project.

---

