# Dashboard Integration Complete ✓

## Overview
Enhanced the backend API responses to include aggregation identifiers and project names for frontend dashboard display.

---

## 1. Upload Response Enhancements

### ParsedPOResponse Schema (Updated)
**Location:** `app/modules/file_uploads/schemas/requests.py`

**New Fields Added:**
- `project_name: Optional[str]` - Name of the project (optional)
- `project_id: Optional[int]` - ID of the resolved/created project
- `dashboard_info: Optional[Dict[str, Any]]` - Dashboard-specific metadata

**Example Response:**
```json
{
  "status": "SUCCESS",
  "file_id": "file_xyz789",
  "session_id": "sess_abc123",
  "client_id": 1,
  "client_name": "Bajaj",
  "parser_type": "po",
  "project_name": "Project A",
  "project_id": 1,
  "po_details": {
    "po_number": "PO-12345",
    "po_date": "2026-02-10"
  },
  "line_items": [...],
  "line_item_count": 5,
  "client_po_id": 112,
  "original_filename": "Bajaj_PO.xlsx",
  "upload_timestamp": "2026-02-10T10:30:00Z",
  "dashboard_info": {
    "project_name": "Project A",
    "po_number": "PO-12345",
    "client_po_id": 112,
    "line_items_count": 5
  }
}
```

### Upload Endpoints Updated:
1. **POST /api/po/upload** (`app/apis/client_po.py`)
   - Accepts: `project_name` (query parameter)
   - Returns: Updated ParsedPOResponse with project_name and dashboard_info

2. **POST /api/proforma-invoice/upload** (`app/apis/proforma_invoice.py`)
   - Accepts: `project_name` (form parameter)
   - Returns: Response with project_name and dashboard_info

---

## 2. Aggregation Response Enhancements

### PO Aggregation Endpoint Updated
**Location:** `app/apis/po_management.py`
**Endpoint:** `GET /api/po/aggregated/by-store`

**New Fields in Each Bundle:**
- `badge` - Visual indicator object for frontend:
  - `badge.type`: "bundled" | "single"
  - `badge.label`: Display text (e.g., "Bundle (2 POs)" or "Single PO")
  - `badge.color`: UI color ("blue" for bundled, "gray" for single)
  - `badge.icon`: UI icon name ("package" for bundled, "file" for single)

- `display_identifier` - Unique identifier:
  - For bundled: "BUNDLED-{bundle_id}"
  - For single: Store ID or PO number

**Example Aggregated Response:**
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
        "line_items": [...],
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
        "line_items": [...],
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
    "bundle_count": 2,
    "bundled_groups": 1,
    "single_po_groups": 1,
    "total_po_value": 100000,
    "total_line_items": 45,
    "summary": {
      "bundled_count": 1,
      "single_count": 1
    }
  }
}
```

---

## 3. Dashboard Display Guide

### Upload Dashboard
When uploading a PO, the response now includes:
- `project_name` - Display in dashboard header
- `po_number` - From parsed data
- `line_items_count` - Consolidated in dashboard_info
- All data in convenient `dashboard_info` object

**Frontend Example:**
```
Project: Project A
PO Number: PO-12345
Line Items: 5
Status: Successfully uploaded
```

### Aggregation Dashboard
When fetching aggregated POs:
- Each bundle shows `badge` with:
  - Colored badge (blue for bundled, gray for single)
  - Icon indicator (package vs file)
  - Label text ("Bundle (2 POs)" vs "Single PO")
- `display_identifier` for grouping/filtering
- Individual PO IDs in `po_ids` array
- Bundling metadata in `bundling_note`

**Frontend Example - Bundled View:**
```
┌─────────────────────────────────────────┐
│ 🔵 Bundle (2 POs) - BUNDLED-1           │
│ Store: STORE-123                        │
│ POs: PO-001, PO-002                     │
│ Total Value: ₹75,000                    │
│ Line Items: 12                          │
│ Note: contains 2 POs: PO-001, PO-002    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 📄 Single PO - STORE-456                │
│ Store: STORE-456                        │
│ PO: PO-005                              │
│ Total Value: ₹25,000                    │
│ Line Items: 8                           │
└─────────────────────────────────────────┘
```

---

## 4. Data Flow for Dashboard

### Upload Flow:
```
User uploads PO with project_name parameter
        ↓
Backend parses file
        ↓
Backend resolves/creates project
        ↓
Backend inserts to database
        ↓
Response includes:
  - project_name ✓
  - project_id ✓
  - po_number ✓
  - dashboard_info with all summary data ✓
        ↓
Frontend displays with project context
```

### Aggregation Flow:
```
Frontend requests: GET /api/po/aggregated/by-store?client_id=1
        ↓
Backend fetches POs grouped by store_id
        ↓
Backend adds badge and display_identifier to each bundle
        ↓
Response includes:
  - badge.type, badge.label, badge.color, badge.icon ✓
  - display_identifier ✓
  - is_bundled flag ✓
  - bundling_note ✓
  - po_ids array ✓
        ↓
Frontend displays bundled POs with visual indicators
```

---

## 5. Implementation Details

### Files Modified:

1. **app/modules/file_uploads/schemas/requests.py**
   - Added `project_name` field to ParsedPOResponse
   - Added `project_id` field to ParsedPOResponse
   - Added `dashboard_info` field to ParsedPOResponse

2. **app/apis/client_po.py**
   - Updated response to include project_name and project_id
   - Added dashboard_info population in response

3. **app/apis/proforma_invoice.py** (Already updated in previous phase)
   - Returns project_name and project_id
   - Includes dashboard_info in response

4. **app/apis/po_management.py**
   - Enhanced aggregation endpoint with badge structure
   - Added display_identifier for each bundle
   - Provides frontend-ready visual indicators

### Badge Structure for Frontend:
```python
{
  "type": "bundled|single",
  "label": "Bundle (N POs)|Single PO",
  "color": "blue|gray",
  "icon": "package|file"
}
```

---

## 6. Testing

✅ ParsedPOResponse schema accepts all new fields
✅ Badge structure properly formatted for UI components
✅ Display identifiers uniquely identify bundles
✅ Project name flows through upload responses
✅ Aggregation response includes all badge metadata

---

## 7. Frontend Integration Ready

**Ready to Implement:**
- Display project_name in upload confirmation
- Show badge indicators for bundled vs single POs
- Use display_identifier for grouping/filtering
- Display po_ids array for expanded view
- Show bundling_note for user context
- Color-code UI elements based on badge.color
- Use badge.icon for list item indicators

---

## Summary

✅ **Upload Responses**: Now include project_name and dashboard_info
✅ **Aggregation Responses**: Now include badge and display_identifier
✅ **Schema Validation**: All new fields validated with Pydantic
✅ **Frontend Ready**: All necessary metadata for dashboard display included

The backend is now fully equipped to provide the frontend with:
1. Project context for uploaded POs
2. Visual indicators for aggregated/bundled POs
3. Aggregation metadata for display and filtering
