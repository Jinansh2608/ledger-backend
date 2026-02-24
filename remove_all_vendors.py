#!/usr/bin/env python3
"""
Remove All Vendors from Database
Keeps: Clients only
Removes: All vendors and vendor-related data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Nexgen_erp",
    "user": "postgres",
    "password": "toor"
}

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    with conn.cursor() as cur:
        cur.execute('SET search_path TO "Finances";')
    return conn

def show_current_stats():
    """Show what's currently in the database"""
    print("\n" + "="*70)
    print("  📊 CURRENT DATABASE STATE")
    print("="*70 + "\n")
    
    conn = get_connection()
    cur = conn.cursor()
    
    tables = {
        "KEEPING": ["client"],
        "REMOVING": [
            "vendor",
            "vendor_order",
            "vendor_payment",
            "vendor_order_line_item"
        ]
    }
    
    for category, table_list in tables.items():
        print(f"  {category}:")
        for table in table_list:
            try:
                cur.execute(f"SELECT COUNT(*) as cnt FROM {table};")
                result = cur.fetchone()
                count = result['cnt'] if result else 0
                symbol = "✅ KEEP" if category == "KEEPING" else "❌ REMOVE"
                print(f"    {symbol:.<20} {table:.<30} {count:>6} records")
            except Exception as e:
                print(f"    ⚠️  {table:.<35} (error reading)")
        print()
    
    conn.close()

def remove_all_vendors():
    """Remove all vendors and related data"""
    print("="*70)
    print("  🧹 REMOVING ALL VENDORS")
    print("="*70 + "\n")
    
    cleanup_steps = [
        # Remove dependent records first
        ("vendor_order_line_item", "DELETE FROM vendor_order_line_item;"),
        ("vendor_order", "DELETE FROM vendor_order;"),
        ("vendor_payment", "DELETE FROM vendor_payment;"),
        ("vendor", "DELETE FROM vendor;"),
    ]
    
    total_removed = 0
    
    for table_name, delete_query in cleanup_steps:
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            cur.execute(delete_query)
            removed = cur.rowcount
            conn.commit()
            conn.close()
            
            if removed > 0:
                print(f"  ✅ {table_name:.<40} Removed {removed:>6} records")
                total_removed += removed
            else:
                print(f"  ℹ️  {table_name:.<40} No records to remove")
                
        except psycopg2.Error as e:
            error_msg = str(e).split('\n')[0][:50]
            print(f"  ⚠️  {table_name:.<40} {error_msg}")
        except Exception as e:
            print(f"  ❌ {table_name:.<40} Error: {str(e)[:30]}")
    
    print(f"\n  📊 TOTAL RECORDS REMOVED: {total_removed}")
    return True

def verify_cleanup():
    """Verify that cleanup was successful"""
    print("\n" + "="*70)
    print("  ✅ VERIFICATION - AFTER CLEANUP")
    print("="*70 + "\n")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Check that vendors are gone
    cur.execute("SELECT COUNT(*) as cnt FROM vendor;")
    vendor_count = cur.fetchone()['cnt']
    
    # Check that clients still exist
    cur.execute("SELECT COUNT(*) as cnt FROM client;")
    client_count = cur.fetchone()['cnt']
    
    print(f"  ✅ KEPT - Clients:  {client_count:>6} records")
    print(f"  ✅ REMOVED - Vendors: {vendor_count:>6} records (should be 0)")
    
    if vendor_count == 0:
        print(f"\n  🎉 SUCCESS! All vendors removed!")
        print(f"  📌 Database is clean.")
    else:
        print(f"\n  ⚠️  WARNING: {vendor_count} vendors still exist!")
    
    conn.close()
    return vendor_count == 0

def main():
    print("\n" + "="*70)
    print("  🗑️  DATABASE CLEANUP - REMOVE ALL VENDORS")
    print("="*70)
    
    # Show current state
    show_current_stats()
    
    # Confirm
    print("\n" + "-"*70)
    print("  ⚠️  WARNING: This will delete ALL vendors!")
    print("  It will KEEP: Clients")
    print("-"*70 + "\n")
    
    response = input("  Type 'DELETE ALL' to confirm (or anything else to cancel): ").strip()
    
    if response != "DELETE ALL":
        print("\n  ❌ Cleanup cancelled.")
        sys.exit(0)
    
    print()
    
    # Perform cleanup
    success = remove_all_vendors()
    
    if success:
        # Verify
        verify_cleanup()
    else:
        print("\n  ❌ Cleanup failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("  ✅ CLEANUP COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⏹️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ❌ Fatal error: {e}")
        sys.exit(1)
