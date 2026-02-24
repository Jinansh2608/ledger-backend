# Projects Integration Guide

## Overview
Project management system for tracking and organizing purchase orders, files, and related activities. Projects serve as containers for coherent business initiatives.

## Architecture

```
Project Creation → Link Documents → Link Vendors → Track Expenses → Generate Reports
        ↓               ↓               ↓               ↓                 ↓
    Metadata      Files/POs       Supplier info    Budget vs Actual   Dashboards
    Status        Versions        Contact info     Timeline          Export data
    Timeline      Approvals       Terms            Milestones        Archive
```

---

## API Endpoints

### 1. Create Project
```http
POST /api/projects
Content-Type: application/json

{
  "name": "Q1 2026 Procurement",
  "description": "Quarterly procurement initiative",
  "status": "ACTIVE",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31",
  "budget": 5000000,
  "department": "Operations",
  "client_id": 1,
  "owner": "admin"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Q1 2026 Procurement",
  "description": "Quarterly procurement initiative",
  "status": "ACTIVE",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31",
  "budget": 5000000,
  "department": "Operations",
  "client_id": 1,
  "owner": "admin",
  "created_at": "2026-02-17T10:30:00",
  "updated_at": "2026-02-17T10:30:00"
}
```

---

### 2. Get Project by ID
```http
GET /api/projects/{project_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Q1 2026 Procurement",
  "description": "Quarterly procurement initiative",
  "status": "ACTIVE",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31",
  "budget": 5000000,
  "actual_spend": 2350000,
  "budget_utilization": 47,
  "document_count": 12,
  "vendor_count": 5,
  "po_count": 8,
  "created_at": "2026-02-17T10:30:00"
}
```

---

### 3. List Projects
```http
GET /api/projects?status=ACTIVE&client_id=1&limit=10&offset=0
```

**Query Parameters:**
- `status` - Filter by status (ACTIVE, ON_HOLD, COMPLETED, ARCHIVED)
- `client_id` - Filter by client
- `department` - Filter by department
- `date_from` - Filter from date
- `date_to` - Filter to date
- `limit` - Pagination limit (default: 50)
- `offset` - Pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Q1 2026 Procurement",
      "status": "ACTIVE",
      "budget": 5000000,
      "actual_spend": 2350000,
      "budget_utilization": 47
    }
  ],
  "total": 8,
  "limit": 10,
  "offset": 0
}
```

---

### 4. Update Project
```http
PUT /api/projects/{project_id}
Content-Type: application/json

{
  "name": "Q1 2026 Procurement - Updated",
  "status": "ON_HOLD",
  "budget": 5500000,
  "description": "Extended budget due to additional items"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Q1 2026 Procurement - Updated",
  "status": "ON_HOLD",
  "budget": 5500000,
  "updated_at": "2026-02-17T11:30:00"
}
```

---

### 5. Delete Project
```http
DELETE /api/projects/{project_id}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "message": "Project deleted successfully",
  "data": {"project_id": 1}
}
```

---

### 6. Get Project Summary
```http
GET /api/projects/{project_id}/summary
```

**Response:**
```json
{
  "project_id": 1,
  "name": "Q1 2026 Procurement",
  "status": "ACTIVE",
  "budget": 5000000,
  "actual_spend": 2350000,
  "budget_remaining": 2650000,
  "budget_utilization_percent": 47,
  "document_count": 12,
  "vendor_count": 5,
  "po_count": 8,
  "total_po_value": 2350000,
  "completed_po_count": 6,
  "pending_po_count": 2,
  "timeline": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31",
    "days_elapsed": 48,
    "days_remaining": 43,
    "completion_percent": 53
  }
}
```

---

### 7. Link PO to Project
```http
POST /api/projects/{project_id}/pos
Content-Type: application/json

{
  "po_ids": [5, 6, 7]
}
```

**Response:**
```json
{
  "project_id": 1,
  "linked_pos": 3,
  "total_linked_pos": 8
}
```

---

### 8. Link Vendor to Project
```http
POST /api/projects/{project_id}/vendors
Content-Type: application/json

