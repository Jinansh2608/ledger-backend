#!/usr/bin/env python3
"""
Remove All Projects for a Specific Client
Removes: Projects, POs, Line Items, Payments, etc. for specified client_id
Keeps: Other clients' data
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

def get_client_name(client_id):
    """Get client name by ID"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM client WHERE id = %s;", (client_id,))
        result = cur.fetchone()
        conn.close()
        return result['name'] if result else f"Client {client_id}"
    except:
        return f"Client {client_id}"

def show_client_stats(client_id):
    """Show what's currently in the database for this client"""
    print("\n" + "="*70)
    print(f"  📊 DATA FOR CLIENT {client_id}: {get_client_name(client_id)}")
    print("="*70 + "\n")
    
    conn = get_connection()
    cur = conn.cursor()
    
    stats = {
        "project": f"SELECT COUNT(*) as cnt FROM project WHERE client_id = %s;",
        "site": f"SELECT COUNT(*) as cnt FROM site WHERE client_id = %s;",
        "client_po": f"SELECT COUNT(*) as cnt FROM client_po WHERE client_id = %s;",
        "billing_po": f"SELECT COUNT(*) as cnt FROM billing_po WHERE client_id = %s;",
        "vendor_order": f"SELECT COUNT(*) as cnt FROM vendor_order WHERE client_id = %s;",
        "payment": f"SELECT COUNT(*) as cnt FROM payment WHERE client_id = %s;",
        "proforma_invoice": f"SELECT COUNT(*) as cnt FROM proforma_invoice WHERE client_id = %s;",
        "document": f"SELECT COUNT(*) as cnt FROM document WHERE client_id = %s;",
    }
    
    print(f"  ITEMS TO REMOVE:")
    total = 0
    for table, query in stats.items():
        try:
            cur.execute(query, (client_id,))
            result = cur.fetchone()
            count = result['cnt'] if result else 0
            total += count
            print(f"    ❌ {table:.<30} {count:>6} records")
        except Exception as e:
            print(f"    ⚠️  {table:.<30} (error reading)")
    
    print(f"\n  TOTAL TO REMOVE: {total} records\n")
    
    conn.close()
    return total

def cleanup_client_projects(client_id):
    """Remove all projects and related data for a specific client"""
    print("="*70)
    print(f"  🧹 REMOVING ALL DATA FOR CLIENT {client_id}: {get_client_name(client_id)}")
    print("="*70 + "\n")
    
    # Get project IDs first
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM project WHERE client_id = %s;", (client_id,))
    project_ids = [row['id'] for row in cur.fetchall()]
    conn.close()
    
    cleanup_steps = [
        # Step 1: Remove payments for this client
        ("payment", 
         f"DELETE FROM payment WHERE client_id = %s;",
         (client_id,)),
        
        # Step 2: Remove vendor payments
        ("vendor_payment", 
         f"DELETE FROM vendor_payment WHERE client_id = %s;",
         (client_id,)),
        
        ("vendor_payment_link", 
         f"DELETE FROM vendor_payment_link WHERE client_id = %s;",
         (client_id,)),
        
        # Step 3: Remove line items
        ("line_item", 
         f"DELETE FROM line_item WHERE client_id = %s;",
         (client_id,)),
        
        # Step 4: Remove vendor orders
        ("vendor_order", 
         f"DELETE FROM vendor_order WHERE client_id = %s;",
         (client_id,)),
        
        # Step 5: Remove POs
        ("client_po", 
         f"DELETE FROM client_po WHERE client_id = %s;",
         (client_id,)),
        
        ("billing_po", 
         f"DELETE FROM billing_po WHERE client_id = %s;",
         (client_id,)),
        
        # Step 6: Remove proforma invoices
        ("proforma_invoice", 
         f"DELETE FROM proforma_invoice WHERE client_id = %s;",
         (client_id,)),
        
        # Step 7: Remove documents
        ("document", 
         f"DELETE FROM document WHERE client_id = %s;",
         (client_id,)),
        
        # Step 8: Remove upload files (if linked to client somehow - may need adjustment)
        # This depends on your schema
        
        # Step 9: Remove sites
        ("site", 
         f"DELETE FROM site WHERE client_id = %s;",
         (client_id,)),
        
        # Step 10: Remove projects
        ("project", 
         f"DELETE FROM project WHERE client_id = %s;",
         (client_id,)),
    ]
    
    total_removed = 0
    
    for table_name, delete_query, params in cleanup_steps:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(delete_query, params)
            removed = cur.rowcount
            conn.commit()
            conn.close()
            
            if removed > 0:
                print(f"  ✅ {table_name:.<30} {removed:>6} records removed")
                total_removed += removed
            
        except psycopg2.errors.UndefinedTable:
            print(f"  ⚠️  {table_name:.<30} (table does not exist)")
        except Exception as e:
            print(f"  ❌ {table_name:.<30} ERROR: {str(e)}")
    
    print(f"\n  TOTAL REMOVED: {total_removed} records\n")
    return total_removed

