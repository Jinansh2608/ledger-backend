#!/usr/bin/env python3
"""Simulate what the frontend is sending and check response"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# This will simulate the parsing that happens and check what data is available
from app.modules.file_uploads.services.parser_factory import ParserFactory
from app.repository.client_po_repo import insert_client_po
import os

print("=" * 80)
print("DIAGNOSIS: Check if insert_client_po can handle parsed data")
print("=" * 80)
print()

# Get a test file
test_file = "uploads/sessions/6084384b-ac78-4015-ac9a-143f70b1257d/20260210_075115_5baf035ca5608a7b26758188c7733ea3.xlsx"

if not os.path.exists(test_file):
    print(f"❌ Test file not found: {test_file}")
    print()
    print("Trying to find Bajaj PO files...")
    
    # Find any xlsx file
    for root, dirs, files in os.walk("uploads"):
        for file in files:
            if file.endswith('.xlsx'):
                test_file = os.path.join(root, file)
                print(f"✅ Found: {test_file}")
                break
        if test_file:
            break

if not os.path.exists(test_file):
    print("No files found to test with")
    sys.exit(1)

print()
print(f"Using test file: {test_file}")
print()

try:
    # Try parsing
    print("Step 1: Parsing file with Bajaj parser...")
    parsed_data = ParserFactory.parse_file(test_file, client_id=1)
    
    print("✅ Parsing successful!")
    print()
    print("Parsed data structure:")
    print(f"  - Keys: {list(parsed_data.keys())}")
    print(f"  - po_details: {bool(parsed_data.get('po_details'))}")
    print(f"  - line_items count: {len(parsed_data.get('line_items', []))}")
    
    if parsed_data.get('po_details'):
        print(f"  - po_details keys: {list(parsed_data['po_details'].keys())}")
        print(f"    - po_number: {parsed_data['po_details'].get('po_number')}")
        print(f"    - po_value: {parsed_data['po_details'].get('po_value')}")
    
    print()
    print("Step 2: Attempting to insert into database...")
    
    client_po_id = insert_client_po(parsed_data, client_id=1, project_id=None)
    
    print(f"✅ Insertion successful! ID: {client_po_id}")
    print()
    print("=" * 80)
    print("✅ SUCCESS: Parser + Insertion working correctly")
    print("=" * 80)
    print()
    print("The issue must be:")
    print("  1. auto_save not being set to true in frontend call, OR")
    print("  2. Exception during insertion being silently caught")
    print()
    print("Check backend logs when uploading from frontend for error messages")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print()
    print("=" * 80)
    print("❌ PARSING/INSERTION FAILED")
    print("=" * 80)
    print()
    print(f"Error: {e}")
