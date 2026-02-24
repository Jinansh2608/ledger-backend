# Implementation Roadmap - Schema Alignment

## Current State
✅ App loads successfully (94 routes registered)  
✅ Database schema optimized (18 tables, minimal columns)  
✅ File upload pipeline operational  
❌ Financial operations need code updates  

---

## Phase 1: Code Base Alignment (Priority: HIGH)

### File 1: `app/repository/billing_po_repo.py`
**Status**: Needs major refactor  
**Impact**: Billing PO CRUD operations  

**Changes Needed:**
```python
# BEFORE (OLD SCHEMA)
def create_billing_po(id=None, client_po_id, project_id, billed_value, billed_gst, billed_total):
    # Generates UUID for id
    # Stores billing_po_id (should link to client_po anyway)

# AFTER (NEW SCHEMA)
def create_billing_po(client_id, po_number, amount, status="pending"):
    # id: auto-generated BIGSERIAL
    # client_id: direct from client
    # po_number: from source data
    # amount: total (no separate gst column)
    # status: "pending", "partial", "completed"

# BEFORE - Line items
def add_billing_line_item(id, description, qty, rate):
    # Creates billing_po_line_item with UUID

# AFTER - Line items
def add_billing_line_item(billing_po_id, item_description, quantity, unit_price, amount):
    # Uses BIGSERIAL auto-ID
    # Simpler naming (quantity not qty, unit_price not rate)
```

**Action Items:**
- [ ] Remove UUID generation (use auto-BIGSERIAL)
- [ ] Remove `project_id` parameter
- [ ] Change `billed_value/billed_gst` → `amount` (single field)
- [ ] Update line item columns: qty→quantity, rate→unit_price
- [ ] Update all SELECT queries to use new columns
- [ ] Test CREATE and READ operations

**Estimated Effort**: 30 minutes

---

### File 2: `app/repository/vendor_order_repo.py`
**Status**: Needs major refactor  
**Impact**: Vendor order creation & linkage  

**Changes Needed:**
```python
# BEFORE (OLD SCHEMA) - 15+ unnecessary columns
def create_vendor_order(
    vendor_id, project_id, po_date, po_value,
    due_date, work_status, payment_status,
    description, reference, po_type, notes
):
    # Many fields not in new schema

# AFTER (NEW SCHEMA) - 6 essential columns
def create_vendor_order(
    vendor_id, po_number, amount, status="pending"
):
    # vendor_id: links to vendor
    # po_number: unique identifier
    # amount: total order value
    # status: "pending", "partial", "completed"
    # id & created_at: auto-generated

# BEFORE - Payment linkage
def get_vendor_order_payments(vendor_order_id):
    # Has payment_id field

# AFTER - Payment linkage
def get_vendor_order_payments(vendor_order_id):
    # Has vendor_payment_id field (renamed)
```

**Action Items:**
- [ ] Remove `project_id` from function parameters
- [ ] Remove: po_date, due_date, work_status, payment_status, description
- [ ] Change `po_value` → `amount`
- [ ] Update line item structure (same as billing_po)
- [ ] Update payment_vendor_link references (payment_id → vendor_payment_id)
- [ ] Update all SELECT queries
- [ ] Test CREATE and READ operations

**Estimated Effort**: 30 minutes

---

### File 3: `app/repository/payment_repo.py`
**Status**: Needs moderate refactor  
**Impact**: All payment operations  

**Changes Needed:**
```python
# BEFORE (OLD SCHEMA) - 15+ columns
client_payment: [
    id, client_id, client_po_id, amount, payment_date, status,
    payment_mode, reference_number, payment_stage,
    tds_deducted, tds_amount, transaction_type, notes,
    bank_details, clearing_status, ...
]

# AFTER (NEW SCHEMA) - 7 essential columns
client_payment: [
    id, client_id, client_po_id, amount, payment_date, status, created_at
]

# BEFORE - Function signature
def create_client_payment(
    client_id, client_po_id, amount, payment_date,
    payment_mode, reference_number, tds_deducted, tds_amount,
    payment_stage, notes, bank_details
):

# AFTER - Function signature
def create_client_payment(
    client_id, client_po_id, amount, payment_date
):
    # status: default "pending"
    # created_at: auto-generated
```

**Action Items:**
- [ ] Remove: payment_mode, reference_number, tds_deducted, tds_amount, payment_stage
- [ ] Remove: notes, bank_details, transaction_type, clearing_status
- [ ] Simplify create/read functions
- [ ] Update all SELECT queries
- [ ] Remove any reference to these deleted columns
- [ ] Test payment CREATE, READ, UPDATE operations

**Estimated Effort**: 20 minutes

---

### File 4: `app/repository/po_management_repo.py`
**Status**: Needs moderate update  
**Impact**: Cascade delete logic  

