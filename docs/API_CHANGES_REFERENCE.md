# API Changes - Quick Reference & Response Comparison

## Changes Summary

| Route | Status | Old Response | New Response | Notes |
|-------|--------|--------------|--------------|-------|
| `GET /api/po` | ✅ FIXED | `{ "pos": [...] }` | `{ "data": { "pos": [...] } }` | Response format fixed |
| `GET /api/po/{poId}` | ✅ NEW | ❌ N/A | `{ "data": { id, po_number, ... } }` | Endpoint added |
| `GET /api/po/{poId}/details` | ✅ NEW | ❌ N/A | `{ "data": { ..., payment_status } }` | Endpoint added |
| `POST /api/billing-po/{billingPoId}/approve` | ✅ NEW | ❌ N/A | `{ "data": { status: "APPROVED" } }` | Endpoint added |
| `GET /api/projects/{projectId}/pl-analysis` | ✅ NEW | ❌ N/A | `{ "data": { net_profit, ... } }` | Endpoint added |
| `POST /api/vendor-orders/{vendorOrderId}/link-payment` | ✅ NEW | ❌ N/A | `{ "data": { link_id, ... } }` | Endpoint added |

---

## 1. GET /api/po Response Format Change

### BEFORE (BROKEN) ❌
```json
{
  "status": "SUCCESS",
  "pos": [
    {
      "id": 1,
      "po_number": "PO-001",
      "po_value": 100000
    }
  ],
  "total_count": 5,
  "total_value": 500000
}
```

### AFTER (FIXED) ✅
```json
{
  "status": "SUCCESS",
  "data": {
    "pos": [
      {
        "id": 1,
        "po_number": "PO-001",
        "po_value": 100000,
        "po_date": "2024-01-15",
        "receivable_amount": 100000,
        "status": "pending"
      }
    ],
    "total_count": 5,
    "total_value": 500000
  }
}
```

**Key Changes:**
- Wrapped response in `data` object
- Added more fields: `po_date`, `receivable_amount`, `status`

---

## 2. NEW - GET /api/po/{poId}

