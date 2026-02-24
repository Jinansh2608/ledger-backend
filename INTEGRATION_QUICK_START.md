# Frontend Integration - Quick Reference Card

**Status:** ✅ Production Ready | **Routes Working:** 70/73 (96%) | **Date:** Feb 17, 2026

---

## 📋 For First-Time Setup

```bash
# 1. Start Backend
python run.py

# 2. Check Health
curl http://localhost:8000/api/health

# 3. Configure Frontend API Client
const API_BASE = 'http://localhost:8000';
const API_PREFIX = '/api';
const UPLOAD_PREFIX = '/uploads';
```

---

## 🚀 Core Workflows at a Glance

### 1. Project Management
```
Create Project → Get Financial Summary → Track Spending → Generate Reports
```

### 2. Purchase Orders
```
Create PO in Project → Add Line Items → Track Receipt → Record Payment
```

### 3. Vendor Management
```
Create Vendor → Create Orders → Track Payments → Generate Summary
```

### 4. File Uploads
```
Create Session → Upload File → Auto-Parse → Download → Delete Session
```

---

## 🔌 Essential Endpoints Quick Reference

| Operation | Endpoint | Method | Status |
|-----------|----------|--------|--------|
| **Health Check** | `/api/health` | GET | ✅ |
| **Create Project** | `/api/projects` | POST | ✅ |
| **List Projects** | `/api/projects` | GET | ✅ |
| **Get Project Finances** | `/api/projects/{id}/financial-summary` | GET | ✅ |
| **Create PO** | `/api/projects/{id}/po?client_id={cid}` | POST | ✅ |
| **List POs** | `/api/projects/{id}/po` | GET | ✅ |
| **Create Vendor** | `/api/vendors` | POST | ✅ |
| **List Vendors** | `/api/vendors` | GET | ✅ |
| **Create Vendor Order** | `/api/projects/{id}/vendor-orders` | POST | ✅ |
| **Upload Session** | `/api/uploads/session` | POST | ✅ |
| **Upload File** | `/api/uploads/session/{id}/files` | POST | ✅ |

---

## 📌 Common Patterns

### API Call Template
```javascript
try {
  const response = await fetch('http://localhost:8000/api/endpoint', {
    method: 'GET|POST|PUT|DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
} catch (error) {
  console.error('API Error:', error);
}
```

### File Upload Template
```javascript
const formData = new FormData();
formData.append('file', file);

const response = await fetch(
  'http://localhost:8000/api/uploads/session/{sessionId}/files',
  {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  }
);
```

---

## ⚠️ Known Limitations (3 Routes)

| Missing Route | Use Instead | Why |
|--------------|-------------|-----|
| `POST /api/po` | `POST /api/projects/{id}/po?client_id={cid}` | POs must be project-scoped |
| `POST /api/vendors/{id}/payments` | `POST /api/vendor-orders/{id}/payments` | Payments tracked at order level |
| `POST /uploads/session/{id}/download-all` | Download files individually | Bulk ZIP not implemented |

**Workaround for bulk download:**
```javascript
// Option 1: Download individually
const files = await api.get(`/api/uploads/session/${sessionId}/files`);
for (const file of files) {
  window.location = `/api/uploads/session/${sessionId}/files/${file.id}/download`;
}
```

---

## 🔒 Authentication

```javascript
// Login
POST /api/auth/login
{ "email": "user@company.com", "password": "password" }
→ Returns: { "token": "...", "user": {...} }

// Store token
localStorage.setItem('authToken', token);

// Include in requests
headers: { 'Authorization': `Bearer ${token}` }

// Get current user
GET /api/auth/me
```

---

## 📊 Data Flow Examples

### Example 1: Create Complete Project with PO
```javascript
// 1. Create project
const proj = await POST /api/projects 
  { name: "Project", client_id: "C1" }

// 2. Create vendor
const vendor = await POST /api/vendors 
  { name: "Vendor", email: "v@company.com" }

// 3. Create PO
const po = await POST /api/projects/{proj.id}/po?client_id=C1
  { vendor_id: vendor.id, po_number: "PO001" }

// 4. Add line item
await POST /api/po/{po.id}/line-items
  { item_code: "I1", quantity: 1, rate: 5000 }

// 5. Record payment
await POST /api/po/{po.id}/payments
  { amount: 5000, date: "2024-02-17" }
```

### Example 2: File Upload & Processing
```javascript
// 1. Create session
const session = await POST /api/uploads/session {}

// 2. Upload file
await POST /api/uploads/session/{session.id}/files
  { file: <binary> }

// 3. Get parsed data
const files = await GET /api/uploads/session/{session.id}/files

// 4. Download if needed
window.location = `/api/uploads/session/{session.id}/files/{file.id}/download`

// 5. Cleanup
await DELETE /api/uploads/session/{session.id}
```

---

