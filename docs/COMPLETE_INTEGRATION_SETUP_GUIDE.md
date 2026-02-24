# Nexgen ERP Finance - Complete Integration Setup Guide

**Version**: 1.0.0 | **Status**: ✅ Production Ready  
**Last Updated**: February 17, 2026

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Database Configuration](#database-configuration)
5. [Environment Configuration](#environment-configuration)
6. [Authentication Setup](#authentication-setup)
7. [Common Workflows](#common-workflows)
8. [Testing & Verification](#testing--verification)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Overview

```
┌─────────────────────────────────────────────┐
│         Frontend (React/Vue/Angular)        │
│  - Dashboard & UI                           │
│  - File Upload Interface                    │
│  - Form Management                          │
│  - State Management (Zustand/Redux)         │
└────────────────┬────────────────────────────┘
                 │ HTTP/HTTPS
                 │ Basic Auth (Base64)
                 ▼
┌─────────────────────────────────────────────┐
│      FastAPI Backend (Production Ready)     │
│  - 95+ Routes across 13 API modules         │
│  - PostgreSQL Database Integration          │
│  - File Upload & Parsing System             │
│  - Connection Pooling (20-50+ connections)  │
│  - JSON Logging with Rotation               │
│  - CORS & Security Middleware               │
└────────────────┬────────────────────────────┘
                 │ SQL
                 ▼
     ┌───────────────────────────┐
     │  PostgreSQL Database      │
     │  - 18+ Tables             │
     │  - Financial Data         │
     │  - File Metadata          │
     └───────────────────────────┘
```

### Supported Clients & Parsers

| Client | Client ID | File Format | Parser Module | Parser Function |
|--------|-----------|-------------|---------------|-----------------|
| **Bajaj** | 1 | Excel/CSV | `bajaj_po_parser.py` | `parse_bajaj_po()` |
| **Dava India** | 2 | Proforma Invoice | `proforma_invoice_parser.py` | `parse_proforma_invoice()` |

---

## Backend Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Git
- Virtual Environment (venv or conda)

### Step 1: Clone & Setup Environment

```bash
# Navigate to backend directory
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create Environment File

Create `.env` file in backend root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nexgen_finances
DATABASE_POOL_MIN=20
DATABASE_POOL_MAX=50

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
ENVIRONMENT=development

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Authentication (optional - for future implementation)
AUTH_ENABLED=false

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB
UPLOAD_TEMP_DIR=uploads/temp
```

### Step 3: Initialize Database

```bash
# Apply migrations
python scripts/apply_schema.py

# Verify schema
python check_schema.py

# Check sample data
python check_db_data.py
```

### Step 4: Start Backend Server

```bash
# Development mode (with auto-reload)
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode (without reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Backend

```bash
# Check if app imports successfully
python -c "from app.main import app; print(f'✅ App imported - {len(app.routes)} routes registered')"

# Test API health
curl http://localhost:8000/api/health

# View API documentation
# Swagger: http://localhost:8000/api/docs
# ReDoc: http://localhost:8000/api/redoc
```

---

## Frontend Setup

### Prerequisites

- Node.js 16+ & npm/yarn
- React 18+ (or your chosen framework)
- TypeScript (recommended)

### Step 1: Create Project

```bash
# Using Vite (recommended)
npm create vite@latest nexgen-frontend -- --template react-ts

# Or using Create React App
npx create-react-app nexgen-frontend

# Navigate to project
cd nexgen-frontend

# Install dependencies
npm install
```

### Step 2: Install Required Packages

```bash
npm install \
  axios \
  zustand \
  react-query \
  react-router-dom \
  tailwindcss \
  @tanstack/react-query \
  cors \
  dotenv

# Optional: For forms
npm install react-hook-form zod

# Optional: For state management
npm install redux @reduxjs/toolkit react-redux
```

### Step 3: Create Environment File

Create `.env` in frontend root:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
VITE_FILE_UPLOAD_MAX_SIZE=52428800  # 50MB in bytes
VITE_POLLING_INTERVAL=5000
VITE_ENV=development
```

### Step 4: Setup Project Structure

```
src/
├── components/
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── FileUpload.tsx
│   ├── POForm.tsx
│   └── Dashboard.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── usePO.ts
│   ├── useProject.ts
│   └── useFileUpload.ts
├── services/
│   ├── api.ts
│   ├── auth.ts
│   └── poService.ts
├── store/
│   ├── projectStore.ts
│   ├── poStore.ts
│   └── authStore.ts
├── types/
│   ├── api.ts
│   ├── entities.ts
│   └── responses.ts
├── pages/
│   ├── Dashboard.tsx
│   ├── Projects.tsx
│   ├── POManagement.tsx
│   └── Vendors.tsx
├── App.tsx
└── main.tsx
```

### Step 5: Create API Service

`src/services/api.ts`:

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios'

class APIClient {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000')
    })
    
    // Add interceptors
    this.client.interceptors.request.use(config => {
      const credentials = this.getCredentials()
      if (credentials.username && credentials.password) {
        const auth = btoa(`${credentials.username}:${credentials.password}`)
        config.headers.Authorization = `Basic ${auth}`
      }
      return config
    })
    
    this.client.interceptors.response.use(
      response => response,
      error => this.handleError(error)
    )
  }
  
  private getCredentials() {
    return {
      username: localStorage.getItem('username') || '',
      password: localStorage.getItem('password') || ''
    }
  }
  
  private handleError(error: AxiosError) {
    if (error.response?.status === 401) {
      localStorage.removeItem('username')
      localStorage.removeItem('password')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
  
  async get<T>(path: string, config?: any) {
    return this.client.get<T>(path, config)
  }
  
  async post<T>(path: string, data?: any, config?: any) {
    return this.client.post<T>(path, data, config)
  }
  
  async put<T>(path: string, data?: any, config?: any) {
    return this.client.put<T>(path, data, config)
  }
  
  async delete<T>(path: string, config?: any) {
    return this.client.delete<T>(path, config)
  }
  
  async uploadFile<T>(path: string, formData: FormData, config?: any) {
    return this.client.post<T>(path, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      ...config
    })
  }
}

export const api = new APIClient()
```

### Step 6: Create Authentication Service

`src/services/auth.ts`:

```typescript
import { api } from './api'

export class AuthService {
  static login(username: string, password: string) {
    localStorage.setItem('username', username)
    localStorage.setItem('password', password)
    return Promise.resolve({ success: true })
  }
  
  static logout() {
    localStorage.removeItem('username')
    localStorage.removeItem('password')
  }
  
  static isLoggedIn(): boolean {
    return !!localStorage.getItem('username')
  }
  
  static getUsername(): string | null {
    return localStorage.getItem('username')
  }
}
```

### Step 7: Create Zustand Store

`src/store/projectStore.ts`:

```typescript
import { create } from 'zustand'
import { api } from '@/services/api'

interface ProjectStore {
  projects: any[]
  currentProject: any | null
  loading: boolean
  
  fetchProjects: () => Promise<void>
  fetchProjectById: (id: number) => Promise<void>
  createProject: (data: any) => Promise<void>
  updateProject: (id: number, data: any) => Promise<void>
  deleteProject: (id: number) => Promise<void>
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: [],
  currentProject: null,
  loading: false,
  
  fetchProjects: async () => {
    set({ loading: true })
    try {
      const response = await api.get('/projects?skip=0&limit=50')
      set({ projects: response.data.data.projects })
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      set({ loading: false })
    }
  },
  
  fetchProjectById: async (id) => {
    set({ loading: true })
    try {
      const response = await api.get(`/projects/${id}`)
      set({ currentProject: response.data.data })
    } catch (error) {
      console.error('Failed to fetch project:', error)
    } finally {
      set({ loading: false })
    }
  },
  
  createProject: async (data) => {
    try {
      const response = await api.post('/projects', data)
      set((state) => ({
        projects: [...state.projects, response.data.data]
      }))
    } catch (error) {
      console.error('Failed to create project:', error)
      throw error
    }
  },
  
  updateProject: async (id, data) => {
    try {
      const response = await api.put(`/projects/${id}`, data)
      set((state) => ({
        projects: state.projects.map(p => p.id === id ? response.data.data : p)
      }))
    } catch (error) {
      console.error('Failed to update project:', error)
      throw error
    }
  },
  
  deleteProject: async (id) => {
    try {
      await api.delete(`/projects/${id}`)
      set((state) => ({
        projects: state.projects.filter(p => p.id !== id)
      }))
    } catch (error) {
      console.error('Failed to delete project:', error)
      throw error
    }
  }
}))
```

### Step 8: Start Frontend

```bash
# Development
npm run dev

# Production build
npm run build

# Preview build
npm run preview

# Frontend will be available at:
# Vite: http://localhost:5173
# CRA: http://localhost:3000
```

---

## Database Configuration

### Prerequisites

```bash
# Install PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Linux: sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
# Windows: Services > PostgreSQL > Start
# macOS: brew services start postgresql
# Linux: sudo service postgresql start

# Create superuser if needed
sudo -u postgres createuser --superuser <username>
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE nexgen_finances;

# Create user
CREATE USER nexgen WITH PASSWORD 'your_secure_password';

# Grant privileges
ALTER ROLE nexgen SET client_encoding TO 'utf8';
ALTER ROLE nexgen SET default_transaction_isolation TO 'read committed';
ALTER ROLE nexgen SET default_transaction_deferrable TO on;
ALTER ROLE nexgen SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nexgen_finances TO nexgen;

# Exit psql
\q
```

### Apply Schema

```bash
# Run migrations
python scripts/apply_schema.py

# Verify tables
python check_schema_tables.py

# Check triggers
python list_all_triggers.py
```

---

## Environment Configuration

### Backend (.env)

```env
# ============ Database ============
DATABASE_URL=postgresql://nexgen:password@localhost:5432/nexgen_finances
DATABASE_POOL_MIN=20
DATABASE_POOL_MAX=50
DATABASE_ECHO=false

# ============ API ============
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
ENVIRONMENT=production
API_VERSION=1.0.0
WORKERS=4

# ============ Security ============
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://yourdomain.com"]
ALLOWED_ORIGINS=["localhost:5173","localhost:3000","yourdomain.com"]
AUTH_ENABLED=false
SECRET_KEY=your-secret-key-here

# ============ Logging ============
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# ============ File Upload ============
MAX_UPLOAD_SIZE=52428800
UPLOAD_TEMP_DIR=./uploads/temp
UPLOAD_SESSION_DIR=./uploads/sessions
ALLOWED_FILE_TYPES=.xlsx,.xls,.csv,.pdf

# ============ Performance ============
REQUEST_TIMEOUT=30
CACHE_TTL=3600
PAGINATION_MAX_SIZE=100
```

### Frontend (.env)

```env
# ============ API ============
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
VITE_API_RETRY_ATTEMPTS=3

# ============ File Upload ============
VITE_FILE_UPLOAD_MAX_SIZE=52428800
VITE_ALLOWED_FILE_TYPES=.xlsx,.xls,.csv

# ============ UI ============
VITE_POLLING_INTERVAL=5000
VITE_TOAST_DURATION=3000
VITE_PAGE_SIZE=20

# ============ Environment ============
VITE_ENV=development
VITE_DEBUG=true
```

---

## Authentication Setup

### Current State

Authentication is **optional** and uses **HTTP Basic Auth** (Base64-encoded username:password) when needed.

### Enable Authentication (Future)

When ready to implement:

1. **Backend** (`app/auth.py`):
   - Username/password validation
   - Session management
   - Role-based access control

2. **Frontend** (`src/services/auth.ts`):
   - Login form
   - Credential storage
   - Auto-logout on 401

### Current Implementation

```typescript
// Login (stores credentials in localStorage)
AuthService.login('admin', 'password')

// Every request includes:
// Authorization: Basic YWRtaW46cGFzc3dvcmQ=

// Logout
AuthService.logout()
```

---

## Common Workflows

### Workflow 1: Create Project → Upload PO → Create Payments

```typescript
import { useProjectStore } from '@/store/projectStore'
import { api } from '@/services/api'

async function completeProjectWorkflow() {
  // Step 1: Create Project
  const projectStore = useProjectStore()
  
  await projectStore.createProject({
    name: 'Mumbai Office Construction',
    location: 'Mumbai',
    city: 'Mumbai',
    state: 'Maharashtra'
  })
  
  const projectId = projectStore.currentProject.id
  
  // Step 2: Upload & Parse PO (Bajaj - Client ID 1)
  // Uses: bajaj_po_parser.parse_bajaj_po()
  const formData = new FormData()
  formData.append('file', bajajExcelFile)
  
  const poResponse = await api.post(
    `/po/upload?client_id=1&project_id=${projectId}&auto_save=true`,
    formData
  )
  
  const poId = poResponse.data.data.client_po_id
  
  // Step 3: Create Payment for PO
  await api.post(`/po/${poId}/payments`, {
    amount: poResponse.data.data.po_details.po_value,
    payment_date: new Date().toISOString().split('T')[0],
    payment_method: 'Bank Transfer',
    reference_number: 'TXN-001'
  })
  
  // Step 4: Get Financial Summary
  const summary = await api.get(`/projects/${projectId}/financial-summary`)
  
  console.log('Project Complete:', {
    project: projectStore.currentProject,
    po: poResponse.data.data,
    financial: summary.data.data
  })
}
```

### Workflow 2: Manage Vendors & Vendor Orders

```typescript
async function vendorManagementWorkflow() {
  // Create Vendor
  const vendorRes = await api.post('/vendors', {
    name: 'ABC Supplies Ltd',
    email: 'contact@abc-supplies.com',
    phone: '+91-9876543210',
    payment_terms: 'Net 30'
  })
  
  const vendorId = vendorRes.data.data.id
  
  // Create Vendor Order for Project
  const voRes = await api.post(`/projects/1/vendor-orders`, {
    vendor_id: vendorId,
    po_number: 'VO-2026-001',
    amount: 50000,
    description: 'Supply materials'
  })
  
  // Add Line Items
  await api.post(`/vendor-orders/${voRes.data.data.id}/line-items`, {
    description: 'Steel Rods (1\" diameter)',
    quantity: 100,
    unit_price: 500,
    amount: 50000
  })
  
  // Update Status
  await api.put(`/vendor-orders/${voRes.data.data.id}/status`, {
    status: 'completed'
  })
  
  // Get Vendor Payment History
  const payments = await api.get(`/vendors/${vendorId}/payments`)
  console.log('Vendor Payments:', payments.data.data)
}
```

### Workflow 3: Upload Multiple Bajaj POs (Bulk)

```typescript
async function bulkUploadBajajPOs(files: File[], projectId: number) {
  const formData = new FormData()
  
  // Add all files
  files.forEach(file => {
    formData.append('files', file)
  })
  
  // Add metadata
  formData.append('project_id', String(projectId))
  formData.append('created_by', 'user@example.com')
  
  const response = await api.post('/bajaj-po/bulk', formData)
  
  return response.data.data
  // {
  //   uploaded_count: 3,
  //   successful: 2,
  //   failed: 1,
  //   results: [...]
  // }
}
```

### Workflow 4: Generate Billing & P&L Analysis

```typescript
async function generateBillingReport(projectId: number) {
  // Create Billing PO
  const billingRes = await api.post(`/projects/${projectId}/billing-po`, {
    po_number: 'BILL-2026-001',
    amount: 150000,
    status: 'pending'
  })
  
  const billingPoId = billingRes.data.data.id
  
  // Add Billing Line Items
  await api.post(`/billing-po/${billingPoId}/line-items`, {
    item_description: 'Construction Services - Phase 1',
    quantity: 1,
    unit_price: 150000,
    amount: 150000
  })
  
  // Approve Billing
  await api.post(`/billing-po/${billingPoId}/approve`, {
    approved_by: 'admin@example.com'
  })
  
  // Get P&L Analysis
  const plAnalysis = await api.get(`/projects/${projectId}/billing-pl-analysis`)
  
  console.log('P&L Analysis:', {
    revenue: plAnalysis.data.data.total_revenue,
    cost: plAnalysis.data.data.total_cost,
    profit: plAnalysis.data.data.gross_profit,
    margin: plAnalysis.data.data.profit_margin + '%'
  })
}
```

---

## Testing & Verification

### Backend Tests

```bash
# Test all routes
python test_all_routes.py

# Test import
python -c "from app.main import app; print(f'✅ {len(app.routes)} routes')"

# Test database
python check_db_data.py

# Test file uploads
python test_file_uploads.py

# Run pytest
pytest tests/ -v
```

### Frontend Tests

```bash
# Unit tests
npm run test

# Build test
npm run build

# E2E tests
npm run test:e2e
```

### Manual API Testing with Postman

1. Import collection: `Postman_Collection_Backend.json`
2. Set environment variables:
   - `base_url`: http://localhost:8000/api
   - `project_id`: 1
   - `client_id`: 1 (Bajaj) or 2 (Dava India)
3. Run requests in order:
   - Health check
   - Get clients
   - Create project
   - Upload PO
   - Create payments
   - Generate financial summary

### cURL Examples

```bash
# Health Check
curl http://localhost:8000/api/health

# Get Projects
curl http://localhost:8000/api/projects

# Create Project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "location": "Mumbai"
  }'

