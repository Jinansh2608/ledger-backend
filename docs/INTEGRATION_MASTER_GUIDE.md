# Master Integration Guide - Backend API Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NEXGEN FINANCES BACKEND                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐│
│   │  File Uploads    │  │    Projects      │  │     Billing PO   ││
│   │  - Sessions      │  │  - Create        │  │  - Parse client  ││
│   │  - Auto Parse    │  │  - Track expenses│  │  - Link payments ││
│   │  - Compression   │  │  - Budget track  │  │  - Generate tax  ││
│   └──────────────────┘  └──────────────────┘  └──────────────────┘│
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐│
│   │    Vendors       │  │  Vendor Orders   │  │    Payments      ││
│   │  - Create        │  │  - Create PO     │  │  - Record payment││
│   │  - Profile       │  │  - Track status  │  │  - Reconcile     ││
│   │  - Payment terms │  │  - 3-way match   │  │  - Batch process ││
│   └──────────────────┘  └──────────────────┘  └──────────────────┘│
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐                       │
│   │   Documents      │  │   Clients        │                       │
│   │  - Store files   │  │  - Bajaj         │                       │
│   │  - Index         │  │  - Dava India    │                       │
│   │  - Search        │  │  - PO tracking   │                       │
│   └──────────────────┘  └──────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
    PostgreSQL Database (Finances Schema)
```

---

## Quick Integration Checklist

### Phase 1: Foundation
- [ ] Setup PostgreSQL database with `Finances` schema
- [ ] Create required tables (vendor, vendor_order, vendor_payment)
- [ ] Configure connection pool (20-40 connections)
- [ ] Run health check endpoint

### Phase 2: Core Workflows
- [ ] Implement vendor management (create, update, list)
- [ ] Implement PO creation and tracking
- [ ] Implement payment recording
- [ ] Setup three-way matching

### Phase 3: Advanced Features
- [ ] Setup file upload sessions
- [ ] Configure auto-parsing for Bajaj POsOF
- [ ] Setup project tracking
- [ ] Implement document management

### Phase 4: Reporting & Analytics
- [ ] Generate vendor performance reports
- [ ] Budget tracking dashboards
- [ ] Payment aging reports
- [ ] PO fulfillment reports

---

## API Base Configuration

```
Base URL: http://localhost:8000
API Prefix: /api
Version: 1.0

Common Headers:
{
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Authorization": "Bearer {token}" (if auth required)
}
```

---

## Common Workflows

### Workflow 1: Complete PO Lifecycle
```
1. Create Vendor
   POST /api/vendors

2. Create Purchase Order
   POST /api/vendor-orders

3. Record Delivery
   POST /api/vendor-orders/{order_id}/delivery

4. Link Invoice
   POST /api/vendor-orders/{order_id}/invoice

5. Create Payment
   POST /api/payments

6. Reconcile
   GET /api/payments/summary/by-vendor
```

### Workflow 2: Client Billing with Auto-Parse
```
1. Create Upload Session
   POST /api/uploads/session (client_id=1 for Bajaj)

2. Upload PO File
   POST /api/uploads/session/{session_id}/files
   (auto_parse=true)

3. System Auto-Parses:
   - Extracts PO number, vendor, amount
   - Creates billing_po record
   - Links to vendor

4. Record Client Payment
   POST /api/billing/pos/{po_id}/payments

5. Generate Invoice
   POST /api/billing/pos/{po_id}/invoice
```

### Workflow 3: Project Budget Tracking
```
1. Create Project
   POST /api/projects (budget=5000000)

2. Link Vendors & POs
   POST /api/projects/{project_id}/vendors
   POST /api/projects/{project_id}/pos

3. Monitor Budget
   GET /api/projects/{project_id}/summary
   (tracks: budget_utilization_percent)

4. Generate Report
   GET /api/projects/{project_id}/summary
```

### Workflow 4: Document Management
```
1. Upload Documents
   POST /api/documents/upload

2. Link to Items
   POST /api/documents/{doc_id}/link

3. Search
   POST /api/documents/search

4. Download
   GET /api/documents/{doc_id}/download
