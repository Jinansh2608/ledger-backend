#!/usr/bin/env python3
"""
Database Diagnostic Tool - Verify and fix schema issues
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

def connect_db():
    """Connect to database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"[ERROR] Cannot connect to database: {e}")
        return None

def check_table_exists(conn, table_name):
    """Check if table exists"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'Finances' AND table_name = %s
            );
        """, (table_name,))
        result = cur.fetchone()
        return result['exists'] if result else False

def get_table_columns(conn, table_name):
    """Get all columns in a table"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'Finances' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        return cur.fetchall()

def check_trigger_exists(conn, trigger_name):
    """Check if trigger exists"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.triggers
                WHERE trigger_schema = 'Finances' AND trigger_name = %s
            );
        """, (trigger_name,))
        result = cur.fetchone()
        return result['exists'] if result else False

def get_trigger_definition(conn, trigger_name):
    """Get trigger function definition"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT pg_get_triggerdef(oid) 
            FROM pg_trigger
            WHERE tgname = %s;
        """, (trigger_name,))
        result = cur.fetchone()
        return result[0] if result else None

def diagnose():
    """Run full diagnosis"""
    print("=" * 70)
    print("DATABASE DIAGNOSTIC TOOL")
    print("=" * 70)
    print()

    conn = connect_db()
    if not conn:
        return

    try:
        # Check tables
        print("[CHECK 1] Checking Upload Session Table...")
        if check_table_exists(conn, 'upload_session'):
            print("[OK] upload_session table exists")
            cols = get_table_columns(conn, 'upload_session')
            print(f"    Columns: {len(cols)}")
            for col in cols:
                print(f"      - {col['column_name']}: {col['data_type']}")
        else:
            print("[FAIL] upload_session table NOT FOUND")

        print()
        print("[CHECK 2] Checking Upload File Table...")
        if check_table_exists(conn, 'upload_file'):
            print("[OK] upload_file table exists")
            cols = get_table_columns(conn, 'upload_file')
            print(f"    Columns: {len(cols)}")
            for col in cols:
                print(f"      - {col['column_name']}: {col['data_type']}")
        else:
            print("[FAIL] upload_file table NOT FOUND")

        print()
        print("[CHECK 3] Checking Upload Stats Table...")
        if check_table_exists(conn, 'upload_stats'):
            print("[OK] upload_stats table exists")
            cols = get_table_columns(conn, 'upload_stats')
            print(f"    Columns: {len(cols)}")
            for col in cols:
                print(f"      - {col['column_name']}: {col['data_type']}")
            
            # Check for session_id column
            col_names = [col['column_name'] for col in cols]
            if 'session_id' in col_names:
                print("[OK] session_id column exists")
            else:
                print("[FAIL] session_id column MISSING - This is the bug!")
        else:
            print("[FAIL] upload_stats table NOT FOUND")

        print()
        print("[CHECK 4] Checking Trigger...")
        if check_trigger_exists(conn, 'trigger_update_upload_stats'):
            print("[OK] trigger_update_upload_stats exists")
            defn = get_trigger_definition(conn, 'trigger_update_upload_stats')
            if defn:
                print(f"    Definition: {defn[:100]}...")
        else:
            print("[FAIL] trigger_update_upload_stats NOT FOUND")

        print()
        print("[CHECK 5] Checking Function...")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.routines
                    WHERE routine_schema = 'Finances' AND routine_name = 'update_upload_stats'
                );
            """)
            result = cur.fetchone()
            if result['exists']:
                print("[OK] update_upload_stats function exists")
            else:
                print("[FAIL] update_upload_stats function NOT FOUND")

        print()
        print("=" * 70)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR] During diagnosis: {e}")
    finally:
        conn.close()

def fix_schema():
    """Attempt to fix schema issues"""
    print()
    print("=" * 70)
    print("ATTEMPTING TO FIX SCHEMA")
    print("=" * 70)
    print()

    conn = connect_db()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Step 1: Add missing session_id column to upload_stats if needed
            print("[STEP 1] Checking if session_id column missing...")
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns
                    WHERE table_schema = 'Finances'
                    AND table_name = 'upload_stats'
                    AND column_name = 'session_id'
                );
            """)
            result = cur.fetchone()
            
            if not result['exists']:
                print("[ACTION] Adding session_id column to upload_stats...")
                cur.execute("""
                    ALTER TABLE upload_stats
                    ADD COLUMN session_id VARCHAR(36) NOT NULL DEFAULT gen_random_uuid()::text;
                """)
                conn.commit()
                print("[OK] Column added successfully")
            else:
                print("[OK] session_id column already exists")

            # Step 2: Create index on session_id
            print()
            print("[STEP 2] Checking for session_id index...")
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.statistics
                    WHERE table_schema = 'Finances'
                    AND table_name = 'upload_stats'
                    AND column_name = 'session_id'
                );
            """)
            result = cur.fetchone()
            
            if not result['exists']:
                print("[ACTION] Creating index on session_id...")
                cur.execute("""
                    CREATE INDEX idx_upload_stats_session_id ON upload_stats(session_id);
                """)
                conn.commit()
                print("[OK] Index created")
            else:
                print("[OK] Index already exists")

            # Step 3: Verify trigger
            print()
            print("[STEP 3] Checking trigger function...")
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.triggers
                    WHERE trigger_schema = 'Finances'
                    AND trigger_name = 'trigger_update_upload_stats'
                );
            """)
            result = cur.fetchone()
            
            if result['exists']:
                print("[OK] Trigger exists")
            else:
                print("[ACTION] Recreating trigger...")
                cur.execute("""
                    CREATE OR REPLACE FUNCTION update_upload_stats() RETURNS TRIGGER AS $$
                    BEGIN
                        INSERT INTO upload_stats (id, session_id, total_uploads, total_size_bytes)
                        VALUES (gen_random_uuid()::text, NEW.session_id, 1, NEW.file_size)
                        ON CONFLICT (session_id) DO UPDATE SET
                            total_uploads = total_uploads + 1,
                            total_size_bytes = total_size_bytes + NEW.file_size,
                            last_activity = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                cur.execute("""
                    DROP TRIGGER IF EXISTS trigger_update_upload_stats ON upload_file;
                """)
                
                cur.execute("""
                    CREATE TRIGGER trigger_update_upload_stats
                    AFTER INSERT ON upload_file
                    FOR EACH ROW
                    EXECUTE FUNCTION update_upload_stats();
                """)
                conn.commit()
                print("[OK] Trigger recreated")

        print()
        print("=" * 70)
        print("SCHEMA FIX COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR] During fix: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print()
    diagnose()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        fix_schema()
    else:
        print()
        print("To attempt automatic fixes, run:")
        print("  python diagnose_db_schema.py --fix")
        print()