### NEW Endpoint ✅
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 1,
    "client_po_id": 1,
    "po_number": "PO-001",
    "po_date": "2024-01-15",
    "po_value": 100000,
    "receivable_amount": 100000,
    "status": "pending",
    "po_type": "standard",
    "notes": "Sample PO",
    "line_items": [
      {
        "line_item_id": 10,
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

**Use Case:** Display individual PO details on a detail page

---

## 3. NEW - GET /api/po/{poId}/details (Enhanced)

### NEW Endpoint ✅
```json
{
  "status": "SUCCESS",
  "data": {
    "id": 1,
    "po_number": "PO-001",
    "po_date": "2024-01-15",
    "po_value": 100000,
    "payment_status": "partial",
    "total_paid": 60000,
    "total_tds": 5000,
    "outstanding_amount": 40000,
    "line_items": [...],
    "line_item_count": 2
  }
}
```

**Use Case:** Display PO with payment information (payment status, collected amount, etc.)

---

## 4. NEW - POST /api/billing-po/{billingPoId}/approve

### NEW Endpoint ✅

**Request:**
```json
{
  "notes": "Approved for final billing"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Billing PO approved",
  "data": {
    "billing_po_id": "550e8400-e29b-41d4-a716-446655440000",
    "client_po_id": 1,
    "project_id": 10,
    "po_number": "BILLING-10",
    "billed_value": 100000,
    "billed_gst": 18000,
    "billed_total": 118000,
    "billing_notes": "Approved for final billing",
    "status": "APPROVED",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T11:30:00"
  }
}
```

**Use Case:** Approve billing PO for payment processing

---

## 5. NEW - GET /api/projects/{projectId}/pl-analysis

### NEW Endpoint ✅

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
    "variance_percentage": 4.0,
    "original_budget": 500000,
    "final_revenue": 520000,
    "analysis": {
      "baseline": {
        "po_value": 500000
      },
      "billing": {
        "billed_value": 520000
      },
      "variance": {
        "delta": 20000,
        "delta_percent": 4.0,
        "direction": "up"
      },
      "costs": {
        "vendor_costs": 350000
      },
      "profit_loss": {
        "amount": 170000,
        "margin_percent": 32.69,
        "status": "profit"
      },
      "totals": {
        "revenue": 520000,
        "costs": 350000,
        "profit": 170000
      }
    }
  }
}
```

**Use Case:** Display P&L dashboard, financial analysis, profit margins

**Fields Explanation:**
- `total_po_value`: Original purchase order value
- `total_billed`: Amount billed to client
- `total_vendor_costs`: Total cost from vendors
- `net_profit`: Revenue - Costs
- `profit_margin_percentage`: (Profit / Revenue) * 100
- `variance`: Difference between billed and original PO
- `variance_percentage`: (Variance / Original PO) * 100

---

## 6. NEW - POST /api/vendor-orders/{vendorOrderId}/link-payment

### NEW Endpoint ✅

**Request:**
```json
{
  "link_type": "incoming",
  "amount": 25000,
  "payment_id": "payment-12345"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Payment linked to vendor order",
  "data": {
    "link_id": "link-550e8400",
    "vendor_order_id": 456,
    "link_type": "incoming",
    "amount": 25000,
    "payment_id": "payment-12345",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Parameters:**
- `link_type`: "incoming" (payment received) or "outgoing" (payment sent)
- `amount`: Optional - amount being linked
- `payment_id`: Optional - payment reference ID

**Use Case:** Link client payments to vendor orders for reconciliation

---

## Migration Guide for Frontend

### Step 1: Update PO List Fetch
```javascript
// OLD CODE (BROKEN)
const response = await fetch('/api/po');
const pos = response.json().pos;  // ❌ Error: .pos is undefined

// NEW CODE (FIXED)
const response = await fetch('/api/po');
const { data } = response.json();
const pos = data.pos;  // ✅ Works correctly
```

### Step 2: Add Single PO Fetch
```javascript
// NEW: Get individual PO details
const response = await fetch(`/api/po/${poId}`);
const { data } = response.json();
// data contains: id, po_number, po_value, line_items, etc.
```

### Step 3: Add Enhanced PO Details (with payments)
```javascript
// NEW: Get PO with payment status
const response = await fetch(`/api/po/${poId}/details`);
const { data } = response.json();
// data contains: payment_status, total_paid, outstanding_amount, etc.
```

### Step 4: Add Billing Approval
```javascript
// NEW: Approve billing PO
const response = await fetch(`/api/billing-po/${billingPoId}/approve`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ notes: 'Approved' })
});
const { data } = response.json();
// data.status will be 'APPROVED'
```

### Step 5: Add P&L Analysis
```javascript
// NEW: Get P&L analysis
const response = await fetch(`/api/projects/${projectId}/pl-analysis`);
const { data } = response.json();
// Display: net_profit, profit_margin_percentage, variance, etc.
```

### Step 6: Add Vendor Payment Linking
```javascript
// NEW: Link payment to vendor order
const response = await fetch(`/api/vendor-orders/${vendorOrderId}/link-payment`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    link_type: 'incoming',
    amount: 50000,
    payment_id: 'payment-123'
  })
});
const { data } = response.json();
// data.link_id contains the link reference
```

---

## Testing Checklist

- [ ] Test GET /api/po - verify response has `data.pos`
- [ ] Test GET /api/po/{poId} - verify single PO loads
- [ ] Test GET /api/po/{poId}/details - verify payment info shows
- [ ] Test GET /api/projects - verify projects load
- [ ] Test GET /api/projects/{projectId}/po - verify project POs load
- [ ] Test POST /api/billing-po/{billingPoId}/approve - verify approval works
- [ ] Test GET /api/projects/{projectId}/pl-analysis - verify P&L data shows
- [ ] Test POST /api/vendor-orders/{vendorOrderId}/link-payment - verify payment links
- [ ] Test error cases - 404, 400, etc.
- [ ] Test response times under load
- [ ] Verify all required fields are present in responses
- [ ] Test with invalid IDs - should return 404

---

## Code Examples

### React Hook for Fetching All POs
```javascript
const [pos, setPos] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchPos = async () => {
    try {
      const response = await fetch('/api/po');
      const json = response.json();
      setPos(json.data.pos);  // ✅ Use data.pos
    } catch (error) {
      console.error('Failed to fetch POs:', error);
    } finally {
      setLoading(false);
    }
  };
  fetchPos();
}, []);
```

### React Hook for Single PO Details
```javascript
const [po, setPo] = useState(null);
const [paymentStatus, setPaymentStatus] = useState(null);

useEffect(() => {
  const fetchPoDetails = async () => {
    const response = await fetch(`/api/po/${poId}/details`);
    const { data } = await response.json();
    setPo(data);
    setPaymentStatus(data.payment_status);
  };
  fetchPoDetails();
}, [poId]);
```

---

## Deployment Notes

1. **Database:** All new features use existing tables, no migrations needed
2. **Backward Compatibility:** Old endpoints still work, but GET /api/po response format changed
3. **Performance:** New endpoints use database indexes, should perform well
4. **Error Handling:** All endpoints return standard error format
5. **Timeouts:** No new timeouts added, use existing connection pool

---

## Support

For questions about the changes, refer to:
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `FRONTEND_INTEGRATION_GUIDE.md` - Complete API guide
- Test file: `verify_routes.py` - Working examples

