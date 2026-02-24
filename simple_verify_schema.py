#!/usr/bin/env python3
"""
Simple verification that schema fixes are correct
"""

from app.database import get_db

print("=" * 100)
print("SCHEMA SYNC FIXES VERIFICATION")
print("=" * 100)

conn = get_db()

try:
    with conn.cursor() as cur:
        # 1. Verify po_project_mapping columns
        print("\n✓ Checking po_project_mapping table...")
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'po_project_mapping' 
            ORDER BY ordinal_position
        """)
        ppm_cols = [row['column_name'] for row in cur.fetchall()]
        print(f"  Actual columns: {', '.join(ppm_cols)}")
        
        if 'is_primary' in ppm_cols:
            print("  ❌ FAIL: is_primary column still exists (should not)")
        else:
            print("  ✅ PASS: is_primary correctly removed")
            
        if 'sequence_order' in ppm_cols:
            print("  ❌ FAIL: sequence_order column still exists (should not)")
        else:
            print("  ✅ PASS: sequence_order correctly removed")
            
        if 'client_po_id' in ppm_cols and 'project_id' in ppm_cols:
            print("  ✅ PASS: Required columns client_po_id and project_id exist")
        else:
            print("  ❌ FAIL: Missing required columns")
        
        # 2. Verify client_po_line_item columns
        print("\n✓ Checking client_po_line_item table...")
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'client_po_line_item' 
            ORDER BY ordinal_position
        """)
        cli_cols = [row['column_name'] for row in cur.fetchall()]
        print(f"  Actual columns: {', '.join(cli_cols)}")
        
        required_cols = ['id', 'item_name', 'quantity', 'unit_price', 'total_price']
        missing = [c for c in required_cols if c not in cli_cols]
        if missing:
            print(f"  ❌ FAIL: Missing required columns: {', '.join(missing)}")
        else:
            print("  ✅ PASS: All basic line item columns present")
            
        new_cols = ['hsn_code', 'unit', 'rate', 'gst_amount', 'gross_amount']
        new_missing = [c for c in new_cols if c not in cli_cols]
        if new_missing:
            print(f"  ❌ FAIL: Missing new fields: {', '.join(new_missing)}")
        else:
            print(f"  ✅ PASS: All new fields present {new_cols}")
            
        if 'created_at' in cli_cols:
            print("  ❌ FAIL: created_at exists (code no longer selects it)")
        else:
            print("  ✅ PASS: created_at correctly not expected")

        print("\n" + "=" * 100)
        print("SCHEMA VERIFICATION COMPLETE")
        print("=" * 100)

finally:
    conn.close()
