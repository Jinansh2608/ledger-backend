# Comprehensive PO Operations Integration Guide

## 📋 Overview

This document provides complete integration details for all Purchase Order (PO) operations in the system. The integration file `PO_API_INTEGRATION.ts` contains all request/response models, API endpoints, and helper functions for frontend development.

---

## 📁 File Structure

The integration is organized into 6 main namespaces:

1. **ClientPO** - Basic client PO retrieval
2. **BajajPO** - Bajaj Excel file upload and parsing
3. **DavaIndiaPO** - Dava India Excel file upload and parsing
4. **POManagement** - Core PO operations (CRUD, line items, projects, verbal agreements)
5. **BillingPO** - Billing-related PO operations
6. **VendorOrders** - Vendor order management

---

## 🚀 Quick Start

### Installation

```typescript
import { POAPIClient, ClientPO, BajajPO, DavaIndiaPO, POManagement, BillingPO, VendorOrders } from './PO_API_INTEGRATION';

// Create API client instance
const poClient = new POAPIClient('http://localhost:8000');

// Set authentication token if needed
poClient.setAuthToken('your-jwt-token');
```

---

## 📌 API Endpoints Reference

### **1. CLIENT PO OPERATIONS**

#### Get Client PO Details
```
GET /api/client-po/{client_po_id}
```

**Request:**
```typescript
const poId = 123;
const response = await ClientPO.getClientPO(poId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  po: {
    po_id: 123,
    po_number: "PO-2024-001",
    po_date: "2024-02-16",
    po_value: 50000,
    po_type: "standard",
    notes: "Standard purchase order"
  },
  line_items: [
    {
      item_name: "Item A",
      quantity: 10,
      unit_price: 5000,
      total: 50000
    }
  ],
  client_po_id: 123
}
```

---

### **2. BAJAJ PO UPLOAD & PARSING**

#### Upload Single Bajaj PO (Excel)
```
POST /api/bajaj-po
```

**Request:**
```typescript
const file = new File(['...'], 'po.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
const clientId = 1;
const projectId = 5;

const response = await BajajPO.uploadBajajPO(file, clientId, projectId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  client_po_id: 456,
  po: {
    po_number: "PO-BAJAJ-2024",
    po_date: "2024-02-16",
    po_value: 100000,
    store_id: "STORE-001",
    location: "Warehouse A"
  },
  summary: {
    total_items: 5,
    total_quantity: 100,
    total_value: 100000
  },
  line_items: [
    {
      item_name: "Product A",
      quantity: 50,
      rate: 1000,
      total: 50000
    },
    {
      item_name: "Product B",
      quantity: 50,
      rate: 1000,
      total: 50000
    }
  ],
  line_item_count: 2
}
```

#### Bulk Upload Bajaj POs
```
POST /api/bajaj-po/bulk
```

**Request:**
```typescript
const files = [
  new File(['...'], 'po1.xlsx'),
  new File(['...'], 'po2.xlsx'),
  new File(['...'], 'po3.xlsx')
];
const clientId = 1;
const projectId = 5;

const response = await BajajPO.bulkUploadBajajPO(files, clientId, projectId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  total_files: 3,
  successful: 3,
  failed: 0,
  uploaded_pos: [
    {
      client_po_id: 456,
      filename: "po1.xlsx",
      po_number: "PO-BAJAJ-001",
      po_value: 50000,
      store_id: "STORE-001",
      line_item_count: 2
    },
    // ... more POs
  ],
  errors: []
}
```

---

### **2B. DAVA INDIA PO UPLOAD & PARSING**

#### Upload Single Dava India PO (Excel)
```
POST /api/dava-india-po
```

