# Nexgen ERP Finance API - Complete Frontend Integration Guide

**Version**: 1.0.0 | **Status**: ✅ Production Ready | **Date**: February 2026

---

## Table of Contents

1. [Setup & Configuration](#setup--configuration)
2. [API Base Structure](#api-base-structure)
3. [Supported Clients](#supported-clients)
4. [Authentication](#authentication)
5. [Health & Status](#health--status)
6. [File Upload System](#file-upload-system)
7. [Purchase Orders (PO Management)](#purchase-orders-po-management)
8. [Line Items](#line-items)
9. [Vendors](#vendors)
10. [Vendor Orders](#vendor-orders)
11. [Payments](#payments)
12. [Projects](#projects)
13. [Billing POs](#billing-pos)
14. [Documents](#documents)
15. [Error Handling](#error-handling)
16. [TypeScript/JavaScript Examples](#typescriptjavascript-examples)
17. [State Management Patterns](#state-management-patterns)
18. [Troubleshooting](#troubleshooting)

---

## Setup & Configuration

### Environment Variables (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
VITE_FILE_UPLOAD_MAX_SIZE=52428800  # 50MB in bytes
VITE_POLLING_INTERVAL=5000
```

### Frontend Configuration

```typescript
// config/api.ts
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  UPLOAD: {
    MAX_SIZE: parseInt(import.meta.env.VITE_FILE_UPLOAD_MAX_SIZE || '52428800'),
    ALLOWED_TYPES: ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']
  }
}

export const ENDPOINTS = {
  HEALTH: '/health',
  // Will expand below...
}
```

---

## API Base Structure

### Response Format (Standard)

All API responses follow this format:

```typescript
interface StandardResponse<T> {
  status: "SUCCESS" | "ERROR"
  message?: string
  data?: T
  timestamp?: string
  error_code?: string
  path?: string
  errors?: Array<{ field: string; message: string; type: string }>
}
```

### Supported Clients

The system supports **multiple PO formats** from different clients:

| Client ID | Client Name | Parser Module | Parser Function | Document Type |
|-----------|-------------|---------------|-----------------|----------------|
| 1 | **Bajaj** | `bajaj_po_parser.py` | `parse_bajaj_po()` | Purchase Order (Excel/CSV) |
| 2 | **Dava India** | `proforma_invoice_parser.py` | `parse_proforma_invoice()` | Proforma Invoice (PO Format) |

When uploading files, specify the `client_id` to automatically use the correct parser.

```typescript
// Get supported clients
async function getSupportedClients() {
  const response = await fetch(`${API_CONFIG.BASE_URL}/clients`)
  const data = await response.json()
  
  return data.data.clients
  // [
  //   { id: 1, name: "Bajaj" },
  //   { id: 2, name: "Dava India" }
  // ]
}
```

### Error Response Format

```typescript
interface ErrorResponse {
  status: "ERROR"
  error_code: string  // e.g., "VALIDATION_ERROR", "NOT_FOUND", "UNAUTHORIZED"
  message: string
  path: string
  errors?: Array<{
    field: string
    message: string
    type: string
  }>
}
```

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response data |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Fix validation errors |
| 401 | Unauthorized | Login required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Fix form data |
| 500 | Server Error | Retry or contact support |

---

## Authentication

### Current Status
Simple username/password authentication. Currently running without authentication required.

### Setup - Simple Auth Service

```typescript
// services/auth.ts
export class AuthService {
  private static USERNAME_KEY = 'app_username'
  private static PASSWORD_KEY = 'app_password'
  
  static getCredentials(): { username: string | null; password: string | null } {
    return {
      username: localStorage.getItem(this.USERNAME_KEY),
      password: localStorage.getItem(this.PASSWORD_KEY)
    }
  }
  
  static setCredentials(username: string, password: string): void {
    localStorage.setItem(this.USERNAME_KEY, username)
    localStorage.setItem(this.PASSWORD_KEY, password)
  }
  
  static clearCredentials(): void {
    localStorage.removeItem(this.USERNAME_KEY)
    localStorage.removeItem(this.PASSWORD_KEY)
  }
  
  static async login(username: string, password: string): Promise<{ success: boolean; message: string }> {
    // Store credentials locally (backend validates on each request)
    this.setCredentials(username, password)
    
    // Optional: Verify credentials by making a test API call
    try {
      await fetch(`${API_CONFIG.BASE_URL}/health`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })
      
      return { success: true, message: 'Login successful' }
    } catch (error) {
      this.clearCredentials()
      throw new Error('Login failed')
    }
  }
  
  static logout(): void {
    this.clearCredentials()
  }
  
  static getAuthHeaders(): HeadersInit {
    const { username, password } = this.getCredentials()
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    }
    
    if (username && password) {
      // Basic auth: encode credentials in Base64
      const credentials = btoa(`${username}:${password}`)
      headers['Authorization'] = `Basic ${credentials}`
    }
    
    return headers
  }
}

// API request helper with auth
export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<StandardResponse<T>> {
  const headers: HeadersInit = {
    ...AuthService.getAuthHeaders(),
    ...(options?.headers || {})
  }
  
  const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
    ...options,
    headers,
    signal: AbortSignal.timeout(API_CONFIG.TIMEOUT)
  })
  
  if (!response.ok) {
    if (response.status === 401) {
      AuthService.logout()
      // Redirect to login
      window.location.href = '/login'
    }
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }
  
  return response.json()
}
```

---

## Health & Status

### Check API Health

```typescript
// GET /api/health
async function checkHealth() {
  const response = await fetch(`${API_CONFIG.BASE_URL}/health`)
  const data: StandardResponse<HealthStatus> = await response.json()
  
  return data.data  // { status: "UP", service: "...", database: "UP", version: "1.0.0", timestamp: "..." }
}

interface HealthStatus {
  status: 'UP' | 'DOWN' | 'DEGRADED'
  service: string
  database: 'UP' | 'DOWN'
  version: string
  timestamp: string
}
```

### Get Detailed Health Metrics

```typescript
// GET /api/health/detailed
async function getDetailedHealth() {
  const response = await fetch(`${API_CONFIG.BASE_URL}/health/detailed`)
  const data = await response.json()
  
  console.log(data)
  // {
  //   status: "UP",
  //   timestamp: "2026-02-17T...",
  //   service: "Nexgen ERP - Finance API",
  //   version: "1.0.0",
  //   environment: "production",
  //   components: { api: "UP", database: "UP" },
  //   database_tables: 18
  // }
}
```

---

## File Upload System

### 1. Create Upload Session

```typescript
// POST /api/uploads/session
interface CreateSessionRequest {
  po_number?: string
  created_by?: string
  description?: string
}

async function createSession(request?: CreateSessionRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/uploads/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request || {})
  })
  
  const data: StandardResponse<SessionResponse> = await response.json()
  
  return data.data  // { session_id: "uuid", po_number: null, status: "active", created_at: "..." }
}

interface SessionResponse {
  session_id: string
  po_number?: string
  status: 'active' | 'processing' | 'completed' | 'failed'
  created_at: string
  file_count: number
}
```

### 2. Upload File to Session

```typescript
// POST /api/uploads/session/{session_id}/files
async function uploadFile(
  sessionId: string,
  file: File,
  options?: { uploaded_by?: string; po_number?: string }
) {
  const formData = new FormData()
  formData.append('file', file)
  
  if (options?.uploaded_by) {
    formData.append('uploaded_by', options.uploaded_by)
  }
  if (options?.po_number) {
    formData.append('po_number', options.po_number)
  }
  
  const response = await fetch(
    `${API_CONFIG.BASE_URL}/uploads/session/${sessionId}/files`,
    {
      method: 'POST',
      body: formData  // Don't set Content-Type header for multipart/form-data
    }
  )
  
  const data: StandardResponse<FileUploadResponse> = await response.json()
  
  return data.data
  // {
  //   file_id: "uuid",
  //   original_filename: "BAJAJ PO.xlsx",
  //   size: 25000,
  //   mime_type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  //   upload_timestamp: "2026-02-17T...",
  //   status: "success",
  //   parsing_status: "completed",
  //   parsed_data: { ... }
  // }
}

interface FileUploadResponse {
  file_id: string
  original_filename: string
  size: number
  mime_type: string
  upload_timestamp: string
  status: 'success' | 'failed'
  parsing_status?: 'pending' | 'processing' | 'completed' | 'failed'
  parsed_data?: any
  error?: string
}
```

### 3. Get Session Details

```typescript
// GET /api/uploads/session/{session_id}
async function getSessionDetails(sessionId: string) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/uploads/session/${sessionId}`)
  const data: StandardResponse<SessionDetailsResponse> = await response.json()
  
  return data.data
}

interface SessionDetailsResponse {
  session_id: string
  po_number?: string
  status: string
  created_at: string
  file_count: number
  files: Array<{
    file_id: string
    filename: string
    size: number
    upload_timestamp: string
  }>
}
```

### 4. List Files in Session

```typescript
// GET /api/uploads/session/{session_id}/files?skip=0&limit=50
async function listSessionFiles(sessionId: string, skip: number = 0, limit: number = 50) {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
  const response = await fetch(`${API_CONFIG.BASE_URL}/uploads/session/${sessionId}/files?${params}`)
  const data: StandardResponse<ListFilesResponse> = await response.json()
  
  return data.data
}

interface ListFilesResponse {
  session_id: string
  files: Array<{
    file_id: string
    filename: string
    size: number
    mime_type: string
    upload_timestamp: string
    parsing_status?: string
  }>
  total_count: number
  skip: number
  limit: number
}
```

### 5. Download File

```typescript
// GET /api/uploads/session/{session_id}/files/{file_id}/download
async function downloadFile(sessionId: string, fileId: string) {
  const response = await fetch(
    `${API_CONFIG.BASE_URL}/uploads/session/${sessionId}/files/${fileId}/download`
  )
  
  if (!response.ok) throw new Error('Download failed')
  
  // Get filename from Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition')
  const filename = contentDisposition?.split('filename=')[1]?.replace(/"/g, '') || 'file'
  
  // Create blob and download
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}
```

### 6. Delete File

```typescript
// DELETE /api/uploads/session/{session_id}/files/{file_id}
async function deleteFile(sessionId: string, fileId: string) {
  const response = await fetch(
    `${API_CONFIG.BASE_URL}/uploads/session/${sessionId}/files/${fileId}`,
    { method: 'DELETE' }
  )
  
  const data: StandardResponse<{ success: boolean; message: string }> = await response.json()
  return data.data
}
```

### 7. Delete Session

```typescript
// DELETE /api/uploads/session/{session_id}
async function deleteSession(sessionId: string) {
  const response = await fetch(
    `${API_CONFIG.BASE_URL}/uploads/session/${sessionId}`,
    { method: 'DELETE' }
  )
  
  const data: StandardResponse<{ success: boolean; message: string }> = await response.json()
  return data.data
}
```

### 8. Upload & Auto-Parse PO

Automatically parse and save PO files. Supports **Bajaj** (client_id=1) and **Dava India** (client_id=2) PO formats.

```typescript
// POST /api/po/upload?client_id=1&project_id=3&auto_save=true
// client_id: 1 = Bajaj, 2 = Dava India

async function uploadAndParsePO(
  file: File,
  clientId: number,  // 1 for Bajaj, 2 for Dava India
  projectId?: number,
  autoSave: boolean = true
) {
  const formData = new FormData()
  formData.append('file', file)
  
  const params = new URLSearchParams({
    client_id: String(clientId),
    auto_save: String(autoSave)
  })
  
  if (projectId) {
    params.append('project_id', String(projectId))
  }
  
  const response = await fetch(
    `${API_CONFIG.BASE_URL}/po/upload?${params}`,
    {
      method: 'POST',
      body: formData
    }
  )
  
  const data: StandardResponse<ParsedPOResponse> = await response.json()
  return data.data
}

// Example: Upload Bajaj PO
const bajajResult = await uploadAndParsePO(
  bajajExcelFile,
  1,  // Bajaj client ID
  projectId,
  true
)

// Example: Upload Dava India PO
const davaResult = await uploadAndParsePO(
  davaProformaFile,
  2,  // Dava India client ID
  projectId,
  true
)

interface ParsedPOResponse {
  status: 'success' | 'error'
  client_id: number  // 1 = Bajaj, 2 = Dava India
  client_name: string  // "Bajaj" or "Dava India"
  po_details: {
    po_number: string
    po_date: string
    po_value: number
    vendor_name: string
  }
  line_items: Array<{
    description: string
    quantity: number
    unit_price: number
    amount: number
  }>
  client_po_id?: number
  parsing_status: 'completed' | 'failed'
  error?: string
}
```

---

## Purchase Orders (PO Management)

### 1. Get All POs

```typescript
// GET /api/po?skip=0&limit=50
async function getAllPOs(skip: number = 0, limit: number = 50) {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
  const response = await fetch(`${API_CONFIG.BASE_URL}/po?${params}`)
  const data: StandardResponse<{ pos: PurchaseOrder[]; total_count: number }> = await response.json()
  
  return data.data
}

interface PurchaseOrder {
  id: number
  po_number: string
  po_date: string
  po_value: number
  vendor_name: string
  client_id: number
  status: 'active' | 'completed' | 'cancelled'
  created_at: string
  updated_at: string
}
```

### 2. Get Single PO with Line Items

```typescript
// GET /api/client-po/{client_po_id}
async function getPODetails(poId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/client-po/${poId}`)
  const data: StandardResponse<any> = await response.json()
  
  return data.data
  // { po_number, po_date, po_value, vendor_name, line_items: [...], ... }
}
```

### 3. Get POs for Project

```typescript
// GET /api/projects/{project_id}/po
async function getProjectPOs(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/po`)
  const data: StandardResponse<{ pos: PurchaseOrder[]; total_project_value: number }> = await response.json()
  
  return data.data
}
```

### 4. Create PO for Project

```typescript
// POST /api/projects/{project_id}/po
interface CreatePORequest {
  po_number: string
  po_date: string
  po_value: number
  vendor_name: string
  description?: string
  client_id?: number
}

async function createPO(projectId: number, request: CreatePORequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/po`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<PurchaseOrder> = await response.json()
  return data.data
}
```

### 5. Update PO

```typescript
// PUT /api/po/{po_id}
interface UpdatePORequest {
  po_number?: string
  po_date?: string
  po_value?: number
  vendor_name?: string
  status?: string
}

async function updatePO(poId: number, request: UpdatePORequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/po/${poId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<PurchaseOrder> = await response.json()
  return data.data
}
```

### 6. Delete PO

```typescript
// DELETE /api/po/{po_id}
async function deletePO(poId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/po/${poId}`, {
    method: 'DELETE'
  })
  
  const data: StandardResponse<{ success: boolean; message: string; client_po_id: number }> = await response.json()
  return data.data
}
```

### 7. Get Enriched POs (with Payment Data)

```typescript
// GET /api/projects/{project_id}/po/enriched
async function getEnrichedPOs(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/po/enriched`)
  const data: StandardResponse<{
    pos: Array<PurchaseOrder & { payment_amount: number; payment_status: string }>
  }> = await response.json()
  
  return data.data
}
```

---

## Line Items

### 1. Add Line Item to PO

```typescript
// POST /api/po/{client_po_id}/line-items
interface LineItemRequest {
  description: string
  quantity: number
  unit_price: number
  amount: number
}

async function addLineItem(poId: number, item: LineItemRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/po/${poId}/line-items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  })
  
  const data: StandardResponse<LineItem> = await response.json()
  return data.data
}

interface LineItem {
  id: number
  client_po_id: number
  description: string
  quantity: number
  unit_price: number
  amount: number
  created_at: string
}
```

### 2. Get Line Items for PO

```typescript
// GET /api/po/{client_po_id}/line-items
async function getLineItems(poId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/po/${poId}/line-items`)
  const data: StandardResponse<LineItem[]> = await response.json()
  
  return data.data
}
```

### 3. Update Line Item

```typescript
// PUT /api/line-items/{line_item_id}
interface LineItemUpdateRequest {
  description?: string
  quantity?: number
  unit_price?: number
  amount?: number
}

async function updateLineItem(lineItemId: number, request: LineItemUpdateRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/line-items/${lineItemId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<LineItem> = await response.json()
  return data.data
}
```

### 4. Delete Line Item

```typescript
// DELETE /api/line-items/{line_item_id}
async function deleteLineItem(lineItemId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/line-items/${lineItemId}`, {
    method: 'DELETE'
  })
  
  const data: StandardResponse<{ success: boolean; message: string }> = await response.json()
  return data.data
}
```

---

## Vendors

### 1. Get All Vendors

```typescript
// GET /api/vendors?status=active
async function getAllVendors(status?: 'active' | 'inactive') {
  const params = new URLSearchParams()
  if (status) params.append('status', status)
  
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendors${params ? '?' + params : ''}`)
  const data: StandardResponse<{ vendors: Vendor[]; vendor_count: number }> = await response.json()
  
  return data.data
}

interface Vendor {
  id: number
  name: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
  gstin?: string
  payment_terms?: string
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}
```

### 2. Get Single Vendor

```typescript
// GET /api/vendors/{vendor_id}
async function getVendorDetails(vendorId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendors/${vendorId}`)
  const data: StandardResponse<VendorDetails> = await response.json()
  
  return data.data
}

interface VendorDetails extends Vendor {
  active_orders: number
  total_payable: number
  total_paid: number
}
```

### 3. Create Vendor

```typescript
// POST /api/vendors
interface CreateVendorRequest {
  name: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
  payment_terms?: string
}

async function createVendor(request: CreateVendorRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<Vendor> = await response.json()
  return data.data
}
```

### 4. Update Vendor

```typescript
// PUT /api/vendors/{vendor_id}
interface UpdateVendorRequest {
  name?: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
  payment_terms?: string
  status?: string
}

async function updateVendor(vendorId: number, request: UpdateVendorRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendors/${vendorId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<Vendor> = await response.json()
  return data.data
}
```

### 5. Delete Vendor

```typescript
// DELETE /api/vendors/{vendor_id}
async function deleteVendor(vendorId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendors/${vendorId}`, {
    method: 'DELETE'
  })
  
  const data: StandardResponse<{ success: boolean; message: string }> = await response.json()
  return data.data
}
```

### 6. Get Vendor Payment History

```typescript
// GET /api/vendors/{vendor_id}/payments
async function getVendorPayments(vendorId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendors/${vendorId}/payments`)
  const data: StandardResponse<{ payments: Payment[]; payment_count: number }> = await response.json()
  
  return data.data
}
```

---

## Vendor Orders

### 1. Create Vendor Order

```typescript
// POST /api/projects/{project_id}/vendor-orders
interface CreateVendorOrderRequest {
  vendor_id: number
  po_number: string
  amount: number
  description?: string
  status?: string
}

async function createVendorOrder(projectId: number, request: CreateVendorOrderRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/vendor-orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<VendorOrder> = await response.json()
  return data.data
}

interface VendorOrder {
  id: number
  project_id: number
  vendor_id: number
  po_number: string
  amount: number
  status: string
  description?: string
  created_at: string
}
```

### 2. Get Project Vendor Orders

```typescript
// GET /api/projects/{project_id}/vendor-orders
async function getProjectVendorOrders(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/vendor-orders`)
  const data: StandardResponse<VendorOrder[]> = await response.json()
  
  return data.data
}
```

### 3. Get Single Vendor Order

```typescript
// GET /api/vendor-orders/{vendor_order_id}
async function getVendorOrderDetails(orderId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendor-orders/${orderId}`)
  const data: StandardResponse<VendorOrder> = await response.json()
  
  return data.data
}
```

### 4. Update Vendor Order

```typescript
// PUT /api/projects/{project_id}/vendor-orders/{vendor_order_id}
interface UpdateVendorOrderRequest {
  vendor_id?: number
  po_number?: string
  amount?: number
  description?: string
}

async function updateVendorOrder(projectId: number, orderId: number, request: UpdateVendorOrderRequest) {
  const response = await fetch(
    `${API_CONFIG.BASE_URL}/projects/${projectId}/vendor-orders/${orderId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    }
  )
  
  const data: StandardResponse<VendorOrder> = await response.json()
  return data.data
}
```

### 5. Update Vendor Order Status

```typescript
// PUT /api/vendor-orders/{vendor_order_id}/status
async function updateVendorOrderStatus(orderId: number, status: string) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendor-orders/${orderId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  })
  
  const data: StandardResponse<VendorOrder> = await response.json()
  return data.data
}
```

### 6. Delete Vendor Order

```typescript
// DELETE /api/projects/{project_id}/vendor-orders/{vendor_order_id}
async function deleteVendorOrder(projectId: number, orderId: number) {
  const response = await fetch(
    `${API_CONFIG.BASE_URL}/projects/${projectId}/vendor-orders/${orderId}`,
    { method: 'DELETE' }
  )
  
  const data: StandardResponse<{ success: boolean; message: string }> = await response.json()
  return data.data
}
```

### 7. Add Line Item to Vendor Order

```typescript
// POST /api/vendor-orders/{vendor_order_id}/line-items
interface VendorOrderLineItemRequest {
  description: string
  quantity: number
  unit_price: number
  amount: number
}

async function addVendorOrderLineItem(orderId: number, item: VendorOrderLineItemRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/vendor-orders/${orderId}/line-items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  })
  
  const data: StandardResponse<VendorOrderLineItem> = await response.json()
  return data.data
}

interface VendorOrderLineItem {
  id: number
  vendor_order_id: number
  description: string
  quantity: number
  unit_price: number
  amount: number
  created_at: string
}
```

---

## Payments

### 1. Create Payment

```typescript
// POST /api/po/{po_id}/payments
interface CreatePaymentRequest {
  amount: number
  payment_date: string
  payment_method: string
  reference_number?: string
  notes?: string
}

async function createPayment(poId: number, request: CreatePaymentRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/po/${poId}/payments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<Payment> = await response.json()
  return data.data
}

interface Payment {
  id: number
  po_id: number
  amount: number
  payment_date: string
  payment_method: string
  status: 'pending' | 'completed' | 'failed'
  reference_number?: string
  notes?: string
  created_at: string
}
```

### 2. Get PO Payments

```typescript
// GET /api/po/{po_id}/payments
async function getPOPayments(poId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/po/${poId}/payments`)
  const data: StandardResponse<Payment[]> = await response.json()
  
  return data.data
}
```

### 3. Update Payment

```typescript
// PUT /api/payments/{payment_id}
interface UpdatePaymentRequest {
  amount?: number
  payment_date?: string
  payment_method?: string
  reference_number?: string
  notes?: string
  status?: string
}

async function updatePayment(paymentId: number, request: UpdatePaymentRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/payments/${paymentId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<Payment> = await response.json()
  return data.data
}
```

### 4. Delete Payment

```typescript
// DELETE /api/payments/{payment_id}
async function deletePayment(paymentId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/payments/${paymentId}`, {
    method: 'DELETE'
  })
  
  const data: StandardResponse<{ success: boolean; message: string }> = await response.json()
  return data.data
}
```

---

## Projects

### 1. Get All Projects

```typescript
// GET /api/projects?skip=0&limit=50
async function getAllProjects(skip: number = 0, limit: number = 50) {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects?${params}`)
  const data: StandardResponse<{ projects: Project[]; project_count: number }> = await response.json()
  
  return data.data
}

interface Project {
  id: number
  name: string
  client_id: number
  location?: string
  city?: string
  state?: string
  country?: string
  latitude?: number
  longitude?: number
  status: 'active' | 'completed' | 'on-hold'
  created_at: string
  updated_at: string
}
```

### 2. Get Single Project

```typescript
// GET /api/projects/{project_id}
async function getProjectDetails(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}`)
  const data: StandardResponse<Project> = await response.json()
  
  return data.data
}
```

### 3. Create Project

```typescript
// POST /api/projects
interface CreateProjectRequest {
  name: string
  client_id?: number
  location?: string
  city?: string
  state?: string
  country?: string
  latitude?: number
  longitude?: number
}

async function createProject(request: CreateProjectRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<Project> = await response.json()
  return data.data
}
```

### 4. Update Project

```typescript
// PUT /api/projects/{project_id}
interface UpdateProjectRequest {
  name?: string
  location?: string
  city?: string
  state?: string
  country?: string
  latitude?: number
  longitude?: number
  status?: string
}

async function updateProject(projectId: number, request: UpdateProjectRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<Project> = await response.json()
  return data.data
}
```

### 5. Delete Project

```typescript
// DELETE /api/projects/{project_id}
async function deleteProject(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}`, {
    method: 'DELETE'
  })
  
  const data: StandardResponse<{ success: boolean; message: string }> = await response.json()
  return data.data
}
```

### 6. Get Project Financial Summary

```typescript
// GET /api/projects/{project_id}/financial-summary
async function getProjectFinancialSummary(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/financial-summary`)
  const data: StandardResponse<FinancialSummary> = await response.json()
  
  return data.data
}

interface FinancialSummary {
  project_id: number
  total_po_value: number
  total_billing_value: number
  total_vendor_order_value: number
  total_payments: number
  remaining_payable: number
  profit_loss: number
}
```

### 7. Search Projects

```typescript
// GET /api/projects/search?q=Mumbai
async function searchProjects(query: string) {
  const params = new URLSearchParams({ q: query })
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/search?${params}`)
  const data: StandardResponse<{ projects: Project[]; project_count: number }> = await response.json()
  
  return data.data
}
```

---

## Billing POs

### 1. Create Billing PO

```typescript
// POST /api/projects/{project_id}/billing-po
interface CreateBillingPORequest {
  po_number: string
  amount: number
  status?: string
  description?: string
}

