# API Routes Visualization

## 🎯 Visual Overview of All Changes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PURCHASE ORDERS (Client POs)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ GET /api/po                           [FIXED: response format] │
│     └─ Returns: { data: { pos: [...], total_count, total_value } } │
│     └─ Query: client_id (optional)                                 │
│                                                                     │
│  ⭐ GET /api/po/{poId}                    [NEW ENDPOINT]           │
│     └─ Returns: { data: { id, po_number, po_date, line_items } }  │
│                                                                     │
│  ⭐ GET /api/po/{poId}/details            [NEW ENDPOINT]           │
│     └─ Returns: { data: { ..., payment_status, total_paid } }     │
│                                                                     │
│  ✅ GET /api/projects/{projectId}/po      [WORKING]                │
│     └─ Returns: { pos: [...], total_project_value, primary_po }   │
│                                                                     │
│  ✅ POST /api/projects/{projectId}/po     [WORKING]                │
│     └─ Body: { po_number, po_date, po_value, ... }               │
│                                                                     │
│  ✅ PUT /api/po/{poId}                    [WORKING]                │
│     └─ Body: { po_number?, po_date?, po_value?, ... }            │
│                                                                     │
│  ✅ DELETE /api/po/{poId}                 [WORKING]                │
│     └─ Returns: { status, message, client_po_id }                │
│                                                                     │
│  ✅ POST /api/projects/{projectId}/po/{poId}/attach  [WORKING]    │
│     └─ Query: sequence_order                                       │
│                                                                     │
│  ✅ PUT /api/projects/{projectId}/po/{poId}/set-primary [WORKING] │
│                                                                     │
│  ✅ GET /api/projects/{projectId}/po/enriched [WORKING]           │
│     └─ Returns: POs with payment_status, total_paid, receivable   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          BILLING POs                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ POST /api/projects/{projectId}/billing-po     [WORKING]        │
│     └─ Body: { client_po_id, billed_value, billed_gst, ... }     │
│                                                                     │
│  ✅ GET /api/billing-po/{billingPoId}             [WORKING]        │
│     └─ Returns: { billing_po, line_items }                        │
│                                                                     │
│  ✅ PUT /api/billing-po/{billingPoId}             [WORKING]        │
│     └─ Body: { billed_value?, billed_gst?, billing_notes? }      │
│                                                                     │
│  ⭐ POST /api/billing-po/{billingPoId}/approve    [NEW ENDPOINT]   │
│     └─ Body: { notes?: string }                                   │
│     └─ Returns: { data: { status: "APPROVED", ... } }            │
│                                                                     │
│  ✅ POST /api/billing-po/{billingPoId}/line-items [WORKING]       │
│     └─ Body: { description, qty, rate }                          │
│                                                                     │
│  ✅ GET /api/billing-po/{billingPoId}/line-items  [WORKING]       │
│     └─ Returns: { line_items, line_item_count, total_value }     │
│                                                                     │
│  ✅ DELETE /api/billing-po/{billingPoId}/line-items/{id} [WORKING]│
│                                                                     │
│  ✅ GET /api/projects/{projectId}/billing-summary [WORKING]       │
│     └─ Returns: Financial summary with P&L basics                │
│                                                                     │
│  ⭐ GET /api/projects/{projectId}/pl-analysis     [NEW ENDPOINT]   │
│     └─ Returns: { data: { net_profit, profit_margin_percentage } }│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     VENDORS & VENDOR ORDERS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ GET /api/vendors                              [WORKING]        │
│     └─ Query: status ('active' | 'inactive')                      │
│     └─ Returns: { vendors: [...], vendor_count }                  │
│                                                                     │
│  ✅ GET /api/vendors/{vendorId}                   [WORKING]        │
│                                                                     │
│  ✅ POST /api/vendors                             [WORKING]        │
│     └─ Body: { name, email, phone, address, ... }                │
│                                                                     │
│  ✅ PUT /api/vendors/{vendorId}                   [WORKING]        │
│                                                                     │
│  ✅ DELETE /api/vendors/{vendorId}                [WORKING]        │
│                                                                     │
│  ✅ GET /api/projects/{projectId}/vendor-orders   [WORKING]        │
│     └─ Returns: { vendor_orders, vendor_order_count }            │
│                                                                     │
│  ✅ POST /api/projects/{projectId}/vendor-orders  [WORKING]        │
│     └─ Body: { vendor_id, po_number, po_date, po_value, ... }   │
│                                                                     │
│  ✅ POST /api/projects/{projectId}/vendor-orders/bulk [WORKING]   │
│     └─ Body: { orders: [ { ... }, { ... } ] }                    │
│                                                                     │
│  ✅ PUT /api/vendor-orders/{vendorOrderId}        [WORKING]        │
│     └─ Body: { po_value?, due_date?, description?, ... }        │
│                                                                     │
│  ✅ PUT /api/vendor-orders/{vendorOrderId}/status [WORKING]        │
│     └─ Body: { work_status?, payment_status? }                   │
│                                                                     │
│  ⭐ POST /api/vendor-orders/{vendorOrderId}/link-payment [NEW]     │
│     └─ Body: { link_type: "incoming"|"outgoing", amount?, ... }  │
│     └─ Returns: { data: { link_id, vendor_order_id, ... } }      │
│                                                                     │
│  ✅ GET /api/vendor-orders/{vendorOrderId}/line-items [WORKING]   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         PROJECTS                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ GET /api/projects                             [WORKING]        │
│     └─ Query: skip=0, limit=50                                    │
│     └─ Returns: { projects, project_count }                      │
│                                                                     │
│  ✅ GET /api/projects/{projectId}                 [WORKING]        │
│                                                                     │
│  ✅ POST /api/projects                            [WORKING]        │
│     └─ Body: { name, location, city, state, ... }               │
│                                                                     │
│  ✅ PUT /api/projects/{projectId}                 [WORKING]        │
│                                                                     │
│  ✅ DELETE /api/projects                          [WORKING]        │
│     └─ Query: name                                                │
│                                                                     │
│  ✅ GET /api/projects/{projectId}/financial-summary [WORKING]     │
│     └─ Returns: Comprehensive financial metrics                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         PAYMENTS                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ GET /api/po/{poId}/payments                   [WORKING]        │
│     └─ Returns: { payments, summary, payment_count }             │
│                                                                     │
│  ✅ POST /api/po/{poId}/payments                  [WORKING]        │
│     └─ Body: { payment_date, amount, payment_mode, ... }        │
│                                                                     │
│  ✅ PUT /api/payments/{paymentId}                 [WORKING]        │
│                                                                     │
│  ✅ DELETE /api/payments/{paymentId}              [WORKING]        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      FILE UPLOADS & SESSIONS                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ POST /api/uploads/session                     [WORKING]        │
│     └─ Body: { metadata?, ttl_hours? }                           │
│                                                                     │
│  ✅ POST /api/uploads/session/{sessionId}         [WORKING]        │
│     └─ FormData: file, uploaded_by, po_number (optional)        │
│                                                                     │
│  ✅ GET /api/uploads/session/{sessionId}/files    [WORKING]        │
│     └─ Query: skip=0, limit=50                                   │
│     └─ Returns: { files, session_id, file_count }               │
│                                                                     │
│  ✅ GET /api/po/{poNumber}/files                  [WORKING]        │
│     └─ Query: skip=0, limit=50                                   │
│                                                                     │
│  ✅ GET /api/po/{poNumber}/files/{fileId}/download [WORKING]      │
│     └─ Returns: File blob (binary)                               │
│                                                                     │
│  ✅ POST /api/uploads/bajaj-po                    [WORKING]        │
│     └─ Query: client_id, project_id                              │
│     └─ FormData: file                                            │
│                                                                     │
│  ✅ POST /api/uploads/proforma                    [WORKING]        │
│     └─ Query: client_id, project_id                              │
│     └─ FormData: file                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Working endpoint (no changes needed) |
| ⭐ | NEW endpoint (just implemented) |
| 🔧 | Fixed endpoint (response format changed) |
| ❌ | Broken/Missing (no longer used) |

