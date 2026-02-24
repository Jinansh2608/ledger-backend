#!/usr/bin/env python3
"""Check if POs are being saved after frontend integration"""

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host='localhost', port=5432, dbname='Nexgen_erp',
    user='postgres', password='toor', cursor_factory=RealDictCursor
)

try:
    cur = conn.cursor()
    cur.execute('SET search_path TO "Finances"')
    
    print("=" * 80)
    print("DATABASE STATUS CHECK - After Frontend Integration")
    print("=" * 80)
    print()
    
    # Check client_po table
    cur.execute('SELECT COUNT(*) as count FROM client_po')
    count = cur.fetchone()['count']
    print(f"✅ Total POs in database: {count}")
    print()
    
    if count > 0:
        print("📋 Latest PO records:")
        cur.execute('SELECT id, po_number, po_value, po_date, status FROM client_po ORDER BY created_at DESC LIMIT 5')
        pos = cur.fetchall()
        for i, po in enumerate(pos, 1):
            print(f"  {i}. ID: {po['id']}")
            print(f"     PO Number: {po['po_number']}")
            print(f"     Value: {po['po_value']}")
            print(f"     Date: {po['po_date']}")
            print(f"     Status: {po['status']}")
        print()
    else:
        print("⚠️  No POs found in database yet!")
        print()
    
    # Check line items
    cur.execute('SELECT COUNT(*) as count FROM client_po_line_item')
    line_count = cur.fetchone()['count']
    print(f"✅ Total line items: {line_count}")
    
    if line_count > 0:
        print()
        print("📝 Sample line items:")
        cur.execute('SELECT client_po_id, item_name, quantity, rate, total_price FROM client_po_line_item LIMIT 5')
        items = cur.fetchall()
        for i, item in enumerate(items, 1):
            print(f"  {i}. PO ID: {item['client_po_id']}, Item: {item['item_name']}, Qty: {item['quantity']}, Rate: {item['rate']}")
    
    print()
    print("=" * 80)
    
    if count > 0:
        print("✅ SUCCESS! POs are being saved to the database!")
        print()
        print("📊 Summary:")
        print(f"  - {count} Purchase Orders created")
        print(f"  - {line_count} Line Items across all POs")
        print(f"  - Average items per PO: {line_count // count if count > 0 else 0}")
    else:
        print("❌ No POs found. Check:")
        print("  1. Frontend is using uploadPO() with client_id=1 or 2")
        print("  2. File format matches expected layout (Bajaj or Dava India)")
        print("  3. Backend logs for any parse errors")
        print("  4. Session has project_id if linking to project")
    
    print("=" * 80)
    
    cur.close()
    
finally:
    conn.close()
