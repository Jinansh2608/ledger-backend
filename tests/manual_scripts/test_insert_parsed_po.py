#!/usr/bin/env python3
"""Test if we can insert parsed PO data from database"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from psycopg2.extras import RealDictCursor
from app.repository.client_po_repo import insert_client_po

conn = psycopg2.connect(
    host='localhost', port=5432, dbname='Nexgen_erp',
    user='postgres', password='toor', cursor_factory=RealDictCursor
)

try:
    cur = conn.cursor()
    cur.execute('SET search_path TO "Finances"')
    
    print("=" * 80)
    print("TEST: Inserting Parsed PO Data from Database")
    print("=" * 80)
    print()
    
    # Get a parsed file from upload_file table
    cur.execute('''
        SELECT id, metadata FROM upload_file 
        WHERE metadata->>'parsed' = 'true'
        LIMIT 1
    ''')
    
    result = cur.fetchone()
    
    if not result:
        print("❌ No parsed files found in database")
        exit(1)
    
    file_id = result['id']
    metadata = result['metadata']
    
    print(f"📁 File ID: {file_id}")
    print(f"📋 Metadata Keys: {list(metadata.keys())}")
    print()
    
    # Check structure
    print("Checking metadata structure:")
    print(f"  - Has 'parsed': {metadata.get('parsed')}")
    print(f"  - Has 'po_details': {bool(metadata.get('po_details'))}")
    print(f"  - Has 'line_items': {bool(metadata.get('line_items'))}")
    print(f"  - Line item count: {metadata.get('line_item_count', 0)}")
    print()
    
    # Try to insert
    print("Attempting to insert PO...")
    print()
    
    try:
        # The parsed_data from metadata should have po_details and line_items
        parsed_data = {
            'po_details': metadata.get('po_details', {}),
            'line_items': metadata.get('line_items', []),
            'line_item_count': metadata.get('line_item_count', 0),
            'client_name': metadata.get('client_name'),
            'parser_type': metadata.get('parser_type')
        }
        
        print(f"Parsed data structure:")
        print(f"  - po_details keys: {list(parsed_data['po_details'].keys()) if parsed_data['po_details'] else 'EMPTY'}")
        print(f"  - line_items count: {len(parsed_data['line_items'])}")
        print()
        
        # Try to insert
        client_po_id = insert_client_po(parsed_data, client_id=1, project_id=None)
        
        print(f"✅ SUCCESS! PO inserted with ID: {client_po_id}")
        
        # Verify it was inserted
        cur.execute('SELECT id, po_number, po_value FROM client_po WHERE id = %s', (client_po_id,))
        po = cur.fetchone()
        if po:
            print()
            print("Verification:")
            print(f"  - PO Number: {po['po_number']}")
            print(f"  - PO Value: {po['po_value']}")
        
    except Exception as e:
        print(f"❌ INSERTION FAILED: {e}")
        print()
        import traceback
        traceback.print_exc()
        
        print()
        print("=" * 80)
        print("DEBUGGING INFO")
        print("=" * 80)
        print()
        print("Full metadata:")
        import json
        print(json.dumps(metadata, indent=2))
        
finally:
    cur.close()
    conn.close()
