# Before & After Code Examples - Schema Migration

## Context
These are real code patterns from the current codebase showing what needs to change.

---

## Example 1: Billing PO Creation Function

### ❌ BEFORE (OLD SCHEMA - Will Fail)

```python
# app/repository/billing_po_repo.py

def create_billing_po(
    client_po_id: str,
    project_id: str,
    billed_value: float,
    billed_gst: float,
    billed_total: float,
    notes: str = None
):
    """
    Problem: Many columns don't exist in new schema
    - id: generating UUID instead of auto-BIGSERIAL
    - project_id: removed from new schema
    - billed_gst: removed (only amount now)
    - billed_total: removed (only amount now)
    """
    try:
        # ❌ Generates UUID - new schema uses BIGSERIAL auto-increment
        billing_po_id = str(uuid4())
        
        # ❌ project_id parameter doesn't exist in new schema
        query = """
            INSERT INTO billing_po 
            (id, client_po_id, project_id, billed_value, billed_gst, billed_total, notes, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
        """
        
        params = (
            billing_po_id,
            client_po_id,
            project_id,        # ❌ Column removed
            billed_value,      # ❌ Column renamed to 'amount'
            billed_gst,        # ❌ Column removed (single amount)
            billed_total,      # ❌ Column removed (single amount)
            notes,             # ❌ Column removed
        )
        
        execute_query(query, params)
        return {"id": billing_po_id, "status": "created"}
        
    except Exception as e:
        logger.error(f"Error creating billing PO: {str(e)}")
        return {"error": str(e)}


def add_billing_line_item(
    billing_po_id: str,
    description: str,
    qty: int,          # ❌ Column name 'qty' → 'quantity'
    rate: float,       # ❌ Column name 'rate' → 'unit_price'
    total: float = None
):
    """
    Problem: Line item columns renamed, id should be auto-generated
    """
    try:
        line_item_id = str(uuid4())  # ❌ Should use BIGSERIAL
        
        query = """
            INSERT INTO billing_po_line_item 
            (id, billing_po_id, description, qty, rate, total, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        
        params = (
            line_item_id,
            billing_po_id,
            description,       # ❌ Column renamed to 'item_description'
            qty,               # ❌ Column name wrong
            rate,              # ❌ Column name wrong
            total or (qty * rate),  # ❌ Calculate or fail
        )
        
        execute_query(query, params)
        return {"id": line_item_id}
        
    except Exception as e:
        logger.error(f"Error adding line item: {str(e)}")
        return {"error": str(e)}


def get_billing_po(billing_po_id: str):
    """
    Problem: Queries removed columns
    """
    query = """
        SELECT 
            id, client_po_id, project_id, billed_value, 
            billed_gst, billed_total, notes, status, created_at
        FROM billing_po
        WHERE id = %s
    """
    # ❌ Will fail: project_id, billed_gst, billed_total don't exist
    
    result = execute_query(query, (billing_po_id,), fetch_one=True)
    return result
```

---

### ✅ AFTER (NEW SCHEMA - Will Work)

```python
# app/repository/billing_po_repo.py

def create_billing_po(
    client_id: str,
    po_number: str,
    amount: float,
    status: str = "pending"
):
    """
    SIMPLIFIED: Only essential fields
    - id: auto-generated BIGSERIAL
    - No more project_id (link is via po_project_mapping if needed)
    - No more separate gst/total (single amount field)
    - Simpler, cleaner function
    """
    try:
        # ✅ Don't generate id - use auto-BIGSERIAL
        query = """
            INSERT INTO billing_po 
            (client_id, po_number, amount, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        """
        
        params = (
            client_id,
            po_number,
            amount,
            status,
        )
        
        result = execute_query(query, params, fetch_one=True)
        return {"id": result['id'], "status": "created"}
        
    except Exception as e:
        logger.error(f"Error creating billing PO: {str(e)}")
        return {"error": str(e)}


def add_billing_line_item(
    billing_po_id: int,              # Now BIGINT
    item_description: str,            # ✅ Renamed from 'description'
    quantity: int,                    # ✅ Renamed from 'qty'
    unit_price: float,                # ✅ Renamed from 'rate'
    amount: float = None
):
    """
    SIMPLIFIED: Clearer naming, auto id
    """
    try:
        # ✅ Don't generate id - let database auto-generate
        query = """
            INSERT INTO billing_po_line_item 
            (billing_po_id, item_description, quantity, unit_price, amount, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """
        
        params = (
            billing_po_id,
            item_description,
            quantity,
            unit_price,
            amount or (quantity * unit_price),
        )
        
        result = execute_query(query, params, fetch_one=True)
        return {"id": result['id']}
        
    except Exception as e:
        logger.error(f"Error adding line item: {str(e)}")
        return {"error": str(e)}


def get_billing_po(billing_po_id: int):
    """
    SIMPLIFIED: Only queries existing columns
    """
    query = """
        SELECT 
            id, client_id, po_number, amount, status, created_at
        FROM billing_po
        WHERE id = %s
    """
    # ✅ All columns exist in new schema
    
    result = execute_query(query, (billing_po_id,), fetch_one=True)
    return result
```