**Request:**
```typescript
const file = new File(['...'], 'dava_po.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
const clientId = 1;
const projectId = 5;

const response = await DavaIndiaPO.uploadDavaIndiaPO(file, clientId, projectId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  client_po_id: 789,
  po: {
    po_number: "PO-DAVA-2024",
    po_date: "2024-02-16",
    po_value: 150000,
    location: "Warehouse B",
    warehouse: "WH-002",
    reference_no: "REF-001"
  },
  summary: {
    total_items: 8,
    total_quantity: 200,
    total_value: 150000
  },
  line_items: [
    {
      item_name: "Component X",
      quantity: 100,
      rate: 1500,
      total: 150000
    }
  ],
  line_item_count: 1
}
```

#### Bulk Upload Dava India POs
```
POST /api/dava-india-po/bulk
```

**Request:**
```typescript
const files = [
  new File(['...'], 'dava_po1.xlsx'),
  new File(['...'], 'dava_po2.xlsx')
];
const clientId = 1;
const projectId = 5;

const response = await DavaIndiaPO.bulkUploadDavaIndiaPO(files, clientId, projectId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  total_files: 2,
  successful: 2,
  failed: 0,
  uploaded_pos: [
    {
      client_po_id: 789,
      filename: "dava_po1.xlsx",
      po_number: "PO-DAVA-001",
      po_value: 75000,
      location: "Warehouse B",
      line_item_count: 3
    }
  ],
  errors: []
}
```

---

### **3. PO MANAGEMENT OPERATIONS**

#### Line Items

##### Add Line Item
```
POST /api/po/{client_po_id}/line-items
```

**Request:**
```typescript
const clientPoId = 123;
const lineItem: POManagement.LineItems.LineItemRequest = {
  item_name: "New Item",
  quantity: 20,
  unit_price: 1500
};

const response = await POManagement.LineItems.addLineItem(clientPoId, lineItem);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  message: "Line item added",
  line_item: {
    id: 789,
    item_name: "New Item",
    quantity: 20,
    unit_price: 1500,
    total_price: 30000
  }
}
```

##### Get Line Items
```
GET /api/po/{client_po_id}/line-items
```

**Request:**
```typescript
const clientPoId = 123;
const response = await POManagement.LineItems.getLineItems(clientPoId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  client_po_id: 123,
  line_items: [
    {
      id: 789,
      item_name: "Item A",
      quantity: 10,
      unit_price: 5000,
      total_price: 50000
    }
  ],
  line_item_count: 1,
  total_value: 50000
}
```

##### Update Line Item
```
PUT /api/line-items/{line_item_id}
```

**Request:**
```typescript
const lineItemId = 789;
const updates: POManagement.LineItems.LineItemUpdateRequest = {
  quantity: 25,
  unit_price: 1600
};

const response = await POManagement.LineItems.updateLineItem(lineItemId, updates);
```

##### Delete Line Item
```
DELETE /api/line-items/{line_item_id}
```

**Request:**
```typescript
const lineItemId = 789;
const response = await POManagement.LineItems.deleteLineItem(lineItemId);
```

---

#### Multiple POs Per Project

##### Create PO for Project
```
POST /api/projects/{project_id}/po?client_id={client_id}
```

**Request:**
```typescript
const projectId = 5;
const clientId = 1;
const po: POManagement.ProjectPOs.CreatePORequest = {
  po_number: "PO-2024-100",
  po_date: "2024-02-16",
  po_value: 75000,
  po_type: "standard",
  notes: "Purchase order for project"
};

const response = await POManagement.ProjectPOs.createPOForProject(projectId, clientId, po);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  message: "PO created",
  client_po_id: 600,
  po_number: "PO-2024-100",
  po_type: "standard"
}
```

##### Get All Project POs
```
GET /api/projects/{project_id}/po
```

**Request:**
```typescript
const projectId = 5;
const response = await POManagement.ProjectPOs.getProjectPOs(projectId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  project_id: 5,
  pos: [
    {
      client_po_id: 600,
      po_number: "PO-2024-100",
      po_date: "2024-02-16",
      po_value: 75000,
      po_type: "standard",
      location: "Warehouse A",
      is_primary: true
    }
  ],
  total_po_count: 1,
  total_project_value: 75000,
  primary_po: { /* primary PO details */ }
}
```

