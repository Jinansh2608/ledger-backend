#!/usr/bin/env python3
"""
POSTMAN TEST GUIDE - Critical Routes 
====================================

Minimal essential tests for backend API
"""

GUIDE = """
╔════════════════════════════════════════════════════════════════════╗
║          POSTMAN COLLECTION - CRITICAL ROUTES GUIDE               ║
╚════════════════════════════════════════════════════════════════════╝

📋 COLLECTION: Postman_Collection_Critical_Routes.json

🎯 ROUTES INCLUDED (7 Essential):

   SESSION MANAGEMENT (3 routes):
   ├─ POST   /api/uploads/session
   ├─ GET    /api/uploads/session/{session_id}
   └─ DELETE /api/uploads/session/{session_id}
   
   FILE UPLOAD & PARSING (2 routes):
   ├─ POST /api/uploads/session/{session_id}/files
   └─ POST /api/uploads/po/upload ⭐ PRIMARY
   
   FILE MANAGEMENT (3 routes):
   ├─ GET    /api/uploads/session/{session_id}/files
   ├─ GET    /api/uploads/session/{session_id}/files/{file_id}/download
   └─ DELETE /api/uploads/session/{session_id}/files/{file_id}
   
   BULK OPERATIONS (1 route):
   └─ POST /api/bajaj-po/bulk


📍 TEST WORKFLOW:

Step 1: Create Session
─────────────────────
   Request: POST /api/uploads/session
   Body:
   {
     "client_id": 1,
     "metadata": {
       "project_id": 3,
       "upload_type": "po"
     },
     "ttl_hours": 24
   }
   
   Response:
   - Save "session_id" to use in next requests
   - Expected status: 200 OK
   
   ➜ Copy session_id from response → Use {{session_id}} variable


Step 2: Upload File to Session (Method 1)
──────────────────────────────────────────
   Request: POST /api/uploads/session/{session_id}/files
   
   Form-data:
   - file: (select Excel file)
   - uploaded_by: admin@nexgen.com
   - po_number: PO-2024-001
   - auto_parse: true
   
   Response:
   - file_id
   - parse_status (SUCCESS, FAILED, SKIPPED)
   - parse_error (if any)
   - po_id (if parsed successfully)
   - Expected status: 200 OK


OR Direct Upload (Method 2 - RECOMMENDED) ⭐
──────────────────────────────────────────
   Request: POST /api/uploads/po/upload
   Query params:
   - client_id=1
   - project_id=3
   
   Form-data:
   - file: (select Excel file)
   - uploaded_by: admin@nexgen.com
   - auto_save: true
   
   Response:
   - Parsed PO data
   - line_items (extracted from Excel)
   - client_po_id (database ID)
   - Expected status: 200 OK
   
   ➜ This is the PRIMARY endpoint for PO uploads!


Step 3: List Files in Session
──────────────────────────────
   Request: GET /api/uploads/session/{session_id}/files
   Query params:
   - skip: 0
   - limit: 50
   
   Response:
   - List of all files uploaded to this session
   - file_count
   - total_size
   - Expected status: 200 OK
   
   ➜ Copy file_id from response


Step 4: Download File
────────────────────
   Request: GET /api/uploads/session/{session_id}/files/{file_id}/download
   
   Response:
   - Binary file content
   - Content-Disposition: attachment
   - Expected status: 200 OK


Step 5: Delete File
───────────────────
   Request: DELETE /api/uploads/session/{session_id}/files/{file_id}
   
   Response:
   {
     "file_id": "...",
     "session_id": "...",
     "deleted": true
   }
   - Expected status: 200 OK


Step 6: Clean Up - Delete Session
──────────────────────────────────
   Request: DELETE /api/uploads/session/{session_id}
   
   Response:
   {
     "status": "SUCCESS",
     "message": "Session deleted successfully"
   }
   - Expected status: 200 OK


🔄 BULK UPLOAD TEST:
────────────────────
   Request: POST /api/bajaj-po/bulk
   Query params:
   - client_id=1
   - project_id=3
   
   Form-data:
   - files: (select multiple Excel files)
   
   Response:
   {
     "status": "SUCCESS",
     "total_files": N,
     "successful": N,
     "failed": N,
     "uploaded_pos": [...],
     "errors": [...]
   }
   - Expected status: 200 OK


⚙️  VARIABLES TO SET:

   ${session_id}  → Get from "Create Session" response
   ${file_id}     → Get from "Upload File" or "List Files" response
   ${client_id}   → 1 (Bajaj) or 2 (Dava India)
   ${project_id}  → Project ID from database


✅ EXPECTED STATUS CODES:

   200 OK                 → Successful request
   400 Bad Request        → Invalid input
   404 Not Found          → Resource not found/expired
   422 Unprocessable      → Validation error
   500 Server Error       → Server error


💡 TEST SUCCESS CRITERIA:

   ✓ Session created with valid session_id
   ✓ File uploaded without errors
   ✓ Parse status shows SUCCESS (if auto_parse enabled)
   ✓ PO created in database (client_po_id returned)
   ✓ File downloadable
   ✓ File deletable
   ✓ Session deletable
   ✓ Bulk upload returns aggregate stats


📊 CRITICAL METRICS:

   - File upload time < 5s
   - Parse time < 3s
   - Download speed > 1MB/s
   - Session TTL working (expires after 24h)
   - Database insertion success rate > 95%


🚀 QUICK START:

   1. Import this collection into Postman
   2. Set base URL: http://localhost:8000
   3. Run "Create Upload Session" first
   4. Copy session_id to {{session_id}} variable
   5. Run "Upload File to Session"
   6. Run other tests in sequence
   7. Use "Delete Session" to clean up


❓ TROUBLESHOOTING:

   Parse failed?     → Check file format (must be Excel .xlsx)
   File not found?   → Session may have expired
   Upload slow?      → Check file size (>50MB may be slow)
   DB error?         → Check database connection
   Auto-parse not working? → Ensure client_id in session metadata


📝 NOTES:

   - Session expires after TTL (default 24 hours)
   - Files are compressed (gzip) automatically
   - PO parsing uses client-specific parsers
   - Bulk upload returns aggregate results
   - All operations support pagination


═══════════════════════════════════════════════════════════════════════
"""

print(GUIDE)

print("\n" + "="*73)
print("Collection file: Postman_Collection_Critical_Routes.json")
print("="*73)
