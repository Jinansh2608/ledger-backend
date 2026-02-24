# Frontend Vendor Order Integration Guide

## ✅ Backend Status: READY
Vendor Order API is fully functional with complete CRUD operations and payment linking.

---

## 📋 Available API Endpoints

### 1. Create Single Vendor Order
```
POST /api/projects/{project_id}/vendor-orders
Content-Type: application/json

{
  "vendor_id": 1,
  "po_number": "VO-2026-001",
  "po_date": "2026-02-17",
  "po_value": 50000.0,
  "due_date": "2026-03-17",
  "description": "Supply for Project A"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Vendor order created",
  "vendor_order": {
    "id": 10,
    "vendor_id": 1,
    "project_id": 1,
    "po_number": "VO-2026-001",
    "po_date": "2026-02-17",
    "amount": 50000.0,
    "due_date": "2026-03-17",
    "description": "Supply for Project A",
    "work_status": "pending",
    "payment_status": "unpaid",
    "created_at": "2026-02-18T10:30:00",
    "updated_at": null
  }
}
```

---

### 2. Bulk Create Vendor Orders
```
POST /api/projects/{project_id}/vendor-orders/bulk
Content-Type: application/json

{
  "orders": [
    {
      "vendor_id": 1,
      "po_number": "VO-2026-001",
      "po_date": "2026-02-17",
      "po_value": 50000.0,
      "due_date": "2026-03-17"
    },
    {
      "vendor_id": 2,
      "po_number": "VO-2026-002",
      "po_date": "2026-02-17",
      "po_value": 30000.0,
      "due_date": "2026-03-17"
    }
  ]
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Created 2 vendor orders",
  "vendor_orders": [...],
  "count": 2
}
```

---

### 3. Get Project Vendor Orders
```
GET /api/projects/{project_id}/vendor-orders
```

**Response:**
```json
{
  "status": "SUCCESS",
  "vendor_order_count": 5,
  "vendor_orders": [
    {
      "id": 10,
      "vendor_id": 1,
      "vendor_name": "ABC Supplier",
      "project_id": 1,
      "po_number": "VO-2026-001",
      "po_date": "2026-02-17",
      "amount": 50000.0,
      "due_date": "2026-03-17",
      "work_status": "in_progress",
      "payment_status": "partially_paid",
      "line_item_count": 3,
      "created_at": "2026-02-18T10:30:00"
    }
  ]
}
```

---

### 4. Get Vendor Order Details
```
GET /api/vendor-orders/{vendor_order_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "vendor_order": {
    "id": 10,
    "vendor_id": 1,
    "vendor_name": "ABC Supplier",
    "project_id": 1,
    "po_number": "VO-2026-001",
    "po_date": "2026-02-17",
    "amount": 50000.0,
    "due_date": "2026-03-17",
    "description": "Supply for Project A",
    "work_status": "in_progress",
    "payment_status": "partially_paid",
    "total_line_items": 3,
    "line_items": [...],
    "created_at": "2026-02-18T10:30:00",
    "updated_at": "2026-02-18T14:00:00"
  }
}
```

---

### 5. Update Vendor Order
```
PUT /api/projects/{project_id}/vendor-orders/{vendor_order_id}
Content-Type: application/json

{
  "po_value": 55000.0,
  "due_date": "2026-03-20",
  "description": "Updated description",
  "work_status": "in_progress",
  "payment_status": "partially_paid"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Vendor order updated",
  "vendor_order": {...}
}
```

---

### 6. Update Vendor Order Status
```
PUT /api/vendor-orders/{vendor_order_id}/status
Content-Type: application/json

{
  "work_status": "completed",
  "payment_status": "paid"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Vendor order status updated",
  "vendor_order": {...}
}
```

---

### 7. Delete Vendor Order
```
DELETE /api/projects/{project_id}/vendor-orders/{vendor_order_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Vendor order deleted"
}
```

---

### 8. Add Line Item to Vendor Order
```
POST /api/vendor-orders/{vendor_order_id}/line-items
Content-Type: application/json

{
  "item_name": "Material ABC",
  "quantity": 100,
  "unit_price": 500.0
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Line item added",
  "line_item": {
    "id": 45,
    "vendor_order_id": 10,
    "item_name": "Material ABC",
    "quantity": 100,
    "unit_price": 500.0,
    "total_amount": 50000.0,
    "created_at": "2026-02-18T10:30:00"
  }
}
```