##### Attach PO to Project
```
POST /api/projects/{project_id}/po/{client_po_id}/attach
```

**Request:**
```typescript
const projectId = 5;
const clientPoId = 600;
const sequenceOrder = 1;

const response = await POManagement.ProjectPOs.attachPOToProject(
  projectId,
  clientPoId,
  sequenceOrder
);
```

##### Set Primary PO
```
PUT /api/projects/{project_id}/po/{client_po_id}/set-primary
```

**Request:**
```typescript
const projectId = 5;
const clientPoId = 600;

const response = await POManagement.ProjectPOs.setPrimaryPO(projectId, clientPoId);
```

---

#### Update PO
```
PUT /api/po/{client_po_id}
```

**Request:**
```typescript
const clientPoId = 600;
const updates: POManagement.UpdatePO.UpdatePORequest = {
  po_value: 80000,
  status: "updated",
  notes: "Updated PO value"
};

const response = await POManagement.UpdatePO.updatePO(clientPoId, updates);
```

---

#### Verbal Agreements

##### Create Verbal Agreement
```
POST /api/projects/{project_id}/verbal-agreement?client_id={client_id}
```

**Request:**
```typescript
const projectId = 5;
const clientId = 1;
const agreement: POManagement.VerbalAgreements.VerbalAgreementRequest = {
  pi_number: "PI-2024-001",
  pi_date: "2024-02-16",
  value: 50000,
  notes: "Verbal agreement discussion"
};

const response = await POManagement.VerbalAgreements.createVerbalAgreement(
  projectId,
  clientId,
  agreement
);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  message: "Verbal agreement created",
  agreement_id: 10,
  pi_number: "PI-2024-001",
  pi_date: "2024-02-16"
}
```

##### Add PO to Verbal Agreement
```
PUT /api/verbal-agreement/{agreement_id}/add-po
```

**Request:**
```typescript
const agreementId = 10;
const poData: POManagement.VerbalAgreements.AddPOToVerbalAgreementRequest = {
  po_number: "PO-2024-100",
  po_date: "2024-02-16"
};

const response = await POManagement.VerbalAgreements.addPOToVerbalAgreement(
  agreementId,
  poData
);
```

##### Get Verbal Agreements
```
GET /api/projects/{project_id}/verbal-agreements
```

**Request:**
```typescript
const projectId = 5;
const response = await POManagement.VerbalAgreements.getVerbalAgreements(projectId);
```

---

#### Projects

##### Create Project
```
POST /api/projects
```

**Request:**
```typescript
const project: POManagement.Projects.CreateProjectRequest = {
  name: "New Construction Project",
  location: "Bangalore",
  city: "Bangalore",
  state: "Karnataka",
  country: "India",
  latitude: 12.9716,
  longitude: 77.5946
};

const response = await POManagement.Projects.createProject(project);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  message: "Project 'New Construction Project' created",
  project_id: 5,
  name: "New Construction Project"
}
```

##### Delete Project
```
DELETE /api/projects?name={project_name}
```

**Request:**
```typescript
const projectName = "Old Project";
const response = await POManagement.Projects.deleteProject(projectName);
```

---

#### Financial Summary

##### Get Financial Summary
```
GET /api/projects/{project_id}/financial-summary
```

**Request:**
```typescript
const projectId = 5;
const response = await POManagement.FinancialSummary.getFinancialSummary(projectId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  project_id: 5,
  financial_summary: {
    total_po_value: 100000,
    total_agreement_value: 50000,
    total_project_value: 150000,
    documents: 2,
    verbal_agreements: 1,
    total_collected: 120000,
    outstanding_amount: 30000,
    net_profit: 90000,
    profit_margin_percentage: 60,
    active_orders: 2,
    vendor_count: 3,
    client_count: 1
  },
  purchase_orders: {
    count: 2,
    total_value: 100000,
    orders: [
      {
        client_po_id: 600,
        po_number: "PO-2024-100",
        po_value: 50000,
        po_date: "2024-02-16",
        location: "Warehouse A"
      },
      {
        client_po_id: 601,
        po_number: "PO-2024-101",
        po_value: 50000,
        po_date: "2024-02-17",
        location: "Warehouse B"
      }
    ]
  },
  verbal_agreements: {
    count: 1,
    total_value: 50000,
    agreements: [ /* Agreement details */ ]
  }
}
```