{
  "vendor_ids": [42, 43, 44]
}
```

**Response:**
```json
{
  "project_id": 1,
  "linked_vendors": 3,
  "total_linked_vendors": 5
}
```

---

### 9. Get Project POs
```http
GET /api/projects/{project_id}/pos
```

**Response:**
```json
{
  "project_id": 1,
  "pos": [
    {
      "id": 5,
      "po_number": "PO-2026-001",
      "vendor_name": "Supplier Name",
      "amount": 500000,
      "status": "COMPLETED"
    }
  ],
  "total": 8,
  "total_value": 2350000
}
```

---

### 10. Get Project Vendors
```http
GET /api/projects/{project_id}/vendors
```

**Response:**
```json
{
  "project_id": 1,
  "vendors": [
    {
      "id": 42,
      "name": "Supplier Name",
      "email": "john@supplier.com",
      "po_count": 3,
      "total_value": 500000
    }
  ],
  "total": 5
}
```

---

## Database Schema

### project table
```sql
CREATE TABLE project (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  status VARCHAR(50),
  start_date DATE,
  end_date DATE,
  budget NUMERIC(15, 2),
  department VARCHAR(100),
  client_id BIGINT,
  owner VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_project_status (status),
  INDEX idx_project_client (client_id),
  INDEX idx_project_date (start_date)
);
```

### project_po table (linking table)
```sql
CREATE TABLE project_po (
  project_id BIGINT NOT NULL,
  po_id BIGINT NOT NULL,
  linked_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (project_id, po_id),
  FOREIGN KEY (project_id) REFERENCES project(id),
  FOREIGN KEY (po_id) REFERENCES vendor_order(id)
);
```

### project_vendor table (linking table)
```sql
CREATE TABLE project_vendor (
  project_id BIGINT NOT NULL,
  vendor_id BIGINT NOT NULL,
  linked_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (project_id, vendor_id),
  FOREIGN KEY (project_id) REFERENCES project(id),
  FOREIGN KEY (vendor_id) REFERENCES vendor(id)
);
```

---

## Project Status Workflow

```
ACTIVE
   ↓
ON_HOLD (if needed)
   ↓
COMPLETED
   ↓
ARCHIVED
```

**Status Definitions:**
- `ACTIVE` - Project is currently active
- `ON_HOLD` - Project is temporarily paused
- `COMPLETED` - Project has ended
- `ARCHIVED` - Project is archived and read-only

---

## Implementation Example

### Python
```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Create project
project_data = {
    "name": "Q1 2026 Procurement",
    "description": "Quarterly procurement initiative",
    "status": "ACTIVE",
    "start_date": "2026-01-01",
    "end_date": "2026-03-31",
    "budget": 5000000,
    "department": "Operations",
    "client_id": 1,
    "owner": "admin"
}

project_resp = requests.post(
    f"{BASE_URL}/api/projects",
    json=project_data
)
project = project_resp.json()
project_id = project["id"]

# 2. Link POs to project
link_pos_resp = requests.post(
    f"{BASE_URL}/api/projects/{project_id}/pos",
    json={"po_ids": [5, 6, 7]}
)

# 3. Link vendors to project
link_vendors_resp = requests.post(
    f"{BASE_URL}/api/projects/{project_id}/vendors",
    json={"vendor_ids": [42, 43, 44]}
)

# 4. Get project summary
summary_resp = requests.get(
    f"{BASE_URL}/api/projects/{project_id}/summary"
)
summary = summary_resp.json()
print(f"Budget Utilization: {summary['budget_utilization_percent']}%")
print(f"Pending POs: {summary['pending_po_count']}")

# 5. Get project POs
pos_resp = requests.get(
    f"{BASE_URL}/api/projects/{project_id}/pos"
)
pos = pos_resp.json()
print(f"Total PO Value: ₹{summary['total_po_value']}")

