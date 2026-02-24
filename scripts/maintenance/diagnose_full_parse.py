#!/usr/bin/env python3
"""Simulate the complete file parsing process like the server does"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.modules.file_uploads.services.parsing_service import FileParsingService
from app.repository.client_po_repo import insert_client_po
from app.database import get_db

print("=" * 80)
print("DIAGNOSIS: Test complete parsing and insertion flow")
print("=" * 80)
print()

# Get a recent uploaded file
test_file = "uploads/sessions/6084384b-ac78-4015-ac9a-143f70b1257d/20260210_075115_5baf035ca5608a7b26758188c7733ea3.xlsx"

if not os.path.exists(test_file):
    print(f"Test file not found: {test_file}")
    print()
    print("Finding recent uploaded file...")
    for root, dirs, files in os.walk("uploads/sessions"):
        for file in sorted(files):
            if file.endswith('.xlsx'):
                test_file = os.path.join(root, file)
                break
        if test_file and os.path.exists(test_file):
            break

if not os.path.exists(test_file):
    print("❌ No files found!")
    sys.exit(1)

print(f"Using file: {test_file}")
file_size = os.path.getsize(test_file)
print(f"File size: {file_size} bytes")
print()

try:
    # Step 1: Read file as bytes
    print("Step 1: Reading file as bytes...")
    with open(test_file, 'rb') as f:
        file_content = f.read()
    print(f"✅ Read {len(file_content)} bytes")
    print()
    
    # Step 2: Parse it the same way the server does
    print("Step 2: Parsing with FileParsingService (mimics server process)...")
    parsed_data = FileParsingService.parse_uploaded_file(
        file_content=file_content,
        filename=os.path.basename(test_file),
        client_id=1,  # Bajaj
        session_id='test-session',
        file_id='test-file-id'
    )
    
    print("✅ Parsing successful!")
    print()
    
    # Step 3: Check what was returned
    print("Parsed data structure:")
    print(f"  - Keys: {list(parsed_data.keys())}")
    print(f"  - po_details: {bool(parsed_data.get('po_details'))}")
    print(f"  - line_items count: {len(parsed_data.get('line_items', []))}")
    print(f"  - parsing_status: {parsed_data.get('parsing_status')}")
    
    if parsed_data.get('po_details'):
        po = parsed_data['po_details']
        print(f"  - po_details keys: {list(po.keys())}")
        print(f"    - po_number: {po.get('po_number')}")
        print(f"    - po_value: {po.get('po_value')}")
    
    if parsed_data.get('line_items'):
        print(f"  - First line item: {parsed_data['line_items'][0] if parsed_data['line_items'] else 'N/A'}")
    
    print()
    
    # Step 4: Try to insert
    print("Step 3: Attempting to insert into database...")
    try:
        client_po_id = insert_client_po(parsed_data, client_id=1, project_id=None)
        print(f"✅ Insertion successful! PO ID: {client_po_id}")
        print()
        
        # Verify
        print("Step 4: Verifying inserted PO...")
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, po_number, client_id, po_value 
                FROM "Finances"."client_po"
                WHERE id = %s
            """, (client_po_id,))
            row = cursor.fetchone()
            if row:
                print(f"✅ PO verified:")
                print(f"   - ID: {row[0]}")
                print(f"   - PO Number: {row[1]}")
                print(f"   - Client ID: {row[2]}")
                print(f"   - PO Value: ${row[3]}")
            else:
                print("❌ PO not found after insertion!")
        conn.close()
        
        print()
        print("=" * 80)
        print("✅ SUCCESS: Full pipeline working!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Insertion failed: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Parsing failed: {e}")
    import traceback
    traceback.print_exc()
