#!/usr/bin/env python3
"""
Complete cleanup - remove ALL orphaned and project-related data
Keep ONLY: clients, vendors, and their base records
"""
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Nexgen_erp",
    "user": "postgres",
    "password": "toor"
}

def cleanup():
    print("\n" + "="*70)
    print("  🧹 COMPLETE DATABASE CLEANUP - REMOVING ALL PROJECT DATA")
    print("="*70 + "\n")
    
    # Order matters: delete dependent tables first
    tables_to_clear = [
        "client_po_line_item",      # Depends on client_po
        "billing_po_line_item",     # Depends on billing_po
        "vendor_order_line_item",   # Depends on vendor_order
        "project_document",         # Depends on project
        "po_project_mapping",       # Depends on project
        "upload_file",              # Depends on upload_session
        "upload_session",           # Upload sessions
        "upload_stats",             # Upload statistics
        "client_payment",           # Depends on client/payment
        "payment_vendor_link",      # Depends on payment
        "client_po",                # Client POs
        "billing_po",               # Billing POs
        "vendor_order",             # Vendor orders
        "vendor_payment",           # Vendor payments
        "site",                     # Sites
    ]
    
    total_removed = 0
    
    for table in tables_to_clear:
        try:
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
            cur = conn.cursor()
            cur.execute('SET search_path TO "Finances";')
            
            # Try to delete
            cur.execute(f'DELETE FROM "{table}";')
            removed = cur.rowcount
            conn.commit()
            conn.close()
            
            if removed > 0:
                print(f"  ✅ {table:.<40} Cleared {removed:>6} records")
                total_removed += removed
            else:
                print(f"  ℹ️  {table:.<40} Empty")
                
        except Exception as e:
            error_str = str(e)
            if "does not exist" in error_str:
                print(f"  ℹ️  {table:.<40} Table doesn't exist")
            else:
                print(f"  ⚠️  {table:.<40} Error: {error_str[:30]}")
    
    print(f"\n  📊 Total records removed: {total_removed}")
    print("\n" + "="*70)
    print("  ✅ CLEANUP COMPLETE")
    print("="*70 + "\n")
    
    # Final verification
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute('SET search_path TO "Finances";')
    
    print("  FINAL STATE:\n")
    
    cur.execute('SELECT COUNT(*) as cnt FROM client;')
    clients = cur.fetchone()['cnt']
    print(f"  ✅ Clients:   {clients} records (KEPT)")
    
    cur.execute('SELECT COUNT(*) as cnt FROM vendor;')
    vendors = cur.fetchone()['cnt']
    print(f"  ✅ Vendors:   {vendors} records (KEPT)")
    
    cur.execute('SELECT COUNT(*) as cnt FROM project;')
    projects = cur.fetchone()['cnt']
    print(f"  ✅ Projects:  {projects} records (REMOVED)")
    
    conn.close()

if __name__ == "__main__":
    cleanup()
