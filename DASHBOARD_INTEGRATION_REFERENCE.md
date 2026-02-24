# Dashboard Integration Quick Reference

## 🎯 Session Changes Summary

### What Changed?
✅ Upload responses now include **project_name** and **dashboard_info**
✅ Aggregated POs now show **visual badges** for bundled/single status
✅ All responses include **aggregation identifiers** for frontend display

---

## 📊 Dashboard Data Flow

### Upload Flow
```
User Uploads PO with project_name
       ↓
Backend Parses & Resolves Project
       ↓
Response includes:
  • project_name ✓ (for dashboard header)
  • project_id ✓ (for linking)
  • po_number ✓ (from parsed data)
  • dashboard_info ✓ (consolidated metadata)
       ↓
Frontend Displays Project Context
```

### Aggregation Flow
```
Frontend requests: GET /api/po/aggregated/by-store?client_id=1
       ↓
Backend Groups POs by Store
       ↓
Response includes:
  • badge (visual indicator)
  • display_identifier (for grouping)
  • is_bundled flag
  • po_ids array
       ↓
Frontend Shows Bundled/Single Indicators
```

---

## 🔌 API Endpoints

### 1. Upload PO Files

**POST /api/po/upload**
```bash
curl -X POST "http://localhost:8000/api/po/upload?client_id=1&project_name=Project%20A" \
  -F "file=@po.xlsx"
```

**Response:**
```json
{
  "status": "SUCCESS",
  "project_name": "Project A",
  "project_id": 1,
  "po_number": "PO-12345",
  "client_po_id": 112,
  "dashboard_info": {
    "project_name": "Project A",
    "po_number": "PO-12345",
    "client_po_id": 112,
    "line_items_count": 5
  }
}
```

**POST /api/proforma-invoice/upload**
```bash
curl -X POST "http://localhost:8000/api/proforma-invoice/upload" \
  -F "file=@pi.xlsx" \
  -F "client_id=1" \
  -F "project_name=Project A"
```

**Response:** Same structure as /api/po/upload

---

### 2. Get Aggregated POs

**GET /api/po/aggregated/by-store?client_id=1**

**Response:**
```json
{
  "status": "SUCCESS",
  "data": {
    "bundles": [
      {
        "bundle_id": 1,
        "store_id": "STORE-123",
        "is_bundled": true,
        "po_ids": ["PO-001", "PO-002"],
        "bundling_note": "contains 2 POs: PO-001, PO-002",
        "total_po_value": 75000,
        "badge": {
          "type": "bundled",
          "label": "Bundle (2 POs)",
          "color": "blue",
          "icon": "package"
        },
        "display_identifier": "BUNDLED-1"
      },
      {
        "bundle_id": 2,
        "store_id": "STORE-456",
        "is_bundled": false,
        "po_ids": ["PO-005"],
        "total_po_value": 25000,
        "badge": {
          "type": "single",
          "label": "Single PO",
          "color": "gray",
          "icon": "file"
        },
        "display_identifier": "STORE-456"
      }
    ],
    "summary": {
      "bundled_count": 1,
      "single_count": 1
    }
  }
}
```

---

## 🎨 Frontend Implementation Examples

### Upload Confirmation Display
```typescript
// Display after file upload
const response = await uploadPO(file, projectName);

<UploadConfirmation>
  <ProjectName>{response.project_name}</ProjectName>
  <PONumber>{response.dashboard_info.po_number}</PONumber>
  <LineItemsCount>{response.dashboard_info.line_items_count}</LineItemsCount>
  <Status>Successfully uploaded</Status>
</UploadConfirmation>
```

### Aggregated POs List Display
```typescript
// Display aggregated POs with badges
const bundles = await getAggregatedPOs(clientId);

{bundles.map(bundle => (
  <POBundle key={bundle.display_identifier}>
    <Badge 
      color={bundle.badge.color}
      icon={bundle.badge.icon}
    >
      {bundle.badge.label}
    </Badge>
    <PO_ID>{bundle.display_identifier}</PO_ID>
    <Store>{bundle.store_id}</Store>
    <POList>
      {bundle.po_ids.map(po => <li key={po}>{po}</li>)}
    </POList>
    <TotalValue>₹{bundle.total_po_value}</TotalValue>
    {bundle.bundling_note && (
      <Note>{bundle.bundling_note}</Note>
    )}
  </POBundle>
))}
```

