#!/usr/bin/env python3
"""
Remove orphaned records left from cleanup
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

def cleanup_orphans():
    print("\n" + "="*70)
    print("  🧹 REMOVING ORPHANED RECORDS")
    print("="*70 + "\n")
    
    orphan_tables = [
        ("client_po_line_item", "No client_po parent"),
        ("upload_stats", "Old upload stats"),
        ("project_document", "No project parent"),
    ]
    
    for table, description in orphan_tables:
        try:
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
            cur = conn.cursor()
            cur.execute('SET search_path TO "Finances";')
            
            cur.execute(f'DELETE FROM "{table}";')
            removed = cur.rowcount
            conn.commit()
            conn.close()
            
            if removed > 0:
                print(f"  ✅ {table:.<40} Deleted {removed:>6} orphaned records")
            else:
                print(f"  ℹ️  {table:.<40} No orphaned records")
                
        except Exception as e:
            print(f"  ⚠️  {table:.<40} {str(e)[:30]}")
    
    print()

if __name__ == "__main__":
    cleanup_orphans()
