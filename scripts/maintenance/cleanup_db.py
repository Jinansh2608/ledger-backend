#!/usr/bin/env python3
"""
Database Cleanup Script
Removes test/unnecessary data while keeping important business records
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

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    with conn.cursor() as cur:
        cur.execute('SET search_path TO "Finances";')
    return conn

def show_database_stats():
    """Show current database statistics"""
    print("\n📊 CURRENT DATABASE STATE\n" + "="*50)
    conn = get_connection()
    cur = conn.cursor()
    
    tables = [
        "client", "vendor", "project", "site",
        "client_po", "billing_po", "vendor_order", "vendor_payment",
        "payment", "proforma_invoice", "document",
        "upload_file", "upload_session", "vendor_payment_link"
    ]
    
    stats = {}
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) as cnt FROM {table};")
            result = cur.fetchone()
            stats[table] = result['cnt']
            print(f"  {table:.<30} {result['cnt']:>6} records")
        except:
            pass
    
    conn.close()
    return stats

def cleanup_database():
    """Remove test/temporary data"""
    print("\n🧹 CLEANING DATABASE\n" + "="*50)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Delete upload sessions and files (test data)
        print("\n  Removing upload sessions...")
        cur.execute("SELECT id FROM upload_session LIMIT 1;")
        if cur.fetchone():
            cur.execute("DELETE FROM upload_file;")
            removed_files = cur.rowcount
            cur.execute("DELETE FROM upload_session;")
            removed_sessions = cur.rowcount
            conn.commit()
            print(f"    ✅ Deleted {removed_files} upload files")
            print(f"    ✅ Deleted {removed_sessions} upload sessions")
        
        # 2. Delete test POs (keep real ones if any)
        print("\n  Checking POs...")
        cur.execute("SELECT COUNT(*) as cnt FROM client_po;")
        po_count = cur.fetchone()['cnt']
        print(f"    ℹ️  Total POs: {po_count}")
        
        if po_count > 0:
            print("    ℹ️  Keeping all POs for now (in case they're important)")
        
        # 3. Show what we're keeping
        print("\n  Keeping these important tables:")
        keep_tables = {
            "client": "Customers",
            "vendor": "Suppliers", 
            "project": "Projects",
            "site": "Sites/Locations",
            "client_po": "Purchase Orders",
            "payment": "Payments",
            "document": "Documents",
            "proforma_invoice": "Proforma Invoices"
        }
        
        for table, description in keep_tables.items():
            cur.execute(f"SELECT COUNT(*) as cnt FROM {table};")
            cnt = cur.fetchone()['cnt']
            if cnt > 0:
                print(f"    ✅ {table:.<25} {cnt} records ({description})")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"    ❌ Error during cleanup: {e}")
        return False
    finally:
        conn.close()
    
    return True

def show_important_records():
    """Display important business records"""
    print("\n📋 IMPORTANT BUSINESS DATA\n" + "="*50)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Clients
        print("\n  CLIENTS:")
        cur.execute("SELECT id, name FROM client LIMIT 10;")
        clients = cur.fetchall()
        if clients:
            for c in clients:
                print(f"    • {c['name']} (ID: {c['id']})")
        else:
            print("    (No clients)")
        
        # Vendors
        print("\n  VENDORS:")
        cur.execute("SELECT id, name, email, phone FROM vendor LIMIT 10;")
        vendors = cur.fetchall()
        if vendors:
            for v in vendors:
                contact = f"{v['email']}" if v['email'] else v['phone'] if v['phone'] else "No contact"
                print(f"    • {v['name']} (ID: {v['id']}, {contact})")
        else:
            print("    (No vendors)")
        
        # Projects
        print("\n  PROJECTS:")
        cur.execute("SELECT id, name FROM project LIMIT 10;")
        projects = cur.fetchall()
        if projects:
            for p in projects:
                print(f"    • {p['name']} (ID: {p['id']})")
        else:
            print("    (No projects)")
        
        # Sites
        print("\n  SITES:")
        cur.execute("SELECT id, site_name, store_id FROM site LIMIT 10;")
        sites = cur.fetchall()
        if sites:
            for s in sites:
                print(f"    • {s['site_name']} (ID: {s['id']}, Store: {s['store_id']})")
        else:
            print("    (No sites)")
        
        # POs
        print("\n  PURCHASE ORDERS:")
        cur.execute("SELECT id, po_number, po_value, client_id FROM client_po LIMIT 10;")
        pos = cur.fetchall()
        if pos:
            for po in pos:
                print(f"    • PO {po['po_number']} (ID: {po['id']}, Value: {po['po_value']}, Client ID: {po['client_id']})")
        else:
            print("    (No POs)")
        
    finally:
        conn.close()

def main():
    print("\n" + "="*60)
    print("DATABASE CLEANUP UTILITY")
    print("="*60)
    
    # Show before-state
    show_database_stats()
    
    # Show important records
    show_important_records()
    
    # Ask for confirmation
    print("\n" + "="*50)
    response = input("\n🤔 Proceed with cleanup? (yes/no): ").strip().lower()
    
    if response == 'yes':
        if cleanup_database():
            print("\n✅ CLEANUP COMPLETE")
            print("\n  After-state:")
            show_database_stats()
            print("\n✨ Database cleaned successfully!")
        else:
            print("\n❌ Cleanup failed")
    else:
        print("\n⏭️  Cleanup cancelled")

if __name__ == "__main__":
    main()
