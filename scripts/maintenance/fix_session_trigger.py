#!/usr/bin/env python3
"""
Fix the initialize_upload_stats trigger to use correct columns
"""

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Nexgen_erp",
    "user": "postgres",
    "password": "toor"
}

print("=" * 70)
print("FIXING initialize_upload_stats TRIGGER")
print("=" * 70)
print()

try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    with conn.cursor() as cur:
        cur.execute('SET search_path TO "Finances";')
        
        # Drop the old trigger
        print("[STEP 1] Dropping old trigger...")
        cur.execute("""
            DROP TRIGGER IF EXISTS trigger_initialize_upload_stats ON upload_session;
        """)
        print("[OK] Trigger dropped")
        
        # Drop the old function
        print("[STEP 2] Dropping old function...")
        cur.execute("""
            DROP FUNCTION IF EXISTS initialize_upload_stats();
        """)
        print("[OK] Function dropped")
        
        # Create new function with correct column names
        print("[STEP 3] Creating new function with correct columns...")
        cur.execute("""
            SET search_path TO "Finances";
            CREATE OR REPLACE FUNCTION initialize_upload_stats()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO upload_stats (session_id, total_files, total_size_bytes, last_updated)
                VALUES (NEW.session_id, 0, 0, CURRENT_TIMESTAMP)
                ON CONFLICT (session_id) DO NOTHING;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("[OK] Function created")
        
        # Create new trigger
        print("[STEP 4] Creating new trigger...")
        cur.execute("""
            SET search_path TO "Finances";
            CREATE TRIGGER trigger_initialize_upload_stats
            AFTER INSERT ON upload_session
            FOR EACH ROW
            EXECUTE FUNCTION initialize_upload_stats();
        """)
        print("[OK] Trigger created")
        
    conn.close()
    
    print()
    print("=" * 70)
    print("TRIGGER FIX COMPLETE")
    print("=" * 70)
    print()
    print("[INFO] Now run the tests again:")
    print("       python test_all_routes.py")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