---

## Example 2: Vendor Order Management

### ❌ BEFORE (OLD SCHEMA - Will Fail)

```python
# app/repository/vendor_order_repo.py

def create_vendor_order(
    vendor_id: str,
    project_id: str,           # ❌ Not in new schema
    po_date: str,              # ❌ Column removed
    po_value: float,           # ❌ Renamed to 'amount'
    due_date: str,             # ❌ Column removed
    work_status: str,          # ❌ Column removed
    description: str,          # ❌ Column removed
):
    """
    Problem: 7+ columns that don't exist in new schema
    """
    try:
        vendor_order_id = str(uuid4())
        
        query = """
            INSERT INTO vendor_order 
            (id, vendor_id, project_id, po_date, po_value, due_date, work_status, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
        """
        
        params = (
            vendor_order_id,
            vendor_id,
            project_id,        # ❌ Removed
            po_date,           # ❌ Removed
            po_value,          # ❌ Renamed
            due_date,          # ❌ Removed
            work_status,       # ❌ Removed
        )
        
        execute_query(query, params)
        return vendor_order_id
        
    except Exception as e:
        logger.error(f"Failed to create vendor order: {str(e)}")


def get_vendor_order_payments(vendor_order_id: str):
    """
    Problem: Queries for payment_id field that doesn't exist
    """
    query = """
        SELECT 
            vp.id, vp.vendor_id, vp.amount, vp.payment_date,
            pvl.payment_id,              # ❌ Column renamed to 'vendor_payment_id'
            pvl.vendor_order_id, pvl.amount_allocated
        FROM vendor_payment vp
        JOIN payment_vendor_link pvl ON vp.id = pvl.payment_id  # ❌ Wrong FK
        WHERE pvl.vendor_order_id = %s
    """
    # ❌ Will fail: payment_id doesn't exist (now vendor_payment_id)
    
    return execute_query(query, (vendor_order_id,), fetch_all=True)


def delete_vendor_order(vendor_order_id: str):
    """
    Problem: Assumes project_id column exists
    """
    try:
        # Get related data
        query = """
            SELECT project_id FROM vendor_order WHERE id = %s
        """
        # ❌ Will fail: project_id doesn't exist
        
        result = execute_query(query, (vendor_order_id,), fetch_one=True)
        project_id = result['project_id']
        
        # Then delete...
        delete_query = """DELETE FROM vendor_order WHERE id = %s"""
        execute_query(delete_query, (vendor_order_id,))
        
    except Exception as e:
        logger.error(f"Failed to delete vendor order: {str(e)}")
```

### ✅ AFTER (NEW SCHEMA - Will Work)

```python
# app/repository/vendor_order_repo.py

def create_vendor_order(
    vendor_id: str,
    po_number: str,
    amount: float,
    status: str = "pending"
):
    """
    SIMPLIFIED: Only essential fields
    - No project_id (simpler relationship)
    - No dates (if needed, add as separate field)
    - No work/payment status (use single 'status' field)
    """
    try:
        # ✅ Don't generate id
        query = """
            INSERT INTO vendor_order 
            (vendor_id, po_number, amount, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        """
        
        params = (vendor_id, po_number, amount, status)
        
        result = execute_query(query, params, fetch_one=True)
        return {"id": result['id']}
        
    except Exception as e:
        logger.error(f"Failed to create vendor order: {str(e)}")
        return {"error": str(e)}


def get_vendor_order_payments(vendor_order_id: int):
    """
    SIMPLIFIED: Corrected FK references
    """
    query = """
        SELECT 
            vp.id, vp.vendor_id, vp.amount, vp.payment_date, vp.status,
            pvl.vendor_payment_id,      # ✅ Correct column name
            pvl.vendor_order_id, pvl.amount_allocated
        FROM vendor_payment vp
        JOIN payment_vendor_link pvl ON vp.id = pvl.vendor_payment_id  # ✅ Correct
        WHERE pvl.vendor_order_id = %s
    """
    # ✅ All columns exist and correct
    
    return execute_query(query, (vendor_order_id,), fetch_all=True)


def delete_vendor_order(vendor_order_id: int):
    """
    SIMPLIFIED: No project_id to worry about, CASCADE handles line items
    """
    try:
        # Database CASCADE will handle vendor_order_line_item
        delete_query = """DELETE FROM vendor_order WHERE id = %s"""
        execute_query(delete_query, (vendor_order_id,))
        return {"status": "deleted"}
        
    except Exception as e:
        logger.error(f"Failed to delete vendor order: {str(e)}")
        return {"error": str(e)}
```

---

## Example 3: Payment Repository Changes

### ❌ BEFORE (OLD SCHEMA - Will Fail)