---

## 📋 Response Field Mapping

### Upload Response Fields for Dashboard

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `project_name` | string | Display project context | "Project A" |
| `project_id` | integer | Link to project record | 1 |
| `po_number` | string | Display PO identifier | "PO-12345" |
| `client_po_id` | integer | Link to database record | 112 |
| `dashboard_info.project_name` | string | Consolidated project reference | "Project A" |
| `dashboard_info.po_number` | string | Consolidated PO reference | "PO-12345" |
| `dashboard_info.line_items_count` | integer | Summary count | 5 |

### Aggregation Response Fields for Dashboard

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `badge.type` | enum | Visual category | "bundled" / "single" |
| `badge.label` | string | User-friendly text | "Bundle (2 POs)" |
| `badge.color` | string | UI color hint | "blue" / "gray" |
| `badge.icon` | string | Icon identifier | "package" / "file" |
| `display_identifier` | string | Unique ID for UI | "BUNDLED-1" |
| `is_bundled` | boolean | Aggregation flag | true / false |
| `po_ids` | array | PO list | ["PO-001", "PO-002"] |
| `bundling_note` | string | Metadata text | "contains 2 POs: ..." |

---

## 🚀 Implementation Checklist

### Backend (Already Done ✓)
- ✅ Added `project_name` parameter to upload endpoints
- ✅ Added `project_id` lookup/creation logic
- ✅ Updated ParsedPOResponse schema with new fields
- ✅ Added `dashboard_info` object to responses
- ✅ Added badge structure to aggregation response
- ✅ Added `display_identifier` to bundles
- ✅ All responses properly validated with Pydantic

### Frontend (Ready to Implement)
- Display project_name in upload confirmation
- Show project selector/creator in upload form
- Render badge components for bundle status
- Use badge.color for UI styling
- Use badge.icon for list indicators
- Display bundling_note for user context
- Implement grouping by display_identifier
- Show expanded po_ids on demand

---

## 📁 Files Modified

1. **app/modules/file_uploads/schemas/requests.py**
   - Updated `ParsedPOResponse` schema
   - Added: `project_name`, `project_id`, `dashboard_info`

2. **app/apis/client_po.py**
   - Update response population
   - Include project_name and dashboard_info

3. **app/apis/proforma_invoice.py** 
   - Include project_name and dashboard_info in response

4. **app/apis/po_management.py**
   - Add badge and display_identifier to aggregation endpoint
   - Enhance bundle response structure

---

## 🧪 Testing

### Test Upload Response
```bash
curl -X POST "http://localhost:8000/api/po/upload?client_id=1&project_name=Test%20Project" \
  -F "file=@sample.xlsx" | jq '.dashboard_info'
```

Expected output:
```json
{
  "project_name": "Test Project",
  "po_number": "PO-001",
  "client_po_id": 112,
  "line_items_count": 5
}
```

### Test Aggregation Response
```bash
curl "http://localhost:8000/api/po/aggregated/by-store?client_id=1" | jq '.data.bundles[0].badge'
```

Expected output:
```json
{
  "type": "bundled",
  "label": "Bundle (2 POs)",
  "color": "blue",
  "icon": "package"
}
```

---

## 📝 Documentation

Complete integration guide: [DASHBOARD_INTEGRATION_COMPLETE.md](./docs/DASHBOARD_INTEGRATION_COMPLETE.md)

---

## ✨ Summary

Your backend now provides:
1. **Project Context** - project_name and project_id in all upload responses
2. **Dashboard Metadata** - dashboard_info object with key summary fields
3. **Aggregation Badges** - Visual indicators (bundled vs single) with colors and icons
4. **Display Identifiers** - Unique IDs for grouping and filtering (e.g., "BUNDLED-1")
5. **Full Metadata** - All necessary data for comprehensive frontend dashboard display

Ready for frontend integration! 🎉