async function createBillingPO(projectId: number, request: CreateBillingPORequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/billing-po`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<BillingPO> = await response.json()
  return data.data
}

interface BillingPO {
  id: string
  project_id: number
  po_number: string
  amount: number
  status: string
  created_at: string
  updated_at: string
}
```

### 2. Get Billing PO Details

```typescript
// GET /api/billing-po/{billing_po_id}
async function getBillingPODetails(billingPoId: string) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/billing-po/${billingPoId}`)
  const data: StandardResponse<BillingPODetails> = await response.json()
  
  return data.data
}

interface BillingPODetails extends BillingPO {
  line_items: Array<{
    id: string
    description: string
    quantity: number
    unit_price: number
    amount: number
  }>
}
```

### 3. Get Project Billing Summary

```typescript
// GET /api/projects/{project_id}/billing-summary
async function getProjectBillingSummary(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/billing-summary`)
  const data: StandardResponse<BillingSummary> = await response.json()
  
  return data.data
}

interface BillingSummary {
  project_id: number
  total_billing_value: number
  billing_count: number
  approved_billing: number
  pending_approval: number
}
```

### 4. Add Billing Line Item

```typescript
// POST /api/billing-po/{billing_po_id}/line-items
interface BillingLineItemRequest {
  item_description: string
  quantity: number
  unit_price: number
  amount: number
}

async function addBillingLineItem(billingPoId: string, item: BillingLineItemRequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/billing-po/${billingPoId}/line-items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  })
  
  const data: StandardResponse<any> = await response.json()
  return data.data
}
```

### 5. Get Billing Line Items

```typescript
// GET /api/billing-po/{billing_po_id}/line-items
async function getBillingLineItems(billingPoId: string) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/billing-po/${billingPoId}/line-items`)
  const data: StandardResponse<any[]> = await response.json()
  
  return data.data
}
```

### 6. Update Billing PO

```typescript
// PUT /api/billing-po/{billing_po_id}
interface UpdateBillingPORequest {
  po_number?: string
  amount?: number
  status?: string
}