```python
# app/repository/payment_repo.py

def create_client_payment(
    client_id: str,
    client_po_id: str,
    amount: float,
    payment_date: str,
    payment_mode: str,          # ❌ Removed
    reference_number: str,      # ❌ Removed
    tds_deducted: bool,         # ❌ Removed
    tds_amount: float,          # ❌ Removed
    notes: str,                 # ❌ Removed
):
    """
    Problem: 5+ unnecessary fields that don't exist in new schema
    """
    try:
        query = """
            INSERT INTO client_payment 
            (id, client_id, client_po_id, amount, payment_date, payment_mode, 
             reference_number, tds_deducted, tds_amount, notes, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'received', NOW())
        """
        
        params = (
            str(uuid4()),
            client_id, client_po_id, amount, payment_date,
            payment_mode,       # ❌ Removed
            reference_number,   # ❌ Removed
            tds_deducted,       # ❌ Removed
            tds_amount,         # ❌ Removed
            notes,              # ❌ Removed
        )
        
        execute_query(query, params)
        # ...
        
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")


def list_client_payments(client_id: str):
    """
    Problem: Queries for removed columns
    """
    query = """
        SELECT 
            id, client_id, client_po_id, amount, payment_date,
            payment_mode, reference_number, payment_stage,
            tds_deducted, tds_amount, notes, status, created_at
        FROM client_payment
        WHERE client_id = %s
        ORDER BY payment_date DESC
    """
    # ❌ Will fail: half these columns don't exist
    
    return execute_query(query, (client_id,), fetch_all=True)
```

### ✅ AFTER (NEW SCHEMA - Will Work)

```python
# app/repository/payment_repo.py

def create_client_payment(
    client_id: str,
    client_po_id: str,
    amount: float,
    payment_date: str,
    status: str = "pending"
):
    """
    SIMPLIFIED: Only essential payment fields
    - No payment_mode (not tracked in new schema)
    - No reference_number (not tracked)
    - No TDS tracking (out of scope)
    - No notes (not tracked)
    """
    try:
        query = """
            INSERT INTO client_payment 
            (client_id, client_po_id, amount, payment_date, status, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """
        
        params = (
            client_id, client_po_id, amount, payment_date, status
        )
        
        result = execute_query(query, params, fetch_one=True)
        return {"id": result['id']}
        
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        return {"error": str(e)}


def list_client_payments(client_id: str):
    """
    SIMPLIFIED: Only existing columns
    """
    query = """
        SELECT 
            id, client_id, client_po_id, amount, payment_date, status, created_at
        FROM client_payment
        WHERE client_id = %s
        ORDER BY payment_date DESC
    """
    # ✅ All columns exist
    
    return execute_query(query, (client_id,), fetch_all=True)
```

---

## Key Patterns to Apply

### Pattern 1: ID Generation
```python
# ❌ OLD - Generate UUID in code
id = str(uuid4())

# ✅ NEW - Let database auto-generate
# Don't specify id, use RETURNING clause
query = """INSERT INTO table (...) VALUES (...) RETURNING id"""
```

### Pattern 2: Column Names
```
# ❌ OLD → ✅ NEW
qty → quantity
rate → unit_price
description → item_description
po_value → amount
billed_value → amount
payment_id → vendor_payment_id
```

### Pattern 3: Removed Columns (Don't use them)
```
❌ project_id (from billing_po, vendor_order)
❌ po_date, due_date (from vendor_order)
❌ work_status, payment_status (from vendor_order)
❌ billed_gst, billed_total (from billing_po)
❌ payment_mode, reference_number (from client_payment)
❌ tds_deducted, tds_amount (from client_payment)
❌ notes, description (simplified fields)
```

### Pattern 4: SELECT Queries
```python
# ❌ OLD - Selecting removed columns
SELECT ... po_date, due_date, work_status FROM ...

# ✅ NEW - Only existing columns
SELECT id, vendor_id, po_number, amount, status, created_at FROM ...
```

### Pattern 5: Function Parameters
```python
# ❌ OLD - Too many params, some removed
def func(vendor_id, project_id, po_date, po_value, due_date, work_status):

# ✅ NEW - Only essential params
def func(vendor_id, po_number, amount, status="pending"):
```

---

## Migration Checklist

For each repository file:

- [ ] Remove UUID generation for ids
- [ ] Remove all `project_id` parameters and references
- [ ] Replace all `qty` with `quantity`
- [ ] Replace all `rate` with `unit_price`
- [ ] Replace all `billed_value/billed_total/billed_gst` with `amount`
- [ ] Replace all `po_value` with `amount`
- [ ] Remove `po_date`, `due_date` parameters
- [ ] Remove `work_status`, `payment_status` (use single `status`)
- [ ] Remove `payment_mode`, `reference_number`, `tds_*` fields
- [ ] Remove `notes` and extra `description` fields
- [ ] Update all SELECT queries to use new columns only
- [ ] Add RETURNING clause to INSERT statements
- [ ] Test all CRUD operations
- [ ] Verify no orphaned references

---

## Files Ready to Update

1. **app/repository/billing_po_repo.py** - 30 min
2. **app/repository/vendor_order_repo.py** - 30 min  
3. **app/repository/payment_repo.py** - 20 min
4. **app/repository/po_management_repo.py** - 20 min

**Total Time: ~2 hours for all updates**

---

Ready to start? I can update these files one by one.