## 🛠️ HTTP Status Codes

| Code | Meaning | Handle With |
|------|---------|-------------|
| 200 | Success | Use returned data |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Check request format/validation |
| 401 | Unauthorized | Redirect to login, refresh token |
| 404 | Not Found | Check endpoint path, resource ID |
| 422 | Validation Error | Show field errors to user |
| 500 | Server Error | Retry or contact support |

---

## 🐛 Quick Debugging

### Check Backend Health
```javascript
fetch('http://localhost:8000/api/health/')
  .then(r => r.json())
  .then(console.log)
  .catch(e => console.error('Backend down:', e))
```

### Verify Authentication
```javascript
const token = localStorage.getItem('authToken');
console.log('Token exists:', !!token);

fetch('http://localhost:8000/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(user => console.log('Current user:', user))
```

### Test API Call
```javascript
// Template to test any endpoint
async function testEndpoint(method, path, data = null) {
  const url = `http://localhost:8000${path}`;
  console.log(`${method} ${url}`);
  
  const response = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`
    },
    body: data ? JSON.stringify(data) : null
  });

  console.log('Status:', response.status);
  const json = await response.json();
  console.log('Response:', json);
  return json;
}

// Usage
testEndpoint('GET', '/api/projects');
testEndpoint('GET', '/api/vendors?limit=5');
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `COMPLETE_FRONTEND_INTEGRATION_GUIDE.md` | **👈 START HERE** - Full integration guide with examples |
| `BACKEND_ROUTES_STATUS_REPORT.md` | Status of all 73 routes, which exist/missing |
| `FRONTEND_API_WORKING_ROUTES.md` | Copy-paste ready endpoint list for frontend |
| `INTEGRATION_*.md` | Module-specific guides (Projects, Vendors, etc.) |

---

## ✅ Pre-Launch Checklist

- [ ] Backend running: `python run.py`
- [ ] Backend healthy: `curl http://localhost:8000/api/health`
- [ ] API base URL configured in frontend
- [ ] Authentication flow implemented
- [ ] Error handling added to API calls
- [ ] CORS configured (if needed)
- [ ] All main workflows tested
- [ ] File uploads tested
- [ ] Payment tracking tested
- [ ] Financial reports tested

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| 404 on `/api/po` POST | Use `/api/projects/{id}/po?client_id={cid}` instead |
| 401 Unauthorized | Add `Authorization: Bearer {token}` header |
| CORS blocked | Backend needs CORS middleware enabled |
| File upload hangs | Check file size, max request timeout |
| Empty response data | Check API returns `200` not `204` |
| Validation errors `422` | Check field types (string/number/date) |

---

## 📞 Quick Support

**Backend won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill process if needed: kill -9 <PID>
# Then restart: python run.py
```

**Need to reset database:**
```bash
# Check current schema
python check_schema.py
# Run migrations if needed
python apply_migrations.py
```

**API returning errors:**
- Check logs in terminal where backend is running
- Verify database connection: See `check_db_data.py`
- Check for database locks: See `cleanup_db.py`

---

## 🎯 Integration Checklist by Component

### Projects
- [ ] Create projects
- [ ] List/filter projects
- [ ] Get financial summary
- [ ] Get billing summary
- [ ] Get P&L analysis

### Purchase Orders
- [ ] Create POs in project context
- [ ] Add line items
- [ ] Track payments
- [ ] Update statuses

### Vendors
- [ ] Create vendors
- [ ] List vendors with filters
- [ ] Create vendor orders
- [ ] Track vendor payments

### File Management
- [ ] Create upload sessions
- [ ] Upload files
- [ ] List uploaded files
- [ ] Download files
- [ ] Delete files

### Reports
- [ ] Generate financial summaries
- [ ] Generate billing reports
- [ ] Export data

---

## 💡 Pro Tips

1. **Use Pagination**: For large lists, use `limit` and `offset` parameters
2. **Batch Operations**: Process multiple items in loops or with Promise.all
3. **Cache Responses**: Cache project/vendor lists for 5-10 seconds
4. **Error Recovery**: Implement retry logic with exponential backoff
5. **Monitor Performance**: Log API response times in production
6. **Validate Input**: Validate data before sending to backend
7. **Handle Timeouts**: Set reasonable timeout values (30-60 seconds)
8. **Track Requests**: Log all API calls during debugging

---

## 🔗 Quick Links to Full Guide

- **Need complete setup?** → See `COMPLETE_FRONTEND_INTEGRATION_GUIDE.md`
- **Need all endpoints?** → See `FRONTEND_API_WORKING_ROUTES.md`
- **Route not working?** → See `BACKEND_ROUTES_STATUS_REPORT.md`
- **Module specific help?** → See `INTEGRATION_*.md` files

---

**Last Updated:** February 17, 2026 | **Status:** Production Ready | **Version:** 1.0