---

## Changes Summary Dashboard

### Fixed Issues: 1
- ❌ GET /api/po response format ✅ FIXED

### New Endpoints: 5
- ⭐ GET /api/po/{poId}
- ⭐ GET /api/po/{poId}/details
- ⭐ POST /api/billing-po/{billingPoId}/approve
- ⭐ GET /api/projects/{projectId}/pl-analysis
- ⭐ POST /api/vendor-orders/{vendorOrderId}/link-payment

### Working Endpoints: 40+
All other routes are working correctly without changes.

---

## Feature Coverage

### ✅ Purchase Orders: 9/9 routes working
- GET all POs (fixed)
- GET single PO (new)
- GET PO details (new)
- Get project POs
- Create PO
- Update PO
- Delete PO
- Attach PO to project
- Set primary PO
- Enriched view

### ✅ Billing: 8/8 routes working
- Create billing PO
- Get billing PO
- Update billing PO
- Approve billing PO (new)
- Add line items
- Get line items
- Delete line items
- Get P&L analysis (new)

### ✅ Vendors: 6/6 routes working
- Get vendors (with filter)
- Get vendor details
- Create vendor
- Update vendor
- Delete vendor
- [Payment link added to vendor orders]

### ✅ Vendor Orders: 8/8 routes working
- Get project orders
- Create order
- Update order (basic)
- Update order (status)
- Delete order
- Bulk create
- Link payment to order (new)
- Get line items
- Manage line items