##### Get Enriched POs (with Payment Data)
```
GET /api/projects/{project_id}/po/enriched
```

**Request:**
```typescript
const projectId = 5;
const response = await POManagement.EnrichedPOs.getEnrichedPOs(projectId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  project_id: 5,
  pos: [
    {
      client_po_id: 600,
      po_number: "PO-2024-100",
      po_value: 75000,
      total_paid: 60000,
      receivable_amount: 15000,
      payment_status: "partial",
      total_tds: 5000,
      location: "Warehouse A",
      payment_details: [ /* payment records */ ],
      payment_count: 3
    }
  ],
  total_po_count: 1,
  total_project_value: 75000,
  total_paid: 60000,
  total_receivable: 15000,
  summary: {
    paid_count: 0,
    partial_count: 1,
    pending_count: 0
  }
}
```

---

### **4. BILLING PO OPERATIONS**

#### Create Billing PO
```
POST /api/projects/{project_id}/billing-po
```

**Request:**
```typescript
const projectId = 5;
const request: BillingPO.CreateBillingPORequest = {
  client_po_id: 600,
  billed_value: 70000,
  billed_gst: 12600, // 18% GST
  billing_notes: "Invoice for project services"
};

const response = await BillingPO.createBillingPO(projectId, request);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  message: "Billing PO created",
  billing_po: {
    billing_po_id: "BILLING-001",
    po_number: "PO-2024-100",
    client_po_id: 600,
    project_id: 5,
    billed_value: 70000,
    billed_gst: 12600,
    billing_notes: "Invoice for project services"
  }
}
```

#### Add Billing Line Item
```
POST /api/billing-po/{billing_po_id}/line-items
```

**Request:**
```typescript
const billingPoId = "BILLING-001";
const item: BillingPO.BillingLineItemRequest = {
  description: "Service charges",
  qty: 10,
  rate: 7000
};

const response = await BillingPO.addBillingLineItem(billingPoId, item);
```

#### Get Billing Line Items
```
GET /api/billing-po/{billing_po_id}/line-items
```

**Request:**
```typescript
const billingPoId = "BILLING-001";
const response = await BillingPO.getBillingLineItems(billingPoId);
```

**Response:**
```typescript
{
  status: "SUCCESS",
  billing_po_id: "BILLING-001",
  line_item_count: 2,
  total_value: 140000,
  line_items: [
    {
      description: "Service charges",
      qty: 10,
      rate: 7000,
      total: 70000
    },
    {
      description: "Material supply",
      qty: 5,
      rate: 14000,
      total: 70000
    }
  ]
}
```

#### Update Billing PO
```
PUT /api/billing-po/{billing_po_id}
```

**Request:**
```typescript
const billingPoId = "BILLING-001";
const request: BillingPO.UpdateBillingPORequest = {
  billed_value: 75000,
  billed_gst: 13500
};

const response = await BillingPO.updateBillingPO(billingPoId, request);
```

#### Delete Billing Line Item
```
DELETE /api/billing-po/{billing_po_id}/line-items/{line_item_id}
```

#### Get Billing Summary
```
GET /api/projects/{project_id}/billing-summary
```

#### Get Profit & Loss Analysis
```
GET /api/projects/{project_id}/billing-pl-analysis
```