---

### 9. Get Vendor Order Line Items
```
GET /api/vendor-orders/{vendor_order_id}/line-items
```

**Response:**
```json
{
  "status": "SUCCESS",
  "vendor_order_id": 10,
  "line_item_count": 3,
  "line_items": [
    {
      "id": 45,
      "vendor_order_id": 10,
      "item_name": "Material ABC",
      "quantity": 100,
      "unit_price": 500.0,
      "total_amount": 50000.0,
      "created_at": "2026-02-18T10:30:00"
    }
  ]
}
```

---

### 10. Update Line Item
```
PUT /api/vendor-line-items/{item_id}
Content-Type: application/json

{
  "quantity": 120,
  "unit_price": 450.0
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Line item updated",
  "line_item": {...}
}
```

---

### 11. Delete Line Item
```
DELETE /api/vendor-line-items/{item_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Line item deleted"
}
```

---

### 12. Link Payment to Vendor Order
```
POST /api/vendor-orders/{vendor_order_id}/link-payment
Content-Type: application/json

{
  "link_type": "incoming",
  "amount": 25000.0,
  "payment_id": "PAY-123456"
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Payment linked to vendor order",
  "linked_payment": {...}
}
```

---

### 13. Get Vendor Order Payment Summary
```
GET /api/vendor-orders/{vendor_order_id}/payment-summary
```

**Response:**
```json
{
  "status": "SUCCESS",
  "vendor_order_id": 10,
  "po_amount": 50000.0,
  "paid_amount": 25000.0,
  "pending_amount": 25000.0,
  "payment_status": "partially_paid",
  "payment_count": 2,
  "payments": [...]
}
```

---

### 14. Get Profit Analysis
```
GET /api/vendor-orders/{vendor_order_id}/profit-analysis
```

**Response:**
```json
{
  "status": "SUCCESS",
  "vendor_order_id": 10,
  "po_amount": 50000.0,
  "billable_amount": 60000.0,
  "profit": 10000.0,
  "profit_margin": 20.0,
  "linked_client_pos": [106, 108]
}
```

---

## 🎯 Frontend Implementation Checklist

### For Project Management Page:
- [ ] Display list of vendor orders for project
- [ ] Call: GET /api/projects/{project_id}/vendor-orders
- [ ] Show vendor order columns: PO #, Vendor, Amount, Due Date, Status
- [ ] Add "Create Vendor Order" button
- [ ] Add "Edit" and "Delete" buttons per order
- [ ] Click to view full order details

### For Vendor Order Details Page:
- [ ] Display vendor order info (from GET /api/vendor-orders/{vendor_order_id})
- [ ] Show line items section
- [ ] Display payment summary
- [ ] Add "Edit Order" button
- [ ] Add "Add Line Item" button
- [ ] Add "Update Status" button
- [ ] Show profit analysis if available

### For Vendor Order Creation Form:
- [ ] Form fields:
  - [ ] Vendor (select dropdown)
  - [ ] PO Number (text input)
  - [ ] PO Date (date picker)
  - [ ] PO Value (number input)
  - [ ] Due Date (date picker)
  - [ ] Description (textarea)
- [ ] Validation: vendor_id, po_number, po_date required
- [ ] Submit button calls: POST /api/projects/{project_id}/vendor-orders
- [ ] On success, redirect to vendor order details page

### For Line Items Management:
- [ ] Display table of line items
- [ ] Add "Add Line Item" button
- [ ] For each line item:
  - [ ] Show item name, quantity, unit price, total
  - [ ] Add "Edit" button (calls PUT /api/vendor-line-items/{item_id})
  - [ ] Add "Delete" button (calls DELETE /api/vendor-line-items/{item_id})
- [ ] Calculate and display line item total automatically

### For Payment Linking:
- [ ] Display "Link Payment" section
- [ ] Show linked payments with amounts
- [ ] Add "Link Payment" button
- [ ] Modal to select payment and amount
- [ ] Shows total linked vs. order amount

### For Bulk Operations:
- [ ] Add "Bulk Create" button in project
- [ ] Modal to upload/paste multiple orders
- [ ] Call: POST /api/projects/{project_id}/vendor-orders/bulk
- [ ] Show results with success/failure counts

---