```

---

## Database Schema Overview

### Core Tables

**vendor**
- Stores supplier information
- Fields: id, name, email, phone, gstin, payment_terms, status
- Key Index: gstin (unique), status

**vendor_order**
- Purchase orders from vendors
- Fields: id, vendor_id, po_number, amount, status
- Key Index: vendor_id, po_number (unique)

**vendor_payment**
- Payments to vendors
- Fields: id, vendor_id, vendor_order_id, amount, payment_date, status
- Key Index: vendor_id, status, payment_date

**client_po (billing_po)**
- Client purchase orders (auto-parsed)
- Fields: id, client_id, po_number, vendor_id, total, status
- Key Index: client_id, po_number (unique)

**upload_session**
- File upload sessions
- Fields: session_id, client_id, metadata, ttl_hours, status

**upload_file**
- Files within sessions
- Fields: id, session_id, po_number, file_size, mime_type, status

**document**
- Document management
- Fields: id, filename, document_type, project_id, vendor_id, po_id

**project**
- Project portfolio
- Fields: id, name, status, budget, department, owner

---

## Error Handling Standards

All error responses follow this format:

```json
{
  "status": "ERROR",
  "error_code": "SPECIFIC_ERROR_CODE",
  "message": "Human readable message",
  "details": {
    "field": "fieldname",
    "issue": "specific issue"
  }
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict (duplicate, etc.)
- `413` - Payload Too Large
- `500` - Server Error

### Error Codes by Module
- **VENDOR**: VENDOR_NOT_FOUND, INVALID_GSTIN, DUPLICATE_GSTIN
- **PO**: DUPLICATE_PO_NUMBER, VENDOR_NOT_FOUND, INVALID_AMOUNT
- **PAYMENT**: INSUFFICIENT_FUNDS, DUPLICATE_PAYMENT, INVALID_AMOUNT
- **FILE**: FILE_TOO_LARGE, UNSUPPORTED_FORMAT, SESSION_EXPIRED
- **PROJECT**: DUPLICATE_PROJECT_NAME, INVALID_DATE_RANGE

---

## Authentication & Authorization

Currently: No authentication required (development mode)

For Production:
```
POST /api/auth/login
{
  "username": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 3600
}

Use in headers:
Authorization: Bearer {access_token}
```

---

## Rate Limiting

Expected rate limits (production):
- API requests: 1000 per minute per user
- File uploads: 100 MB per day per user
- Batch operations: 100 items per request

---

## Data Pagination

All list endpoints support pagination:

```
GET /api/endpoint?limit=10&offset=0

Response:
{
  "data": [...],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

Default: limit=50, max=100

---

## Key Metrics by Module

### Vendors
- Total vendors
- Vendor by status
- Average payment terms
- Payment on-time %

### Purchase Orders
- Total POs by status
- Average PO value
- Delivery on-time %
- Invoice accuracy %

### Payments
- Total paid vs pending
- Payment completion %
- Average payment days
- Budget variance %

### Projects
- Budget utilization %
- Timeline progress %
- Vendor count
- Document count

---

## Performance Recommendations

### Database
- Connection pool: 20-40 connections
- Query timeout: 30 seconds
- Index all foreign keys
- Archive data older than 2 years
- Batch inserts for > 100 records

### Caching
- Cache vendor list (5 minute TTL)
- Cache project summaries (10 minute TTL)
- Cache vendor payment summary (15 minute TTL)

### File Storage
- Max file size: 50 MB
- Auto-compression for text files
- CDN for document delivery
- S3/Azure Blob for production

---

## Security Best Practices

1. **Authentication**
   - Use JWT tokens (production)
   - Set token expiry to 1 hour
   - Refresh tokens for long sessions

2. **Authorization**
   - Implement role-based access control (RBAC)
   - Vendor data: vendor-specific access
   - Project data: project-team access
   - Finance data: finance-team only

3. **Data Protection**
   - Encrypt sensitive documents
   - Use HTTPS (production)
   - Implement audit logging
   - Secure password hashing

4. **API Security**
   - Use HTTPS only (production)
   - Validate all inputs
   - Sanitize outputs
   - Implement rate limiting
   - CORS restriction

---

## Testing Strategy

### Unit Tests
- Endpoint validation
- Business logic
- Error handling

### Integration Tests
- Complete workflows
- Database interactions
- File operations

### Performance Tests
- Load testing (1000 concurrent users)
- Throughput testing (requests/second)
- Database query optimization

### Sample Test Data
See individual module guides for data models

---

## Deployment Considerations

### Environment Variables
```
DATABASE_URL=postgresql://user:pass@localhost/finances
DEBUG=false
ALLOWED_ORIGINS=https://frontend.example.com
MAX_FILE_SIZE=52428800
JWT_SECRET=your_jwt_secret
```

### Docker Deployment
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
- 2-3 replicas for high availability
- Health check endpoint: `/health`
- Resource limits: CPU 1000m, Memory 1GB

---

## Monitoring & Alerts

### Key Metrics to Monitor
- API response time (target: <200ms)
- Database query time (target: <100ms)
- File upload success rate (target: >99%)
- Payment processing success rate (target: 100%)
- Disk space usage (alert: >80%)

### Alert Thresholds
- Response time > 500ms: Warning
- Database error rate > 1%: Critical
- File upload failure rate > 5%: Critical
- Disk space > 90%: Critical

---

## Support & Maintenance

### Backup Strategy
- Daily database backups
- Weekly full backups
- Monthly archive retention
- Test restore quarterly

### Maintenance Windows
- Non-critical updates: Anytime
- Database migrations: Weekly (scheduled)
- Major updates: Monthly (planned)

### Health Check
```
GET /api/health
Response: { "status": "OK" }

GET /api/health/database
Response: { "status": "OK", "response_time_ms": 45 }
```

---

## Integration Guides Available

1. **[INTEGRATION_FILE_UPLOAD.md](INTEGRATION_FILE_UPLOAD.md)** - File upload, sessions, auto-parsing
2. **[INTEGRATION_VENDORS.md](INTEGRATION_VENDORS.md)** - Vendor management
3. **[INTEGRATION_PAYMENTS.md](INTEGRATION_PAYMENTS.md)** - Payment processing
4. **[INTEGRATION_VENDOR_ORDERS.md](INTEGRATION_VENDOR_ORDERS.md)** - PO management
5. **[INTEGRATION_PROJECTS.md](INTEGRATION_PROJECTS.md)** - Project tracking
6. **[INTEGRATION_BILLING_PO.md](INTEGRATION_BILLING_PO.md)** - Client billing
7. **[INTEGRATION_DOCUMENTS.md](INTEGRATION_DOCUMENTS.md)** - Document management

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-17 | Initial release with all core modules |
| | | File upload with auto-parsing |
| | | Vendor and PO management |
| | | Payment processing |
| | | Project tracking |
| | | Billing and invoicing |
| | | Document management |

---

## Getting Started Examples

### Python
```python
import requests
BASE_URL = "http://localhost:8000"

# Health check
health = requests.get(f"{BASE_URL}/api/health").json()

# Create vendor
vendor = requests.post(f"{BASE_URL}/api/vendors", json={
    "name": "Supplier Ltd",
    "email": "info@supplier.com",
    "gstin": "27AABFU6954R1Z1"
}).json()

# Create PO
po = requests.post(f"{BASE_URL}/api/vendor-orders", json={
    "vendor_id": vendor["id"],
    "po_number": f"PO-{datetime.now().strftime('%Y%m%d')}-001",
    "amount": 100000,
    "status": "PENDING_CONFIRMATION"
}).json()
```

### JavaScript
```javascript
const BASE_URL = "http://localhost:8000";

// Health check
const health = await fetch(`${BASE_URL}/api/health`).then(r => r.json());

// Create vendor
const vendor = await fetch(`${BASE_URL}/api/vendors`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "Supplier Ltd",
    email: "info@supplier.com",
    gstin: "27AABFU6954R1Z1"
  })
}).then(r => r.json());
```

---

## FAQ

**Q: How do I setup the backend?**
A: See the README.md in the root directory for complete setup instructions.

**Q: How do I test the API?**
A: Use the Postman collection provided: `Postman_Complete_Backend_Collection.json`

**Q: How do file uploads work?**
A: See [INTEGRATION_FILE_UPLOAD.md](INTEGRATION_FILE_UPLOAD.md) for complete details.

**Q: How do I enable auto-parsing?**
A: Pass `auto_parse=true` when uploading files to a session with valid client_id.

**Q: How do I track project budgets?**
A: Create a project, set budget, link POs, then use GET /api/projects/{id}/summary

**Q: How do I process bulk payments?**
A: Use POST /api/payments/bulk-process with array of payment IDs.

---

## Contact & Support

For issues, questions, or contributions:
- Email: support@nexgenfinances.com
- Documentation: See individual module guides
- Postman Collection: Built-in examples available