**Response:**
```typescript
{
  status: "SUCCESS",
  project_id: 5,
  analysis: {
    baseline: { po_value: 75000 },
    billing: { billed_value: 70000 },
    variance: {
      delta: -5000,
      delta_percent: -6.67,
      direction: "down"
    },
    costs: { vendor_costs: 45000 },
    profit_loss: {
      amount: 25000,
      margin_percent: 35.71,
      status: "profit"
    },
    totals: {
      revenue: 70000,
      costs: 45000,
      profit: 25000
    }
  }
}
```

---

### **5. VENDOR ORDERS OPERATIONS**

#### Create Vendor Order
```
POST /api/projects/{project_id}/vendor-orders
```

**Request:**
```typescript
const projectId = 5;
const order: VendorOrders.VendorOrderRequest = {
  vendor_id: 2,
  po_number: "VO-2024-001",
  po_date: "2024-02-16",
  po_value: 50000,
  due_date: "2024-03-16",
  description: "Vendor purchase order"
};

const response = await VendorOrders.createVendorOrder(projectId, order);
```

#### Bulk Create Vendor Orders
```
POST /api/projects/{project_id}/vendor-orders/bulk
```

**Request:**
```typescript
const projectId = 5;
const request: VendorOrders.BulkCreateVendorOrdersRequest = {
  orders: [
    {
      vendor_id: 2,
      po_number: "VO-2024-001",
      po_date: "2024-02-16",
      po_value: 50000
    },
    {
      vendor_id: 3,
      po_number: "VO-2024-002",
      po_date: "2024-02-16",
      po_value: 30000
    }
  ]
};

const response = await VendorOrders.bulkCreateVendorOrders(projectId, request);
```

#### Get Project Vendor Orders
```
GET /api/projects/{project_id}/vendor-orders
```

#### Update Vendor Order
```
PUT /api/vendor-orders/{vendor_order_id}
```

#### Update Vendor Order Status
```
PUT /api/vendor-orders/{vendor_order_id}/status
```

**Request:**
```typescript
const vendorOrderId = 1;
const status: VendorOrders.VendorOrderStatusRequest = {
  work_status: "completed",
  payment_status: "partial"
};

const response = await VendorOrders.updateVendorOrderStatus(vendorOrderId, status);
```

#### Add Vendor Order Line Item
```
POST /api/vendor-orders/{vendor_order_id}/line-items
```

#### Get Vendor Order Line Items
```
GET /api/vendor-orders/{vendor_order_id}/line-items
```

#### Delete Vendor Order
```
DELETE /api/vendor-orders/{vendor_order_id}
```

---

## 🔧 Using the POAPIClient

The `POAPIClient` class provides a convenient wrapper for all operations:

```typescript
import { POAPIClient } from './PO_API_INTEGRATION';

// Create client
const client = new POAPIClient('http://localhost:8000');

// Set authentication
client.setAuthToken('your-jwt-token');

// Use methods
const poData = await client.getClientPO(123);
const projects = await client.getAllPOs(1);
const uploadResult = await client.uploadBajajPO(file, 1, 5);
const davaUploadResult = await client.uploadDavaIndiaPO(file, 1, 5);

// Create project
const newProject = await client.createProject({
  name: "New Project",
  city: "Bangalore"
});

// Financial summary with location data
const summary = await client.getFinancialSummary(5);
console.log(summary.purchase_orders.orders.forEach(po => {
  console.log(`${po.po_number} - Location: ${po.location}`);
}));
```

---

## 📊 Common Workflows

### Workflow 1: Create Project with PO and Billing

```typescript
async function createProjectWithPOAndBilling() {
  const client = new POAPIClient();
  
  // 1. Create project
  const project = await client.createProject({
    name: "Construction Project 2024",
    city: "Bangalore"
  });
  const projectId = project.project_id;
  
  // 2. Create PO for project
  const po = await client.createPOForProject(projectId, 1, {
    po_number: "PO-2024-500",
    po_date: "2024-02-16",
    po_value: 100000
  });
  const clientPoId = po.client_po_id;
  
  // 3. Add line items to PO
  await client.addLineItem(clientPoId, {
    item_name: "Material A",
    quantity: 50,
    unit_price: 2000
  });
  
  // 4. Create billing PO
  const billingPO = await client.createBillingPO(projectId, {
    client_po_id: clientPoId,
    billed_value: 95000,
    billed_gst: 17100
  });
  
  return { projectId, clientPoId, billingPoId: billingPO.billing_po.billing_po_id };
}
```