**Changes Needed:**
```python
# BEFORE - delete_po() logic
def delete_po(po_id):
    # Deletes from: billing_po (project_id constraint)
    # Deletes from: vendor_order (project_id constraint)
    # Complex join logic

# AFTER - delete_po() logic
def delete_po(po_id):
    # Deletes from: client_po
    # Cascade deletes: client_po_line_item
    # Cascade deletes: billing_po (FK client_id)
    # Cascade deletes: client_payment
    # Via po_project_mapping: related projects
    # Simpler - project_id no longer in vendor_order

# BEFORE - delete_project() logic
def delete_project(project_id):
    # Complex joins with project_id in multiple tables

# AFTER - delete_project() logic
def delete_project(project_id):
    # Uses po_project_mapping (only link now)
    # Cascade deletes: project_document
    # Cascade deletes: upload_files via mapping
    # Simpler - fewer tables to check
```

**Action Items:**
- [ ] Remove project_id checks from vendor_order deletion
- [ ] Update billing_po deletion cascade (use client_id link)
- [ ] Simplify delete_project() - only check po_project_mapping
- [ ] Update all FK constraints in deletion logic
- [ ] Test cascade delete operations
- [ ] Verify no orphaned records remain

**Estimated Effort**: 20 minutes

---

### File 5: `app/apis/billing_po.py` (If exists)
**Status**: Likely needs update  
**Impact**: API endpoints  

**Changes Needed:**
- [ ] Update request models to use new fields
- [ ] Remove: project_id, billed_gst, billed_total
- [ ] Keep: client_id, po_number, amount, status
- [ ] Update response models
- [ ] Update POST/GET/PUT/DELETE handlers
- [ ] Test all endpoints

**Estimated Effort**: 15 minutes

---

## Phase 2: Verification (Priority: HIGH)

### Database Verification
- [ ] Verify all 18 tables exist
- [ ] Verify column structure matches schema
- [ ] Verify FK constraints with CASCADE deletes
- [ ] Verify all business data intact (2 clients, 2 vendors, 4 POs, etc.)

**Command:**
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
\d billing_po  -- view structure
\d+ client_po  -- view with constraints
```

### App Startup Verification
```bash
# Should load successfully
python run.py

# Check output
# ✅ 94 routes loaded
# ✅ Database connected
# ✅ Redis connected (if applicable)
```

### File Upload Pipeline Test
- [ ] Create upload session
- [ ] Upload Excel file
- [ ] Parse PO
- [ ] Verify PO created in `client_po` table
- [ ] Verify line items in `client_po_line_item` table

**Using Postman Collection:**
```
1. POST /api/uploads/session → Get session_id
2. POST /api/uploads/session/{id}/files → Upload file
3. POST /api/uploads/po/upload → Parse (should create client_po)
4. GET /api/uploads/session/{id}/files → Verify
```

---

## Phase 3: Financial Operations Testing (Priority: MEDIUM)

### Billing PO Operations
- [ ] Create billing_po from client_po
- [ ] Add line items
- [ ] List all billing_po
- [ ] Update status
- [ ] Delete billing_po (cascade check)

### Vendor Order Operations
- [ ] Create vendor_order for vendor
- [ ] Add line items
- [ ] List all vendor_order
- [ ] Link to payments
- [ ] Delete vendor_order (cascade check)

### Payment Tracking
- [ ] Create client_payment
- [ ] Create vendor_payment
- [ ] Link payments (payment_vendor_link)
- [ ] Query payment status
- [ ] Delete payment (cascade check)

---

## Timeline Estimate

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1.1 | Update billing_po_repo.py | 30 min | ⏳ Ready |
| 1.2 | Update vendor_order_repo.py | 30 min | ⏳ Ready |
| 1.3 | Update payment_repo.py | 20 min | ⏳ Ready |
| 1.4 | Update po_management_repo.py | 20 min | ⏳ Ready |
| 1.5 | Update API models | 15 min | ⏳ Ready |
| **Phase 1 Total** | **Code updates** | **~2 hours** | |
| 2 | Database & app verification | 30 min | ⏳ Ready |
| 3 | Financial ops testing | 1 hour | ⏳ Ready |
| **Total** | **Complete system** | **~3.5 hours** | |

---

## Files Ready for Update
- ✅ [app/repository/billing_po_repo.py](app/repository/billing_po_repo.py)
- ✅ [app/repository/vendor_order_repo.py](app/repository/vendor_order_repo.py)
- ✅ [app/repository/payment_repo.py](app/repository/payment_repo.py)
- ✅ [app/repository/po_management_repo.py](app/repository/po_management_repo.py)

---

## Success Criteria

✅ App loads without errors  
✅ All 94 routes registered  
✅ Database connectivity confirmed  
✅ File upload pipeline works end-to-end  
✅ PO creation from uploaded files  
✅ Billing PO CRUD operations  
✅ Vendor order CRUD operations  
✅ Payment tracking operations  
✅ Cascade deletes work correctly  
✅ No orphaned records  
✅ All tests pass  

---

## Notes

- Schema is finalized and tested
- All tables created with proper constraints
- Database integrity verified
- App loads successfully (confirmed)
- **Only code updates remain** - no more schema changes needed
- Updates are straightforward column/logic changes, not architecture changes

---

## Ready to Proceed?

Answer: **Yes** - Start with Phase 1.1 (billing_po_repo.py)
