#!/usr/bin/env python3
"""
Test script to verify line items mapping for a project
Follows the complete chain: Project → POs → Line Items
"""

from app.database import get_db
import json


def get_all_projects():
    """Get all projects in database"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, status FROM project ORDER BY created_at DESC")
            projects = cur.fetchall()
            return projects
    finally:
        conn.close()


def get_project_pos(project_id):
    """Get all POs linked to a project"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Query using both direct link and mapping table
            cur.execute("""
                SELECT DISTINCT
                    cp.id as po_id,
                    cp.po_number,
                    cp.po_date,
                    cp.po_value,
                    cp.status,
                    cp.po_type,
                    cp.created_at
                FROM client_po cp
                LEFT JOIN po_project_mapping ppm ON cp.id = ppm.client_po_id
                WHERE ppm.project_id = %s OR cp.project_id = %s
                ORDER BY cp.created_at
            """, (project_id, project_id))
            
            pos = cur.fetchall()
            return pos
    finally:
        conn.close()


def get_po_line_items(client_po_id):
    """Get all line items for a PO"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    item_name,
                    quantity,
                    unit_price,
                    total_price,
                    unit,
                    hsn_code
                FROM client_po_line_item
                WHERE client_po_id = %s
                ORDER BY id
            """, (client_po_id,))
            
            items = cur.fetchall()
            return items
    finally:
        conn.close()


def main():
    print("\n" + "="*80)
    print("🔍 TEST: Project → POs → Line Items Mapping")
    print("="*80)
    
    # Step 1: Get all projects
    print("\n📋 STEP 1: Getting all projects...")
    projects = get_all_projects()
    
    if not projects:
        print("❌ No projects found in database")
        return
    
    print(f"✅ Found {len(projects)} project(s):")
    for project in projects:
        print(f"   - ID: {project['id']}, Name: {project['name']}, Status: {project['status']}")
    
    # Step 2: Process first project
    project = projects[0]
    project_id = project['id']
    project_name = project['name']
    
    print(f"\n📌 STEP 2: Getting POs for Project '{project_name}' (ID: {project_id})...")
    pos = get_project_pos(project_id)
    
    if not pos:
        print(f"⚠️  No POs linked to project '{project_name}'")
        return
    
    print(f"✅ Found {len(pos)} PO(s) for this project:")
    
    # Step 3: Get line items for each PO
    total_line_items = 0
    total_value = 0
    
    for idx, po in enumerate(pos, 1):
        po_id = po['po_id']
        po_number = po['po_number']
        po_value = po['po_value']
        po_type = po['po_type']
        
        print(f"\n   PO #{idx}: {po_number} (ID: {po_id})")
        print(f"   ├─ Value: {po_value}")
        print(f"   ├─ Type: {po_type}")
        print(f"   ├─ Status: {po['status']}")
        
        # Get line items for this PO
        line_items = get_po_line_items(po_id)
        
        if not line_items:
            print(f"   └─ Line Items: None")
        else:
            print(f"   └─ Line Items: {len(line_items)}")
            for item_idx, item in enumerate(line_items, 1):
                print(f"       ├─ Item {item_idx}: {item['item_name']}")
                print(f"       │  ├─ Quantity: {item['quantity']} {item['unit']}")
                print(f"       │  ├─ Unit Price: {item['unit_price']}")
                print(f"       │  ├─ HSN Code: {item['hsn_code']}")
                print(f"       │  └─ Total: {item['total_price']}")
                
                total_line_items += 1
                total_value += float(item['total_price']) if item['total_price'] else 0
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Project: {project_name} (ID: {project_id})")
    print(f"Total POs: {len(pos)}")
    print(f"Total Line Items: {total_line_items}")
    print(f"Total Line Items Value: ₹{total_value:,.2f}")
    
    # Database stats
    print("\n" + "="*80)
    print("🗄️  DATABASE VERIFICATION")
    print("="*80)
    
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Count records in each table
            cur.execute("SELECT COUNT(*) as count FROM project")
            project_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM client_po")
            po_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM client_po_line_item")
            line_item_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM po_project_mapping")
            mapping_count = cur.fetchone()['count']
            
            print(f"✅ Projects table: {project_count} records")
            print(f"✅ Client POs table: {po_count} records")
            print(f"✅ Line Items table: {line_item_count} records")
            print(f"✅ PO-Project Mapping: {mapping_count} records")
    finally:
        conn.close()
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
