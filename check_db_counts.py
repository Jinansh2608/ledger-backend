#!/usr/bin/env python3
from app.database import get_db

conn = get_db()
try:
    with conn.cursor() as cur:
        # Check projects
        cur.execute("SELECT COUNT(*) as count FROM project")
        project_count = cur.fetchone()["count"]
        print(f"Projects: {project_count}")
        
        # Check client_po
        cur.execute("SELECT COUNT(*) as count FROM client_po")
        po_count = cur.fetchone()["count"]
        print(f"Client POs: {po_count}")
        
        # Check line items
        cur.execute("SELECT COUNT(*) as count FROM client_po_line_item")
        line_items_count = cur.fetchone()["count"]
        print(f"Line Items: {line_items_count}")
        
        # Check po_project_mapping
        cur.execute("SELECT COUNT(*) as count FROM po_project_mapping")
        mapping_count = cur.fetchone()["count"]
        print(f"PO Project Mappings: {mapping_count}")
finally:
    conn.close()
