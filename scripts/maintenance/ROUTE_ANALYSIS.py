#!/usr/bin/env python3
"""
Route Analysis Report
Identifies redundant and unused routes
"""

routes_analysis = {
    "ESSENTIAL ROUTES": {
        "description": "Core file upload functionality (KEEP)",
        "routes": [
            "POST   /api/uploads/session - Create upload session",
            "POST   /api/uploads/session/{session_id}/files - Upload file with auto-parse",
            "POST   /api/uploads/po/upload - Direct PO upload & parse (PRIMARY)",
            "GET    /api/uploads/session/{session_id} - Get session details",
            "GET    /api/uploads/session/{session_id}/files - List files in session",
            "GET    /api/uploads/session/{session_id}/files/{file_id}/download - Download file",
            "DELETE /api/uploads/session/{session_id}/files/{file_id} - Delete file",
            "DELETE /api/uploads/session/{session_id} - Delete session"
        ]
    },
    
    "REDUNDANT ROUTES": {
        "description": "Duplicate functionality - can be removed",
        "routes": [
            "GET    /api/uploads/po/{po_number}/files - REDUNDANT (use session-based access)",
            "GET    /api/uploads/po/{po_number}/files/{file_id}/download - REDUNDANT",
            "GET    /api/uploads/po/{po_number}/stats - REDUNDANT",
            "DELETE /api/uploads/po/{po_number}/files/{file_id} - REDUNDANT"
        ]
    },
    
    "OPTIONAL ROUTES": {
        "description": "Nice to have but not critical",
        "routes": [
            "GET    /api/uploads/session/{session_id}/stats - Session statistics (REMOVE - rarely used)",
            "POST   /api/uploads/session/{session_id}/expire - Manual expiration (REMOVE - TTL handles it)"
        ]
    },
    
    "LEGACY ROUTES": {
        "description": "Duplicate of /api/uploads/po/upload functionality",
        "routes": [
            "POST   /api/bajaj-po - DUPLICATE (use /api/uploads/po/upload with client_id=1)"
        ]
    },
    
    "SUMMARY": {
        "to_remove": 7,
        "routes_to_remove": [
            "GET    /api/uploads/session/{session_id}/stats",
            "GET    /api/uploads/po/{po_number}/files",
            "GET    /api/uploads/po/{po_number}/files/{file_id}/download",
            "GET    /api/uploads/po/{po_number}/stats",
            "DELETE /api/uploads/po/{po_number}/files/{file_id}",
            "POST   /api/uploads/session/{session_id}/expire",
            "POST   /api/bajaj-po"
        ],
        "to_keep": 8,
        "estimated_lines_saved": "~300 lines"
    }
}

print("\n" + "="*70)
print("ROUTE REDUNDANCY ANALYSIS")
print("="*70)

for section, content in routes_analysis.items():
    if section == "SUMMARY":
        continue
    print(f"\n📌 {section}")
    print(f"   {content['description']}\n")
    for route in content['routes']:
        print(f"   • {route}")

print("\n" + "="*70)
print("CLEANUP PLAN")
print("="*70)
summary = routes_analysis["SUMMARY"]
print(f"\n   Routes to REMOVE: {summary['to_remove']}")
print(f"   Routes to KEEP:   {summary['to_keep']}")
print(f"   Lines Saved:      ~{summary['estimated_lines_saved']}")

print("\n   Routes being removed:")
for route in summary['routes_to_remove']:
    print(f"   ❌ {route}")

print("\n" + "="*70)