## 📊 Vendor Order Fields Reference

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `id` | int | 10 | Order ID (read-only) |
| `vendor_id` | int | 1 | Link to vendor |
| `vendor_name` | string | "ABC Supplier" | Vendor display name |
| `project_id` | int | 1 | Link to project |
| `po_number` | string | "VO-2026-001" | Unique PO number |
| `po_date` | string | "2026-02-17" | ISO date |
| `amount` / `po_value` | float | 50000.0 | Order total |
| `due_date` | string | "2026-03-17" | ISO date (optional) |
| `description` | string | "Supply..." | Order description |
| `work_status` | string | "in_progress" | pending/in_progress/completed |
| `payment_status` | string | "partially_paid" | unpaid/partially_paid/paid |
| `line_item_count` / `total_line_items` | int | 3 | Number of line items |
| `created_at` | string | "2026-02-18T10:30:00" | ISO datetime (read-only) |
| `updated_at` | string | "2026-02-18T14:00:00" | ISO datetime |

---

## 📊 Line Item Fields Reference

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `id` | int | 45 | Line item ID (read-only) |
| `vendor_order_id` | int | 10 | Parent order ID |
| `item_name` | string | "Material ABC" | Item description |
| `quantity` | float | 100 | Quantity ordered |
| `unit_price` | float | 500.0 | Price per unit |
| `total_amount` | float | 50000.0 | quantity × unit_price (read-only) |
| `created_at` | string | "2026-02-18T10:30:00" | ISO datetime (read-only) |

---

## 💡 Implementation Tips

### Status Badge Styling
```javascript
const workStatusColors = {
  'pending': 'gray',
  'in_progress': 'blue',
  'completed': 'green'
};

const paymentStatusColors = {
  'unpaid': 'red',
  'partially_paid': 'yellow',
  'paid': 'green'
};
```

### Calculate Order Total from Line Items
```javascript
const orderTotal = lineItems.reduce((sum, item) => {
  return sum + (item.quantity * item.unit_price);
}, 0);
```

### Format Currency Display
```javascript
const formatted = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR'
}).format(vendorOrder.amount);
```

### Calculate Days Until Due
```javascript
const daysUntilDue = Math.ceil(
  (new Date(vendorOrder.due_date) - new Date()) / (1000 * 60 * 60 * 24)
);
```

### Auto-calculate Line Item Total
```javascript
const lineItemTotal = quantity * unitPrice;
// Update on quantity or price change
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Vendor order not created | Check vendor_id exists, po_number is unique |
| Line items not showing | Verify GET /api/vendor-orders/{id}/line-items called |
| Payment linking fails | Ensure payment_id is valid |
| Status update not working | Use PUT /api/vendor-orders/{id}/status endpoint |
| Bulk create fails partially | Check each order has required fields |
| Profit analysis showing 0 | Ensure order is linked to client POs |
| Due date not displaying | Check if due_date was provided (optional field) |

---

## ✅ Test Data Available
- **Sample vendors:** Available via GET /api/vendors
- **Sample projects:** Use any active project ID
- **Test vendor order:** Create one to test workflows

---

## 📝 Common Workflows

### Workflow 1: Create and Link Vendor Order
```
1. GET /api/vendors (to select vendor)
2. POST /api/projects/{project_id}/vendor-orders (create order)
3. POST /api/vendor-orders/{vendor_order_id}/line-items (add items)
4. PUT /api/vendor-orders/{vendor_order_id}/status (update status)
5. POST /api/vendor-orders/{vendor_order_id}/link-payment (link payment)
```

### Workflow 2: View Vendor Order Summary
```
1. GET /api/projects/{project_id}/vendor-orders (get all orders)
2. GET /api/vendor-orders/{vendor_order_id} (get details)
3. GET /api/vendor-orders/{vendor_order_id}/line-items (get items)
4. GET /api/vendor-orders/{vendor_order_id}/payment-summary (get payments)
5. GET /api/vendor-orders/{vendor_order_id}/profit-analysis (profit info)
```

### Workflow 3: Update Vendor Order
```
1. GET /api/vendor-orders/{vendor_order_id} (fetch current)
2. PUT /api/projects/{project_id}/vendor-orders/{vendor_order_id} (update fields)
3. PUT /api/vendor-line-items/{item_id} (update line items)
4. PUT /api/vendor-orders/{vendor_order_id}/status (update status)
```

---

## Next Steps
1. List vendor orders in project details page
2. Implement vendor order creation form
3. Implement vendor order details view
4. Add line item management
5. Add payment linking feature
6. Add status update functionality
7. Test with sample data
