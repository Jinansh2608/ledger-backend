# Frontend Payments Integration Guide

## ✅ Backend Status: WORKING
Payments API is fully functional and returning data correctly.

---

## 📋 Available API Endpoints

### 1. Get All Payments (Global)
```
GET /api/payments?skip=0&limit=50
```

**Response:**
```json
{
  "status": "SUCCESS",
  "payments": [
    {
      "id": 10,
      "client_po_id": 115,
      "payment_date": "2026-02-17",
      "amount": 11.0,
      "payment_mode": "neft",
      "status": "cleared",
      "payment_stage": "other",
      "reference_number": "REF-1771353856451",
      "is_tds_deducted": false,
      "tds_amount": 0,
      "transaction_type": "credit"
    }
  ],
  "payment_count": 3,
  "total_count": 3,
  "skip": 0,
  "limit": 50
}
```

---

### 2. Get Payments for Specific PO
```
GET /api/po/{po_id}/payments
```

**Response:**
```json
{
  "status": "SUCCESS",
  "po_id": 106,
  "payments": [
    {
      "id": 12,
      "client_po_id": 106,
      "payment_date": "2026-02-17",
      "amount": 10000.0,
      "payment_mode": "neft",
      "reference_number": "REF-1771354292199",
      "status": "pending",
      "payment_stage": "other",
      "is_tds_deducted": false,
      "tds_amount": 0,
      "created_at": "2026-02-18T00:21:32.513534"
    }
  ],
  "payment_count": 2,
  "summary": {
    "total_paid": 100000.0,
    "total_tds": 0.0,
    "cleared_count": 1,
    "pending_count": 1,
    "bounced_count": 0
  }
}
```

---

### 3. Create Payment
```
POST /api/po/{po_id}/payments
Content-Type: application/json

{
  "payment_date": "2026-02-17",
  "amount": 10000.0,
  "payment_mode": "neft",
  "status": "pending",
  "reference_number": "REF-123456",
  "is_tds_deducted": false,
  "tds_amount": 0
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Payment recorded",
  "payment_id": 12,
  "payment_date": "2026-02-17",
  "amount": 10000.0,
  "payment_mode": "neft",
  "payment_stage": "other",
  "payment_status": "pending",
  "transaction_type": "credit"
}
```

---

## 🎯 Frontend Implementation Checklist

### For PO Details Page:
- [ ] When fetching PO details (GET /api/po/{po_id})
- [ ] Also fetch payments: GET /api/po/{po_id}/payments
- [ ] Display "Payments" section showing:
  - [ ] List of all payments
  - [ ] Payment summary stats (total_paid, cleared_count, pending_count)
  - [ ] Payment date, amount, status, mode
- [ ] Add "Record Payment" button
- [ ] After creating payment, refresh the payments list

### For Payment Creation Modal/Form:
- [ ] Form fields:
  - [ ] Payment Date (date picker)
  - [ ] Amount (number input)
  - [ ] Payment Mode (select: neft, cheque, rtgs, etc.)
  - [ ] Status (select: pending, cleared, bounced)
  - [ ] Reference Number (text input)
  - [ ] Optional TDS section
- [ ] Validation: all required fields must be filled
- [ ] After successful POST, refresh payments list

### For Global Payments Dashboard:
- [ ] Call: GET /api/payments?skip=0&limit=50
- [ ] Display paginated list of all payments
- [ ] Use skip/limit for pagination
- [ ] Show payment info with PO ID link

---

## 📊 Payment Fields Reference

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `id` | int | 12 | Payment ID (read-only) |
| `client_po_id` | int | 106 | Link to PO |
| `payment_date` | string | "2026-02-17" | ISO date |
| `amount` | float | 10000.0 | Payment amount |
| `payment_mode` | string | "neft" | neft/cheque/rtgs/etc |
| `status` | string | "pending" | pending/cleared/bounced |
| `payment_stage` | string | "other" | Payment stage |
| `reference_number` | string | "REF-123456" | Unique reference |
| `is_tds_deducted` | boolean | false | TDS applied |
| `tds_amount` | float | 0 | TDS amount |
| `transaction_type` | string | "credit" | credit/debit |
| `created_at` | string | "2026-02-18T00:21:32" | ISO datetime (read-only) |

---

## 💡 Implementation Tips

### Display Payment Status with Colors
```javascript
const statusColors = {
  'cleared': 'green',
  'pending': 'yellow',
  'bounced': 'red'
};
```

### Format Payment Amount
```javascript
const formatted = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR'
}).format(payment.amount);
```

### Display Payment Summary
```javascript
const summary = summaryData;
// Shows: "₹100,000 cleared (1 payment) + ₹0 pending (1 payment)"
```

### Refresh After Payment Creation
```javascript
// After POST /api/po/{po_id}/payments succeeds
await fetchPayments(po_id); // Refresh the payments list
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Payments not showing | Check if GET /api/po/{po_id}/payments is being called |
| Payments disappear after create | Implement auto-refresh after POST success |
| Wrong payment amounts | Check if you're using `amount` (not `total_amount`) |
| Status not updating | Need to call PUT /api/payments/{payment_id} to update |
| TDS not showing | Check `is_tds_deducted` boolean and `tds_amount` field |

---

## ✅ Test Data Available
- **Total payments in system:** 3
- **Sample PO with payments:** 106 (has 2 payments)
- **Status breakdown:** 1 cleared, 1 pending, 1 bounced

You can test with these PO IDs to see real payment data!

---

## Next Steps
1. Add Payments section to PO details page UI
2. Implement payment creation form
3. Add payment list refresh after creation
4. Add payment status filtering/sorting
5. Test with sample data (PO 106, 115)
