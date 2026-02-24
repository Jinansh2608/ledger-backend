#!/usr/bin/env python3
"""
Automatic Database Cleanup
Removes all test/temporary upload data while keeping important business records
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

def cleanup():
    """Auto-cleanup unnecessary data"""
    print("\n🧹 DATABASE CLEANUP - AUTO MODE\n" + "="*50)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Delete upload files
        print("\n  1️⃣  Removing upload files...")
        cur.execute("SELECT COUNT(*) as cnt FROM upload_file;")
        file_count = cur.fetchone()['cnt']
        if file_count > 0:
            cur.execute("DELETE FROM upload_file;")
            print(f"     ✅ Deleted {file_count} upload file records")
        else:
            print(f"     ℹ️  No upload files to delete")
        
        # Delete upload sessions
        print("\n  2️⃣  Removing upload sessions...")
        cur.execute("SELECT COUNT(*) as cnt FROM upload_session;")
        session_count = cur.fetchone()['cnt']
        if session_count > 0:
            cur.execute("DELETE FROM upload_session;")
            print(f"     ✅ Deleted {session_count} upload session records")
        else:
            print(f"     ℹ️  No upload sessions to delete")
        
        conn.commit()
        
        # Show final stats
        print("\n  3️⃣  Final database state:")
        tables = {
            "client": "Clients",
            "vendor": "Vendors",
            "project": "Projects",
            "site": "Sites",
            "client_po": "POs",
            "upload_file": "Upload Files",
            "upload_session": "Upload Sessions"
        }
        
        for table, desc in tables.items():
            cur.execute(f"SELECT COUNT(*) as cnt FROM {table};")
            cnt = cur.fetchone()['cnt']
            status = "✅" if cnt > 0 or table not in ["upload_file", "upload_session"] else "✅"
            print(f"     {status} {desc:.<25} {cnt} records")
        
        print("\n" + "="*50)
        print("✨ Cleanup complete! Database cleaned successfully.")
        print("="*50)
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during cleanup: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup()