async function updateBillingPO(billingPoId: string, request: UpdateBillingPORequest) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/billing-po/${billingPoId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  })
  
  const data: StandardResponse<BillingPO> = await response.json()
  return data.data
}
```

### 7. Approve Billing PO

```typescript
// POST /api/billing-po/{billing_po_id}/approve
async function approveBillingPO(billingPoId: string, approvedBy: string) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/billing-po/${billingPoId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved_by: approvedBy })
  })
  
  const data: StandardResponse<BillingPO> = await response.json()
  return data.data
}
```

### 8. Get Project P&L Analysis

```typescript
// GET /api/projects/{project_id}/billing-pl-analysis
async function getProjectPLAnalysis(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/projects/${projectId}/billing-pl-analysis`)
  const data: StandardResponse<PLAnalysis> = await response.json()
  
  return data.data
}

interface PLAnalysis {
  project_id: number
  total_revenue: number
  total_cost: number
  gross_profit: number
  profit_margin: number
}
```

---

## Documents

### 1. Upload Document

```typescript
// POST /api/documents/upload (multipart/form-data)
async function uploadDocument(
  file: File,
  options: {
    project_id?: number
    client_po_id?: number
    po_number?: string
    description?: string
  }
) {
  const formData = new FormData()
  formData.append('file', file)
  
  if (options.project_id) {
    formData.append('project_id', String(options.project_id))
  }
  if (options.client_po_id) {
    formData.append('client_po_id', String(options.client_po_id))
  }
  if (options.po_number) {
    formData.append('po_number', options.po_number)
  }
  if (options.description) {
    formData.append('description', options.description)
  }
  
  const response = await fetch(`${API_CONFIG.BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData
  })
  
  const data: StandardResponse<Document> = await response.json()
  return data.data
}