# Upload & Parse PO (Bajaj)
curl -X POST "http://localhost:8000/api/po/upload?client_id=1&project_id=1" \
  -F "file=@/path/to/bajaj_po.xlsx"

# Create Vendor
curl -X POST http://localhost:8000/api/vendors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vendor Name",
    "email": "vendor@example.com"
  }'
```

---

## Deployment

### Docker Deployment

**Dockerfile** (Backend):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql://user:pass@db:5432/nexgen_finances
ENV ENVIRONMENT=production

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: nexgen_finances
      POSTGRES_USER: nexgen
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./Backend
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://nexgen:secure_password@db:5432/nexgen_finances
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    volumes:
      - ./Backend/logs:/app/logs
      - ./Backend/uploads:/app/uploads

  frontend:
    build: ./Frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api
```

**Deploy**:

```bash
docker-compose up -d
```

### Linux Systemd Deployment

**Backend Service** (`/etc/systemd/system/nexgen-backend.service`):

```ini
[Unit]
Description=Nexgen Finance Backend
After=network.target postgresql.service

[Service]
Type=notify
User=nexgen
WorkingDirectory=/opt/nexgen/backend
ExecStart=/opt/nexgen/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

**Enable & Start**:

```bash
sudo systemctl enable nexgen-backend
sudo systemctl start nexgen-backend
sudo systemctl status nexgen-backend
```

### Nginx Reverse Proxy

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://frontend;
    }
}
```