def verify_removal(client_id):
    """Verify that all data has been removed"""
    print("="*70)
    print(f"  ✅ VERIFICATION - DATA FOR CLIENT {client_id}")
    print("="*70 + "\n")
    
    conn = get_connection()
    cur = conn.cursor()
    
    checks = {
        "project": f"SELECT COUNT(*) as cnt FROM project WHERE client_id = %s;",
        "site": f"SELECT COUNT(*) as cnt FROM site WHERE client_id = %s;",
        "client_po": f"SELECT COUNT(*) as cnt FROM client_po WHERE client_id = %s;",
        "billing_po": f"SELECT COUNT(*) as cnt FROM billing_po WHERE client_id = %s;",
        "vendor_order": f"SELECT COUNT(*) as cnt FROM vendor_order WHERE client_id = %s;",
        "payment": f"SELECT COUNT(*) as cnt FROM payment WHERE client_id = %s;",
        "proforma_invoice": f"SELECT COUNT(*) as cnt FROM proforma_invoice WHERE client_id = %s;",
    }
    
    total_remaining = 0
    all_clean = True
    
    for table, query in checks.items():
        try:
            cur.execute(query, (client_id,))
            result = cur.fetchone()
            count = result['cnt'] if result else 0
            total_remaining += count
            
            if count == 0:
                print(f"  ✅ {table:.<30} 0 records (CLEAN)")
            else:
                print(f"  ⚠️  {table:.<30} {count:>6} records (NOT CLEAN)")
                all_clean = False
        except Exception as e:
            print(f"  ⚠️  {table:.<30} (error reading)")
    
    conn.close()
    
    print(f"\n  TOTAL REMAINING: {total_remaining} records")
    
    if all_clean:
        print(f"\n  ✅ SUCCESS! All data for client {client_id} has been removed!\n")
    else:
        print(f"\n  ⚠️  WARNING! Some data still exists for client {client_id}. Review above.\n")
    
    return all_clean

def main():
    """Main function"""
    
    # Get client_id from argument or default to 1 (Bajaj)
    if len(sys.argv) > 1:
        try:
            client_id = int(sys.argv[1])
        except ValueError:
            print("❌ Error: client_id must be a number")
            sys.exit(1)
    else:
        client_id = 1  # Default to Bajaj (client 1)
    
    print(f"\n🔍 Looking for data to remove for Client {client_id}...")
    
    # Show current state
    total_to_remove = show_client_stats(client_id)
    
    if total_to_remove == 0:
        print(f"  ✅ No data found for client {client_id}. Nothing to remove.\n")
        return
    
    # Confirm before deletion
    print("⚠️  WARNING: This will permanently delete all data!")
    response = input(f"\n  Continue with deletion? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("\n  ❌ Deletion cancelled.\n")
        return
    
    # Perform cleanup
    cleanup_client_projects(client_id)
    
    # Verify
    verify_removal(client_id)

if __name__ == "__main__":
    main()