# 6. Get project vendors
vendors_resp = requests.get(
    f"{BASE_URL}/api/projects/{project_id}/vendors"
)
vendors = vendors_resp.json()["vendors"]
for vendor in vendors:
    print(f"{vendor['name']}: {vendor['po_count']} POs")

# 7. Update project status
update_resp = requests.put(
    f"{BASE_URL}/api/projects/{project_id}",
    json={"status": "COMPLETED"}
)
```

### JavaScript
```javascript
const BASE_URL = "http://localhost:8000";

// 1. Create project
async function createProject() {
  const response = await fetch(`${BASE_URL}/api/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: "Q1 2026 Procurement",
      description: "Quarterly procurement initiative",
      status: "ACTIVE",
      start_date: "2026-01-01",
      end_date: "2026-03-31",
      budget: 5000000,
      department: "Operations",
      client_id: 1,
      owner: "admin"
    })
  });
  return response.json();
}

// 2. Link POs to project
async function linkPOsToProject(projectId, poIds) {
  const response = await fetch(
    `${BASE_URL}/api/projects/${projectId}/pos`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ po_ids: poIds })
    }
  );
  return response.json();
}

// 3. Get project summary
async function getProjectSummary(projectId) {
  const response = await fetch(
    `${BASE_URL}/api/projects/${projectId}/summary`
  );
  const summary = await response.json();
  console.log(`Budget Utilization: ${summary.budget_utilization_percent}%`);
  return summary;
}

// 4. List all projects
async function listProjects() {
  const response = await fetch(
    `${BASE_URL}/api/projects?status=ACTIVE&limit=20`
  );
  const { data, total } = await response.json();
  console.log(`Total projects: ${total}`);
  data.forEach(p => {
    console.log(`${p.name}: ${p.budget_utilization}% utilized`);
  });
}
```

---

## Workflows

### Project Lifecycle
```
1. Define project requirements
2. Create project with budget
3. Identify vendors required
4. Create POs for vendors
5. Link POs to project
6. Track expenses vs budget
7. Monitor timeline
8. Complete project
9. Generate final report
10. Archive project
```

### Budget Tracking Workflow
```
1. Set project budget
2. For each PO created:
   - Deduct from available budget
   - Track actual spend
3. Generate budget reports
4. Alert if spending exceeds 80% of budget
5. Flag if spending exceeds budget
6. Report final variance
```

---

## Error Handling

**409 Conflict - Duplicate Project Name**
```json
{
  "status": "ERROR",
  "error_code": "DUPLICATE_PROJECT_NAME",
  "message": "Project with name 'Q1 2026 Procurement' already exists"
}
```

**400 Bad Request - End Date Before Start Date**
```json
{
  "status": "ERROR",
  "error_code": "INVALID_DATE_RANGE",
  "message": "End date must be after start date"
}
```

---

## Best Practices

1. **Project Planning**
   - Clear project scope and objectives
   - Realistic budget estimation
   - Defined timeline with milestones
   - Assigned owner and approvers

2. **Budget Management**
   - Set realistic budgets before procurement
   - Track spending continuously
   - Alert on budget thresholds (50%, 80%, 100%)
   - Maintain contingency reserves

3. **Vendor Management**
   - Link projects to relevant vendors
   - Track vendor performance by project
   - Maintain vendor diversity
   - Review vendor quality metrics

4. **Reporting**
   - Generate weekly budget reports
   - Track timeline progress
   - Monitor PO completion rates
   - Report variance analysis

5. **Documentation**
   - Link all relevant documents to project
   - Maintain approval trail
   - Store project specifications
   - Archive after completion

---

## Key Metrics

- **Budget Utilization %** = (Actual Spend / Budget) × 100
- **Timeline Progress %** = (Days Elapsed / Total Days) × 100
- **PO Completion Rate** = (Completed POs / Total POs) × 100
- **Vendor Performance** = On-time delivery % by vendor
- **Cost per PO** = Total Project Cost / Number of POs

