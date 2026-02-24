# API Route Analysis & Missing Endpoints

## Issue Summary
The `get_po` endpoint (GET /api/po) is not returning POs correctly, and several routes are missing or misconfigured compared to frontend expectations.

---

## 1. Purchase Orders (Client POs) - ISSUES & FIXES

### ✅ WORKING Routes
- `GET /api/po` - Returns all POs (but needs data wrapping fix)
- `GET /api/projects/{projectId}/po` - Returns project POs
- `POST /api/projects/{projectId}/po` - Create PO for project
- `PUT /api/po/{poId}` - Update PO
- `DELETE /api/po/{poId}` - Delete PO
- `POST /api/projects/{projectId}/po/{poId}/attach` - Attach PO to project
- `PUT /api/projects/{projectId}/po/{poId}/set-primary` - Set primary PO
- `GET /api/projects/{projectId}/po/enriched` - Get enriched POs with payment status

### ❌ MISSING or MISCONFIGURED Routes
1. **GET /api/po/{poId}** - MISSING
   - Frontend expects: Get individual PO details by ID
   - Currently: No dedicated endpoint (only /api/client-po/{client_po_id})
   - Need to add endpoint

2. **GET /api/po response format** - BROKEN
   - Current: Returns `{ "status": "SUCCESS", "pos": [...], "total_count": X, "total_value": Y }`
   - Frontend expects: `GetAllPOsResponse` with proper structure
   - Fix: Wrap data properly as `data` object

3. **Get Order Details** - MISSING
   - Route: `GET /api/po/{clientPoId}/details` or similar
   - Frontend expects: `OrderDetailsResponse`
   - Current: No such endpoint

---

## 2. Vendors & Vendor Orders - STATUS

### ✅ WORKING Routes
- `GET /api/vendors` - Query param: status ('active' | 'inactive')
- `GET /api/vendors/{vendorId}`
- `POST /api/vendors`
- `PUT /api/vendors/{vendorId}`
- `DELETE /api/vendors/{vendorId}`
- `GET /api/projects/{projectId}/vendor-orders`
- `POST /api/projects/{projectId}/vendor-orders`
- `POST /api/projects/{projectId}/vendor-orders/bulk`
- `PUT /api/vendor-orders/{vendorOrderId}/status`

### ❌ ISSUES
1. **Link Payment to Order** - MISSING
   - Route: `POST /api/vendor-orders/{vendorOrderId}/link-payment`
   - Body: `{ link_type: "incoming"|"outgoing", amount?: number, payment_id?: string }`

---

## 3. Billing POs - STATUS

### ✅ WORKING Routes
- `POST /api/projects/{projectId}/billing-po` - Create Billing PO
- `GET /api/billing-po/{billingPoId}` - Get Billing PO
- `PUT /api/billing-po/{billingPoId}` - Update Billing PO
- `GET /api/projects/{projectId}/billing-summary` - Get billing summary
- `POST /api/billing-po/{billingPoId}/line-items` - Add Line Item
- `GET /api/billing-po/{billingPoId}/line-items` - Get line items

### ❌ MISSING Routes
1. **POST /api/billing-po/{billingPoId}/approve** - MISSING
   - Body: `{ notes?: string }`
   - Frontend expects approval endpoint

2. **GET /api/projects/{projectId}/pl-analysis** or similar - MISSING
   - Frontend expects: `GetProjectProfitLossResponse`
   - Currently: Only `/api/projects/{projectId}/financial-summary` exists

---

## 4. Payments - STATUS

### ✅ WORKING Routes
- `GET /api/po/{poId}/payments`
- `POST /api/po/{poId}/payments`
- `PUT /api/payments/{paymentId}`
- `DELETE /api/payments/{paymentId}`

---

## 5. File Uploads & Sessions - STATUS

### ✅ WORKING Routes
- `POST /api/uploads/session` - Create Session
- `POST /api/uploads/session/{sessionId}` - Upload File
- `GET /api/uploads/session/{sessionId}/files` - List Files
- `GET /api/po/{poNumber}/files` - Get Files by PO
- `GET /api/po/{poNumber}/files/{fileId}/download` - Download File
- `POST /api/uploads/bajaj-po` - Upload Bajaj PO
- `POST /api/uploads/proforma` - Upload Proforma

---

## Critical Fixes Needed

### Priority 1: CRITICAL - Breaks Frontend
1. Add `GET /api/po/{poId}` endpoint that returns single PO with details
2. Fix response format for `GET /api/po` to wrap data properly
3. Add approval endpoint for billing POs: `POST /api/billing-po/{billingPoId}/approve`
4. Add P&L analysis endpoint: `GET /api/projects/{projectId}/pl-analysis`

### Priority 2: IMPORTANT - Missing Features
1. Add order details endpoint: `GET /api/po/{clientPoId}/details`
2. Add vendor order payment link endpoint: `POST /api/vendor-orders/{vendorOrderId}/link-payment`

### Priority 3: NICE-TO-HAVE - API Improvements
1. Add pagination to `GET /api/po`
2. Add filtering options
3. Add response validation

---

## Implementation Plan

### File: `/app/apis/po_management.py`
- Add new route: `GET /api/po/{poId}` - Get single PO details
- Modify: `GET /api/po` response format
- Add new route: `GET /api/po/{poId}/details` - Get order details

### File: `/app/apis/billing_po.py`
- Add new route: `POST /api/billing-po/{billingPoId}/approve` - Approve billing PO
- Add new route: `GET /api/projects/{projectId}/pl-analysis` - P&L analysis

### File: `/app/apis/vendor_orders.py`
- Add new route: `POST /api/vendor-orders/{vendorOrderId}/link-payment` - Link payment

### File: `/app/repository/po_management_repo.py`
- Add function: `get_po_by_id()` - Get single PO details
- Ensure proper data wrapping for responses

### File: `/app/repository/billing_po_repo.py`
- Add function: `approve_billing_po()` - Approve billing PO
- Add function: `get_project_pl_analysis()` - Get P&L analysis

