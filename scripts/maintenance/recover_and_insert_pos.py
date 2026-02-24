#!/usr/bin/env python3
"""Insert POs from successfully parsed files that are missing line_items from the database"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.repository.client_po_repo import insert_client_po
import json

print("=" * 80)
print("RECOVERY: Insert POs from successfully parsed files")
print("=" * 80)
print()

conn = get_db()
with conn.cursor() as cursor:
    # Get all files that were parsed
    cursor.execute("""
        SELECT id, original_filename, metadata
        FROM "Finances"."upload_file"
        WHERE metadata IS NOT NULL 
        AND metadata->>'parsed' = 'true'
    """)
    
    files = cursor.fetchall()
    print(f"Found {len(files)} parsed files")
    print()
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for file_rec in files:
        if isinstance(file_rec, dict):
            file_id = file_rec['id']
            filename = file_rec['original_filename']
            metadata_json = file_rec['metadata']
        else:
            file_id, filename, metadata_json = file_rec
        
        try:
            # Parse metadata
            metadata = metadata_json if isinstance(metadata_json, dict) else json.loads(metadata_json)
            
            # Check if we have line_items
            line_items = metadata.get('line_items', [])
            
            if not line_items or line_items == []:
                skip_count += 1
                print(f"⏭️  SKIP: {filename} - No line items in metadata")
                continue
            
            # Check if PO already exists
            po_details = metadata.get('po_details', {})
            if not po_details:
                skip_count += 1
                print(f"⏭️  SKIP: {filename} - No PO details in metadata")
                continue
            
            po_number = po_details.get('po_number')
            if not po_number:
                skip_count += 1
                print(f"⏭️  SKIP: {filename} - No PO number")
                continue
            
            # Check if this PO already exists in database
            cursor.execute("""
                SELECT id FROM "Finances"."client_po"
                WHERE po_number = %s AND client_id = %s
            """, (po_number, 1))  # Assuming client_id = 1
            
            if cursor.fetchone():
                skip_count += 1
                print(f"⏭️  SKIP: {filename} (PO #{po_number}) - Already in database")
                continue
            
            # Prepare parsed_data for insertion
            parsed_data = {
                'po_details': po_details,
                'line_items': line_items,
                'parser_type': metadata.get('parser_type', 'unknown'),
                'client_name': metadata.get('client_name', 'Unknown'),
                'line_item_count': len(line_items)
            }
            
            # Insert into database
            po_id = insert_client_po(parsed_data, client_id=1, project_id=None)
            success_count += 1
            print(f"✅ SUCCESS: {filename} -> PO ID {po_id} (PO #{po_number})")
            
        except Exception as e:
            error_count += 1
            print(f"❌ ERROR: {filename} - {str(e)}")
    
    conn.close()

print()
print("=" * 80)
print(f"RESULTS: {success_count} inserted, {skip_count} skipped, {error_count} errors")
print("=" * 80)