### Workflow 2: Upload Bajaj POs and Attach to Project

```typescript
async function uploadAndAttachBajajPOs() {
  const client = new POAPIClient();
  const projectId = 5;
  const clientId = 1;
  
  // 1. Upload Excel files
  const uploadResult = await client.uploadBajajPO(
    new File([...], 'po.xlsx'),
    clientId,
    projectId
  );
  
  const clientPoId = uploadResult.client_po_id;
  
  // 2. Set as primary PO
  await client.setPrimaryPO(projectId, clientPoId);
  
  // 3. Get enriched POs for payment tracking
  const enrichedPOs = await client.getEnrichedPOs(projectId);
  
  return enrichedPOs;
}
```

### Workflow 2B: Upload Dava India POs and Attach to Project

```typescript
async function uploadAndAttachDavaIndiaPOs() {
  const client = new POAPIClient();
  const projectId = 5;
  const clientId = 1;
  
  // 1. Upload Excel files
  const uploadResult = await client.uploadDavaIndiaPO(
    new File([...], 'dava_po.xlsx'),
    clientId,
    projectId
  );
  
  const clientPoId = uploadResult.client_po_id;
  
  // 2. Set as primary PO
  await client.setPrimaryPO(projectId, clientPoId);
  
  // 3. Get project POs with location information
  const projectPOs = await client.getProjectPOs(projectId);
  projectPOs.pos.forEach(po => {
    console.log(`PO: ${po.po_number}, Location: ${po.location}`);
  });
  
  // 4. Get enriched POs for payment tracking
  const enrichedPOs = await client.getEnrichedPOs(projectId);
  
  return enrichedPOs;
}
```

### Workflow 3: Get Complete Project Financial Status

```typescript
async function getProjectFinancialStatus(projectId: number) {
  const client = new POAPIClient();
  
  // Get all required data
  const [financial, billing, profitLoss, enrichedPOs] = await Promise.all([
    client.getFinancialSummary(projectId),
    client.getProjectBillingSummary(projectId),
    client.getProjectProfitLoss(projectId),
    client.getEnrichedPOs(projectId)
  ]);
  
  return {
    financial,
    billing,
    profitLoss,
    enrichedPOs
  };
}
```

---

## 🛡️ Error Handling

All API calls return either successful responses or throw errors. Handle them properly:

```typescript
try {
  const response = await client.createProject({
    name: "New Project"
  });
  console.log("Success:", response);
} catch (error) {
  if (error instanceof Error) {
    console.error("Error:", error.message);
  }
}
```

---

## 📝 Response Status Codes

| Status | Meaning |
|--------|---------|
| `SUCCESS` | Operation completed successfully |
| `FAILED` | Operation failed (validation error) |
| `ERROR` | Server error occurred |

---

## 🔐 Authentication

Include authorization header in requests:

```typescript
const client = new POAPIClient();
client.setAuthToken('Bearer eyJhbGciOiJIUzI1NiIs...');
```

---

## ✅ Type Safety

All requests and responses are fully typed in TypeScript:

```typescript
const request: POManagement.ProjectPOs.CreatePORequest = {
  po_number: "PO-123",
  po_date: "2024-02-16",
  po_value: 50000
};

const response: POManagement.ProjectPOs.CreatePOResponse = 
  await client.createPOForProject(projectId, clientId, request);

// TypeScript will catch type errors at compile time
```

---

## 📞 Support

For issues or questions regarding the integration:
- Check API response messages for detailed information
- Ensure all required parameters are provided
- Verify API endpoint URLs match your backend configuration