---

## Troubleshooting

### Backend Issues

#### Issue: Database Connection Failed

```
Error: could not translate host name "localhost" to address
```

**Solution**:
- Check PostgreSQL is running: `sudo service postgresql status`
- Verify `DATABASE_URL` in `.env`
- Test connection: `psql postgresql://user:pass@localhost/nexgen_finances`

#### Issue: Import Error - Module Not Found

```
ModuleNotFoundError: No module named 'app'
```

**Solution**:
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
- Check `PYTHONPATH` includes backend directory

#### Issue: Port 8000 Already in Use

```
OSError: [Errno 48] Address already in use
```

**Solution**:
```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Frontend Issues

#### Issue: CORS Error

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**:
- Check `VITE_API_BASE_URL` is correct
- Verify backend `CORS_ORIGINS` includes frontend URL
- Ensure both use matching protocol (http vs https)

#### Issue: API Timeout

```
Error: timeout of 30000ms exceeded
```

**Solution**:
- Check backend is running: `curl http://localhost:8000/api/health`
- Increase `VITE_API_TIMEOUT` in `.env`
- Check database connection
- Review backend logs

### Database Issues

#### Issue: Tables Not Created

```
ProgrammingError: relation "projects" does not exist
```

**Solution**:
```bash
# Check current schema
python check_schema_tables.py

# Apply migrations
python scripts/apply_schema.py

# Verify tables
psql -U nexgen -d nexgen_finances -c "\dt"
```

