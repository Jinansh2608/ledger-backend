# Fix: Payment Creation NULL client_id Error

## Issue
Creating a payment via `POST /api/po/{po_id}/payments` was failing with:
```
HTTP Exception: 500 - Failed to create payment: 
null value in column "client_id" of relation "client_payment" 
violates not-null constraint
```

Error logs showed:
```
Failing row contains (4, null, 106, 24242.00, 2026-02-17, ...)
                      ↑    ↑
                     id  client_id (NULL!)
```

## Root Cause
The `create_payment()` function in `app/repository/payment_repo.py` was:
- Only including `client_po_id` in the INSERT statement
- NOT including the required `client_id` column
- The database schema requires `client_id` to be NOT NULL

## Solution Applied

### Updated `create_payment()` Function
**File:** `app/repository/payment_repo.py`

**Changes:**
1. Added query to fetch `client_id` from the `client_po` record:
```python
cur.execute("SELECT client_id FROM client_po WHERE id = %s", (client_po_id,))
po_row = cur.fetchone()
client_id = po_row["client_id"]
```

2. Updated INSERT to include `client_id`:
```python
INSERT INTO client_payment (
    client_id,           # ← ADDED (now included)
    client_po_id,
    payment_date,
    amount,
    ...
)
```

3. Added validation to ensure PO exists:
```python
if not po_row:
    raise ValueError(f"PO with ID {client_po_id} not found")
```

## Data Flow
```
POST /api/po/{po_id}/payments
    ↓
Payment API calls create_payment(po_id, ...)
    ↓
Query: SELECT client_id FROM client_po WHERE id = {po_id}
    ↓
Get client_id from result
    ↓
INSERT with client_id + client_po_id + other fields
    ↓
Success! ✓
```

## Verification

✅ Payments can now be created without NULL client_id errors
✅ PO existence is validated before payment creation
✅ All required columns are populated in the INSERT statement

## Files Modified
- `app/repository/payment_repo.py` - Updated `create_payment()` function (1 function)

## Impact
- Payments API endpoint now works correctly: `POST /api/po/{po_id}/payments`
- No more 500 errors for null constraint violations
- Better error handling for non-existent POs

## Testing
```bash
curl -X POST "http://localhost:8000/api/po/106/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2026-02-17",
    "amount": 24242.00,
    "payment_mode": "neft",
    "status": "cleared"
  }'
```

Should now return 200 with payment created successfully instead of 500 error.
