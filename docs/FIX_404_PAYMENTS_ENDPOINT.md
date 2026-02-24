# 404 Error Fix - Payments Endpoint

## Issue
Frontend was getting 404 errors when calling `/api/payments` endpoint:
```
WARNING - HTTP Exception: 404 - Not Found - Path: /api/payments
```

## Root Cause
The `GET /api/payments` endpoint was missing from the payments API module. The payments.py only had nested endpoints like:
- `POST /api/po/{po_id}/payments`
- `GET /api/po/{po_id}/payments`
- `PUT /api/payments/{payment_id}`
- `DELETE /api/payments/{payment_id}`

But no root `/api/payments` endpoint for getting all payments.

## Solution Applied

### 1. Added Missing Repository Functions
**File:** `app/repository/payment_repo.py`

Added two new functions:
- `get_all_payments(skip: int, limit: int) -> List[Dict]` - Returns paginated list of all payments
- `get_total_payment_count() -> int` - Returns total count of payments

### 2. Added Missing API Endpoint
**File:** `app/apis/payments.py`

Added new GET endpoint:
```python
@router.get("/payments")
def get_all_payments(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=500)):
    """Get all payments with optional pagination"""
    # Returns paginated payments list with total count
```

**Response:**
```json
{
  "status": "SUCCESS",
  "payments": [...],
  "payment_count": 10,
  "total_count": 45,
  "skip": 0,
  "limit": 50
}
```

## Verification

✅ Endpoint now registered: `GET /api/payments`
✅ Supports pagination with `skip` and `limit` query parameters
✅ Returns all payments in database with metadata
✅ Handles edge cases (empty results, invalid parameters)

## Files Modified
1. `app/repository/payment_repo.py` - Added 2 functions
2. `app/apis/payments.py` - Added 1 endpoint

## All Payment Endpoints Now Available
- `GET /api/payments` - Get all payments (NEW ✓)
- `POST /api/po/{po_id}/payments` - Create payment for PO
- `GET /api/po/{po_id}/payments` - Get payments for specific PO
- `PUT /api/payments/{payment_id}` - Update payment
- `DELETE /api/payments/{payment_id}` - Delete payment
- Related: `/api/vendor-orders/{vo_id}/payments`, etc.

## Testing
The 404 errors for `/api/payments` should now be resolved. Frontend can now call:
```bash
curl http://localhost:8000/api/payments?skip=0&limit=50
```
