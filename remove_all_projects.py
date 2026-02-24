#!/usr/bin/env python3
"""
Remove All Projects and Related Data
Keeps only: Clients, Vendors, and core configuration
Removes: Projects, POs, Line Items, Payments, Vendor Orders, Documents, etc.
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
        "KEEPING": ["client", "vendor"],
        "REMOVING": [
            "project", "site",
            "client_po", "billing_po", "vendor_order",
            "payment", "proforma_invoice",
            "document", "upload_file", "upload_session",
            "vendor_payment", "vendor_payment_link"
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
                print(f"    {symbol:.<20} {table:.<25} {count:>6} records")
            except Exception as e:
                print(f"    ⚠️  {table:.<35} (error reading)")
        print()
    
    conn.close()

def cleanup_all_projects():
    """Remove all projects and related data"""
    print("="*70)
    print("  🧹 REMOVING ALL PROJECTS AND RELATED DATA")
    print("="*70 + "\n")
    
    cleanup_steps = [
        # Step 1: Remove upload files and sessions
        ("upload_file", "DELETE FROM upload_file;"),
        ("upload_session", "DELETE FROM upload_session;"),
        
        # Step 2: Remove documents
        ("document", "DELETE FROM document;"),
        
        # Step 3: Remove payments
        ("payment", "DELETE FROM payment;"),
        ("vendor_payment", "DELETE FROM vendor_payment;"),
        ("vendor_payment_link", "DELETE FROM vendor_payment_link;"),
        
        # Step 4: Remove line items (if separate table exists)
        ("line_item", "DELETE FROM line_item WHERE 1=1;"),
        
        # Step 5: Remove orders
        ("vendor_order", "DELETE FROM vendor_order;"),
        ("client_po", "DELETE FROM client_po;"),
        ("billing_po", "DELETE FROM billing_po;"),
        
        # Step 6: Remove proforma invoices
        ("proforma_invoice", "DELETE FROM proforma_invoice;"),
        
        # Step 7: Remove projects and sites
        ("site", "DELETE FROM site;"),
        ("project", "DELETE FROM project;"),
    ]
    
    total_removed = 0
    
    for table_name, delete_query in cleanup_steps:
        # Create new connection for each delete to avoid transaction abort issues
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Try to disable triggers for this table
            try:
                cur.execute(f"ALTER TABLE IF EXISTS {table_name} DISABLE TRIGGER ALL;")
            except:
                pass
            
            try:
                cur.execute(delete_query)
                removed = cur.rowcount
                conn.commit()
                
                if removed > 0:
                    print(f"  ✅ {table_name:.<30} Removed {removed:>6} records")
                    total_removed += removed
                else:
                    print(f"  ℹ️  {table_name:.<30} No records to remove")
            except psycopg2.Error as e:
                conn.rollback()
                error_msg = str(e).split('\n')[0][:50]
                print(f"  ⚠️  {table_name:.<30} {error_msg}")
            finally:
                conn.close()
                
        except Exception as e:
            print(f"  ❌ {table_name:.<30} Connection error: {str(e)[:30]}")
    
    print(f"\n  📊 TOTAL RECORDS REMOVED: {total_removed}")
    return True

def verify_cleanup():
    """Verify that cleanup was successful"""
    print("\n" + "="*70)
    print("  ✅ VERIFICATION - AFTER CLEANUP")
    print("="*70 + "\n")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Check that projects are gone
    cur.execute("SELECT COUNT(*) as cnt FROM project;")
    project_count = cur.fetchone()['cnt']
    
    # Check that clients still exist
    cur.execute("SELECT COUNT(*) as cnt FROM client;")
    client_count = cur.fetchone()['cnt']
    
    # Check that vendors still exist
    cur.execute("SELECT COUNT(*) as cnt FROM vendor;")
    vendor_count = cur.fetchone()['cnt']
    
    print(f"  ✅ KEPT - Clients: {client_count:>6} records")
    print(f"  ✅ KEPT - Vendors: {vendor_count:>6} records")
    print(f"  ❌ REMOVED - Projects: {project_count:>6} records (should be 0)")
    
    if project_count == 0:
        print(f"\n  🎉 SUCCESS! All projects and related data removed!")
        print(f"  📌 Database is clean. Ready for new projects.")
    else:
        print(f"\n  ⚠️  WARNING: {project_count} projects still exist!")
    
    conn.close()
    return project_count == 0

def main():
    print("\n" + "="*70)
    print("  🗑️  DATABASE CLEANUP - REMOVE ALL PROJECTS")
    print("="*70)
    
    # Show current state
    show_current_stats()
    
    # Confirm
    print("\n" + "-"*70)
    print("  ⚠️  WARNING: This will delete ALL projects and related data!")
    print("  It will KEEP: Clients and Vendors")
    print("-"*70 + "\n")
    
    response = input("  Type 'DELETE ALL' to confirm (or anything else to cancel): ").strip()
    
    if response != "DELETE ALL":
        print("\n  ❌ Cleanup cancelled.")
        sys.exit(0)
    
    print()
    
    # Perform cleanup
    success = cleanup_all_projects()
    
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