interface Document {
  id: number
  document_name: string
  document_path: string
  compressed_filename: string
  download_url: string
  file_size: number
  created_at: string
}
```

### 2. Get Documents for Project

```typescript
// GET /api/documents/project/{project_id}
async function getProjectDocuments(projectId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/documents/project/${projectId}`)
  const data: StandardResponse<{ documents: Document[] }> = await response.json()
  
  return data.data
}
```

### 3. Get Documents for PO

```typescript
// GET /api/documents/po/{client_po_id}
async function getPODocuments(poId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/documents/po/${poId}`)
  const data: StandardResponse<{ documents: Document[] }> = await response.json()
  
  return data.data
}
```

### 4. Get Single Document

```typescript
// GET /api/documents/{doc_id}
async function getDocumentDetails(docId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/documents/${docId}`)
  const data: StandardResponse<Document> = await response.json()
  
  return data.data  // Includes download_url
}
```

### 5. Download Document

```typescript
// GET /api/documents/download/{doc_id}
async function downloadDocument(docId: number) {
  const response = await fetch(`${API_CONFIG.BASE_URL}/documents/download/${docId}`)
  
  if (!response.ok) throw new Error('Download failed')
  
  const blob = await response.blob()
  const filename = response.headers.get('Content-Disposition')?.split('filename=')[1]?.replace(/"/g, '') || `document-${docId}`
  
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}
```

---

## Error Handling

### Standard Error Handling Pattern

```typescript
interface APIError {
  error_code: string
  message: string
  status_code: number
  details?: any
}

class APIErrorHandler {
  static handle(error: unknown): APIError {
    if (error instanceof Response) {
      return {
        status_code: error.status,
        error_code: this.mapStatusCode(error.status),
        message: error.statusText,
        details: error
      }
    }
    
    if (error instanceof Error) {
      return {
        status_code: 500,
        error_code: 'UNKNOWN_ERROR',
        message: error.message
      }
    }
    
    return {
      status_code: 500,
      error_code: 'UNKNOWN_ERROR',
      message: 'An unknown error occurred'
    }
  }
  
  private static mapStatusCode(status: number): string {
    const map: { [key: number]: string } = {
      400: 'VALIDATION_ERROR',
      401: 'UNAUTHORIZED',
      403: 'FORBIDDEN',
      404: 'NOT_FOUND',
      422: 'VALIDATION_ERROR',
      500: 'SERVER_ERROR'
    }
    return map[status] || 'UNKNOWN_ERROR'
  }
}

// Usage
async function safeAPICall<T>(
  fn: () => Promise<T>,
  onError?: (error: APIError) => void
): Promise<T | null> {
  try {
    return await fn()
  } catch (error) {
    const apiError = APIErrorHandler.handle(error)
    onError?.(apiError)
    console.error(`API Error: ${apiError.error_code}`, apiError.message)
    return null
  }
}

// Example usage
const projects = await safeAPICall(
  () => getAllProjects(),
  (error) => {
    if (error.error_code === 'UNAUTHORIZED') {
      // Redirect to login
    } else if (error.error_code === 'SERVER_ERROR') {
      // Show retry button
    }
  }
)
```

### Validation Error Handler

```typescript
interface ValidationError {
  field: string
  message: string
  type: string
}

function handleValidationErrors(errors: ValidationError[]): { [key: string]: string } {
  const fieldErrors: { [key: string]: string } = {}
  
  errors.forEach(error => {
    fieldErrors[error.field] = error.message
  })
  
  return fieldErrors
}

// Usage in form
async function submitForm(formData: CreatePORequest) {
  try {
    const result = await createPO(projectId, formData)
    // Success
  } catch (error) {
    if (error.error_code === 'VALIDATION_ERROR') {
      const fieldErrors = handleValidationErrors(error.details.errors)
      // Set form errors
      setErrors(fieldErrors)
    }
  }
}
```

---

## TypeScript/JavaScript Examples

### Complete React Hook Example

```typescript
// hooks/usePO.ts
import { useState, useCallback } from 'react'
import { PurchaseOrder } from '@/types'

export function usePO(projectId: number) {
  const [pos, setPOs] = useState<PurchaseOrder[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const fetchPOs = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await getProjectPOs(projectId)
      setPOs(result.pos)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch POs')
    } finally {
      setLoading(false)
    }
  }, [projectId])
  
  const createNewPO = useCallback(
    async (request: CreatePORequest) => {
      try {
        const newPO = await createPO(projectId, request)
        setPOs(prev => [...prev, newPO])
        return newPO
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create PO')
        throw err
      }
    },
    [projectId]
  )
  
  const removePO = useCallback(
    async (poId: number) => {
      try {
        await deletePO(poId)
        setPOs(prev => prev.filter(po => po.id !== poId))
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete PO')
        throw err
      }
    },
    []
  )
  
  return { pos, loading, error, fetchPOs, createNewPO, removePO }
}
```

### File Upload with Progress

```typescript
// components/FileUploadZone.tsx
function FileUploadZone({ projectId }: { projectId: number }) {
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  
  const handleFileSelect = (selectedFiles: FileList) => {
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i]
      
      // Validate file size
      if (file.size > API_CONFIG.UPLOAD.MAX_SIZE) {
        alert(`File ${file.name} is too large (max 50MB)`)
        continue
      }
      
      // Validate file type
      if (!API_CONFIG.UPLOAD.ALLOWED_TYPES.includes(file.type)) {
        alert(`File ${file.name} is not supported`)
        continue
      }
      
      setFiles(prev => [...prev, file])
    }
  }
  
  const uploadFiles = async () => {
    if (files.length === 0) return
    
    setUploading(true)
    
    try {
      // Create session
      const session = await createSession()
      
      // Upload each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        
        await uploadFile(session.session_id, file, {
          uploaded_by: 'current-user@example.com'
        })
        
        // Update progress
        const progress = Math.round(((i + 1) / files.length) * 100)
        setUploadProgress(progress)
      }
      
      // Success
      alert('Files uploaded successfully!')
      setFiles([])
      setUploadProgress(0)
    } catch (error) {
      alert(`Upload failed: ${error}`)
    } finally {
      setUploading(false)
    }
  }
  
  return (
    <div>
      <input
        type="file"
        multiple
        onChange={(e) => handleFileSelect(e.target.files!)}
        disabled={uploading}
      />
      <button onClick={uploadFiles} disabled={uploading || files.length === 0}>
        {uploading ? `Uploading... ${uploadProgress}%` : 'Upload'}
      </button>
    </div>
  )
}
```

### Data Table with Pagination

```typescript
// components/POTable.tsx
import { useEffect, useState } from 'react'

function POTable({ projectId }: { projectId: number }) {
  const [pos, setPOs] = useState<PurchaseOrder[]>([])
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(10)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    const fetchPOs = async () => {
      setLoading(true)
      try {
        const result = await getProjectPOs(projectId)
        setPOs(result.pos.slice(page * pageSize, (page + 1) * pageSize))
        setTotal(result.pos.length)
      } finally {
        setLoading(false)
      }
    }
    
    fetchPOs()
  }, [projectId, page, pageSize])
  
  const columns = [
    { header: 'PO Number', render: (po: PurchaseOrder) => po.po_number },
    { header: 'Vendor', render: (po: PurchaseOrder) => po.vendor_name },
    { header: 'Amount', render: (po: PurchaseOrder) => `₹${po.po_value.toLocaleString()}` },
    { header: 'Status', render: (po: PurchaseOrder) => po.status },
    { header: 'Date', render: (po: PurchaseOrder) => new Date(po.po_date).toLocaleDateString() }
  ]
  
  return (
    <div>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                {columns.map(col => <th key={col.header}>{col.header}</th>)}
              </tr>
            </thead>
            <tbody>
              {pos.map(po => (
                <tr key={po.id}>
                  {columns.map(col => (
                    <td key={col.header}>{col.render(po)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          
          <div>
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
            >
              Previous
            </button>
            <span>Page {page + 1} of {Math.ceil(total / pageSize)}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={(page + 1) * pageSize >= total}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
```

---

## State Management Patterns

### Zustand Store Example

```typescript
// store/projectStore.ts
import { create } from 'zustand'

interface ProjectStore {
  projects: Project[]
  currentProject: Project | null
  loading: boolean
  error: string | null
  
  // Actions
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project | null) => void
  fetchProjects: () => Promise<void>
  fetchProjectById: (id: number) => Promise<void>
  createNewProject: (request: CreateProjectRequest) => Promise<void>
  updateExistingProject: (id: number, request: UpdateProjectRequest) => Promise<void>
  removeProject: (id: number) => Promise<void>
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: [],
  currentProject: null,
  loading: false,
  error: null,
  
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  
  fetchProjects: async () => {
    set({ loading: true, error: null })
    try {
      const result = await getAllProjects()
      set({ projects: result.projects })
    } catch (error) {
      set({ error: `Failed to fetch projects` })
    } finally {
      set({ loading: false })
    }
  },
  
  fetchProjectById: async (id) => {
    set({ loading: true, error: null })
    try {
      const project = await getProjectDetails(id)
      set({ currentProject: project })
    } catch (error) {
      set({ error: `Failed to fetch project` })
    } finally {
      set({ loading: false })
    }
  },
  
  createNewProject: async (request) => {
    set({ loading: true, error: null })
    try {
      const newProject = await createProject(request)
      set(state => ({
        projects: [...state.projects, newProject]
      }))
    } catch (error) {
      set({ error: `Failed to create project` })
      throw error
    } finally {
      set({ loading: false })
    }
  },
  
  updateExistingProject: async (id, request) => {
    set({ loading: true, error: null })
    try {
      const updated = await updateProject(id, request)
      set(state => ({
        projects: state.projects.map(p => p.id === id ? updated : p),
        currentProject: state.currentProject?.id === id ? updated : state.currentProject
      }))
    } catch (error) {
      set({ error: `Failed to update project` })
      throw error
    } finally {
      set({ loading: false })
    }
  },
  
  removeProject: async (id) => {
    set({ loading: true, error: null })
    try {
      await deleteProject(id)
      set(state => ({
        projects: state.projects.filter(p => p.id !== id),
        currentProject: state.currentProject?.id === id ? null : state.currentProject
      }))
    } catch (error) {
      set({ error: `Failed to delete project` })
      throw error
    } finally {
      set({ loading: false })
    }
  }
}))
```

### Redux Store Example

```typescript
// store/projectSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

export const fetchProjects = createAsyncThunk(
  'projects/fetchProjects',
  async () => {
    const result = await getAllProjects()
    return result.projects
  }
)

export const createNewProject = createAsyncThunk(
  'projects/create',
  async (request: CreateProjectRequest) => {
    return await createProject(request)
  }
)

const projectSlice = createSlice({
  name: 'projects',
  initialState: {
    items: [] as Project[],
    loading: false,
    error: null as string | null,
    currentProject: null as Project | null
  },
  reducers: {
    setCurrentProject: (state, action) => {
      state.currentProject = action.payload
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProjects.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload
      })
      .addCase(fetchProjects.rejected, (state) => {
        state.loading = false
        state.error = 'Failed to fetch projects'
      })
      .addCase(createNewProject.fulfilled, (state, action) => {
        state.items.push(action.payload)
      })
  }
})

export default projectSlice.reducer
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: CORS Errors

**Problem**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
- Verify `CORS_ORIGINS` environment variable includes your frontend URL
- Backend must be running with correct CORS configuration
- Ensure frontend URL matches exactly (protocol, domain, port)

```typescript
// Check CORS configuration
async function checkCORS() {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/health`)
    console.log('CORS OK')
  } catch (error) {
    console.error('CORS Error:', error)
  }
}
```

#### Issue: 401 Unauthorized

**Problem**: API returns 401 on authenticated endpoints

**Solution**:
- Credentials may be incorrect
- Credentials not included in Authorization header
- Use Basic auth format `Basic <base64(username:password)>`

```typescript
// Debug authentication
function debugAuth() {
  const credentials = AuthService.getCredentials()
  console.log('Username:', credentials.username)
  console.log('Password stored:', !!credentials.password)
  
  // Check credentials format
  if (credentials.username && credentials.password) {
    const base64 = btoa(`${credentials.username}:${credentials.password}`)
    console.log('Basic Auth Header:', `Basic ${base64}`)
  } else {
    console.log('❌ No credentials stored - user not logged in')
  }
}
```

#### Issue: File Upload Failed

**Problem**: `413 Payload Too Large` or file rejected

**Solution**:
- File size exceeds `MAX_FILE_SIZE` (50MB)
- File type not in `ALLOWED_FILE_TYPES`
- Check `Content-Type` header not being set for multipart/form-data

```typescript
// Validate file before upload
function validateFile(file: File): string | null {
  const maxSize = API_CONFIG.UPLOAD.MAX_SIZE
  const allowedTypes = API_CONFIG.UPLOAD.ALLOWED_TYPES
  
  if (file.size > maxSize) {
    return `File size ${(file.size / 1024 / 1024).toFixed(2)}MB exceeds limit of 50MB`
  }
  
  if (!allowedTypes.includes(file.type)) {
    return `File type ${file.type} not supported. Allowed: ${allowedTypes.join(', ')}`
  }
  
  return null
}
```

#### Issue: Slow API Response

**Problem**: API takes 10+ seconds to respond

**Solution**:
- Database connection issues
- Large result set being processed
- API overloaded

```typescript
// Monitor API performance
async function monitorAPIPerformance(endpoint: string, fn: () => Promise<any>) {
  const start = performance.now()
  const result = await fn()
  const duration = performance.now() - start
  
  console.log(`${endpoint} took ${duration.toFixed(2)}ms`)
  
  if (duration > 5000) {
    console.warn('⚠️ Slow API response - consider optimization')
  }
  
  return result
}
```

#### Issue: Network Timeout

**Problem**: `AbortError: The operation was aborted`

**Solution**:
- Increase `VITE_API_TIMEOUT` environment variable
- Check network connectivity
- Server may be unresponsive

```typescript
// Implement exponential backoff retry
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      const delay = Math.pow(2, i) * 1000
      console.log(`Retry ${i + 1}/${maxRetries} in ${delay}ms`)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  throw new Error('Max retries exceeded')
}
```

---

## API Endpoint Summary

| Feature | Method | Endpoint | Description |
|---------|--------|----------|-------------|
| Health | GET | `/api/health` | Basic health check |
| Session | POST | `/api/uploads/session` | Create upload session |
| Files | POST | `/api/uploads/session/{session_id}/files` | Upload file |
| Files | GET | `/api/uploads/session/{session_id}/files` | List files |
| Files | DELETE | `/api/uploads/session/{session_id}/files/{file_id}` | Delete file |
| PO | GET | `/api/po` | Get all POs |
| PO | POST | `/api/po` | Create PO |
| PO | PUT | `/api/po/{po_id}` | Update PO |
| PO | DELETE | `/api/po/{po_id}` | Delete PO |
| LineItems | POST | `/api/po/{po_id}/line-items` | Add line item |
| LineItems | GET | `/api/po/{po_id}/line-items` | Get line items |
| Vendors | GET | `/api/vendors` | Get vendors |
| Vendors | POST | `/api/vendors` | Create vendor |
| Vendors | DELETE | `/api/vendors/{vendor_id}` | Delete vendor |
| Projects | GET | `/api/projects` | Get projects |
| Projects | POST | `/api/projects` | Create project |
| Payments | POST | `/api/po/{po_id}/payments` | Create payment |
| Payments | GET | `/api/po/{po_id}/payments` | Get payments |
| Documents | POST | `/api/documents/upload` | Upload document |
| Documents | GET | `/api/documents/project/{project_id}` | Get project docs |

---

## Support & Resources

- **API Documentation**: Available at `http://localhost:8000/api/docs` (Swagger)
- **ReDoc**: Available at `http://localhost:8000/api/redoc`
- **Backend Repository**: DEPLOYMENT_GUIDE.md, README_PRODUCTION.md
- **Error Codes**: See Error Handling section above

---

**Last Updated**: February 17, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0.0