---

## Quick Start Checklist

### Backend

- [ ] Python 3.9+ installed
- [ ] PostgreSQL running
- [ ] Virtual environment created & activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with `DATABASE_URL`
- [ ] Database schema applied (`python scripts/apply_schema.py`)
- [ ] Backend started (`python run.py`)
- [ ] Health check passes (`curl http://localhost:8000/api/health`)

### Frontend

- [ ] Node.js 16+ installed
- [ ] Project created (`npm create vite@latest`)
- [ ] Dependencies installed (`npm install`)
- [ ] `.env` file created with `VITE_API_BASE_URL`
- [ ] Services created (api.ts, auth.ts, stores)
- [ ] Frontend started (`npm run dev`)
- [ ] Can access app (`http://localhost:5173`)

### Verification

- [ ] Backend routes: `http://localhost:8000/api/docs`
- [ ] Can call health check
- [ ] Can create project via API
- [ ] Can upload PO file
- [ ] Frontend calls backend API successfully

---

## Key API Endpoints Reference

| Category | Method | Endpoint | Purpose | Parser |
|----------|--------|----------|---------|--------|
| Health | GET | `/api/health` | System status | - |
| Clients | GET | `/api/clients` | Supported clients (Bajaj, Dava India) | - |
| Projects | GET | `/api/projects` | List all projects | - |
| | POST | `/api/projects` | Create project | - |
| PO | POST | `/api/po/upload?client_id=1` | Upload & parse Bajaj PO | `parse_bajaj_po()` |
| | POST | `/api/po/upload?client_id=2` | Upload & parse Dava India PO | `parse_proforma_invoice()` |
| Vendors | GET | `/api/vendors` | List vendors | - |
| | POST | `/api/vendors` | Create vendor | - |
| Payments | POST | `/api/po/{id}/payments` | Create payment | - |
| Billing | POST | `/api/projects/{id}/billing-po` | Create billing PO | - |
| | GET | `/api/projects/{id}/billing-pl-analysis` | P&L report | - |
| Files | POST | `/api/documents/upload` | Upload document | - |
| | GET | `/api/documents/project/{id}` | Get project documents | - |

---

## Support & Resources

- **API Docs**: http://localhost:8000/api/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/api/redoc
- **Frontend Guide**: `FRONTEND_INTEGRATION_COMPLETE.md`
- **Backend Guide**: `DEPLOYMENT_GUIDE.md`, `README_PRODUCTION.md`
- **Postman Collections**: `Postman_Collection_Backend.json`

---

**Version**: 1.0.0 | **Status**: ✅ Production Ready | **Last Updated**: February 17, 2026