### ✅ Payments: 4/4 routes working
- Get payments
- Create payment
- Update payment
- Delete payment

### ✅ File Uploads: 7/7 routes working
- Create session
- Upload file
- List files
- Get files by PO
- Download file
- Upload Bajaj PO
- Upload proforma

---

## Integration Priority (For Frontend)

### Priority 1: CRITICAL (Must integrate)
1. GET /api/po - Response format changed
2. GET /api/po/{poId} - Use for detail views
3. GET /api/po/{poId}/details - Use for payment views

### Priority 2: IMPORTANT (Should integrate)
4. POST /api/billing-po/{billingPoId}/approve - Approval workflow
5. GET /api/projects/{projectId}/pl-analysis - Financial dashboard
6. POST /api/vendor-orders/{vendorOrderId}/link-payment - Payment linking

### Priority 3: OPTIONAL (Nice to have)
- All others (already working)

---

## Data Flow Diagram

```
User Interface
    │
    ├─→ PO List                 [GET /api/po]                ✅ FIXED
    │   ├─→ Click PO            [GET /api/po/{poId}]         ⭐ NEW
    │   └─→ View Details        [GET /api/po/{poId}/details] ⭐ NEW
    │
    ├─→ Project Dashboard       [GET /api/projects]          ✅ WORKING
    │   ├─→ Project POs         [GET /api/projects/{id}/po]  ✅ WORKING
    │   └─→ P&L Analysis        [GET /api/projects/{id}/pl-analysis] ⭐ NEW
    │
    ├─→ Billing Workflow        [POST /api/billing-po]       ✅ WORKING
    │   └─→ Approve             [POST /api/billing-po/{id}/approve] ⭐ NEW
    │
    ├─→ Vendor Management       [GET /api/vendors]           ✅ WORKING
    │   ├─→ Vendor Orders       [POST /api/vendor-orders]    ✅ WORKING
    │   └─→ Link Payment        [POST /api/vendor-orders/{id}/link-payment] ⭐ NEW
    │
    └─→ Payments                [GET /api/po/{id}/payments]  ✅ WORKING
```

---

## Testing Matrix

### Test Scenarios

| Scenario | Endpoint | Expected Result |
|----------|----------|-----------------|
| Get all POs | GET /api/po | Returns wrapped data in `.data.pos` |
| Get single PO | GET /api/po/{poId} | Returns PO with line_items |
| Get PO details with payments | GET /api/po/{poId}/details | Returns with payment_status |
| Approve billing | POST /api/billing-po/{id}/approve | Status changes to APPROVED |
| View P&L | GET /api/projects/{id}/pl-analysis | Shows net_profit and margin |
| Link payment | POST /api/vendor-orders/{id}/link-payment | Creates link and returns link_id |

---

## Rollout Plan

### Phase 1: Backend Deployment
- [ ] Deploy updated code to production
- [ ] Run database migrations (none needed)
- [ ] Test all endpoints
- [ ] Verify error handling

### Phase 2: Frontend Integration
- [ ] Update PO list fetch with new response format
- [ ] Add single PO detail view
- [ ] Add payment details view
- [ ] Add billing approval workflow
- [ ] Add P&L dashboard
- [ ] Add vendor payment linking

### Phase 3: Testing & Validation
- [ ] User testing
- [ ] Performance testing
- [ ] Load testing
- [ ] Error scenario testing

### Phase 4: Release
- [ ] Deploy frontend
- [ ] Monitor for issues
- [ ] Gather user feedback

