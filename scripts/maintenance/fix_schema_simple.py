#!/usr/bin/env python3
"""
Fix database schema - simpler approach
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

def fix_schema():
    """Fix the database schema"""
    
    print("=" * 70)
    print("DATABASE SCHEMA FIX - Simple Approach")
    print("=" * 70)
    print()
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cur:
            # Ensure we're in the right schema
            cur.execute('SET search_path TO "Finances";')
            
            # Step 1: Check if session_id column exists
            print("[STEP 1] Checking session_id column in upload_stats...")
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'Finances' AND table_name = 'upload_stats' 
                AND column_name = 'session_id';
            """)
            
            if not cur.fetchone():
                print("[ACTION] Adding session_id column...")
                try:
                    cur.execute("""
                        ALTER TABLE "Finances"."upload_stats"
                        ADD COLUMN session_id VARCHAR(36) UNIQUE;
                    """)
                    print("[OK] Column added")
                except Exception as e:
                    print(f"[WARN] Error adding column: {e}")
                    # Try alternative
                    try:
                        cur.execute('SET search_path TO "Finances";')
                        cur.execute("""
                            ALTER TABLE upload_stats
                            ADD COLUMN session_id VARCHAR(36) UNIQUE;
                        """)
                        print("[OK] Column added (using unqualified name)")
                    except Exception as e2:
                        print(f"[ERROR] Could not add column: {e2}")
            else:
                print("[OK] session_id column already exists")
            
            # Step 2: Add FOREIGN KEY constraint if missing
            print()
            print("[STEP 2] Checking foreign key constraint...")
            try:
                cur.execute("""
                    SET search_path TO "Finances";
                    ALTER TABLE upload_stats
                    ADD CONSTRAINT fk_upload_stats_session_id
                    FOREIGN KEY (session_id) REFERENCES upload_session(session_id) 
                    ON DELETE CASCADE;
                """)
                print("[OK] Foreign key constraint added")
            except Exception as e:
                if "already exists" in str(e):
                    print("[OK] Constraint already exists")
                else:
                    print(f"[WARN] {e}")
            
            # Step 3: Create the function
            print()
            print("[STEP 3] Creating/updating trigger function...")
            try:
                cur.execute('SET search_path TO "Finances";')
                cur.execute("""
                    CREATE OR REPLACE FUNCTION update_upload_stats() 
                    RETURNS TRIGGER AS $$
                    BEGIN
                        UPDATE upload_stats 
                        SET total_files = total_files + 1,
                            total_size_bytes = total_size_bytes + COALESCE(NEW.file_size, 0),
                            last_updated = CURRENT_TIMESTAMP
                        WHERE session_id = NEW.session_id;
                        
                        IF NOT FOUND THEN
                            INSERT INTO upload_stats (session_id, total_files, total_size_bytes, last_updated)
                            VALUES (NEW.session_id, 1, COALESCE(NEW.file_size, 0), CURRENT_TIMESTAMP)
                            ON CONFLICT DO NOTHING;
                        END IF;
                        
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                print("[OK] Function created/updated")
            except Exception as e:
                print(f"[ERROR] Could not create function: {e}")
            
            # Step 4: Create the trigger
            print()
            print("[STEP 4] Creating/updating trigger...")
            try:
                cur.execute('SET search_path TO "Finances";')
                cur.execute("""
                    DROP TRIGGER IF EXISTS trigger_update_upload_stats ON upload_file;
                """)
                
                cur.execute("""
                    CREATE TRIGGER trigger_update_upload_stats
                    AFTER INSERT ON upload_file
                    FOR EACH ROW
                    EXECUTE FUNCTION update_upload_stats();
                """)
                print("[OK] Trigger created")
            except Exception as e:
                print(f"[ERROR] Could not create trigger: {e}")
        
        conn.close()
        
        print()
        print("=" * 70)
        print("SCHEMA FIX COMPLETE")
        print("=" * 70)
        print()
        print("[INFO] Run tests again with:")
        print("       python test_all_routes.py")
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    fix_schema()
