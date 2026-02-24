#!/usr/bin/env python3
"""
List all triggers on upload_file table
"""

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Nexgen_erp",
    "user": "postgres",
    "password": "toor"
}

conn = psycopg2.connect(**DB_CONFIG)
with conn.cursor() as cur:
    # Get all triggers on upload_file
    cur.execute("""
        SET search_path TO "Finances";
        SELECT trigger_name, event_manipulation, event_object_table
        FROM information_schema.triggers
        WHERE event_object_table = 'upload_file' AND trigger_schema = 'Finances';
    """)
    
    results = cur.fetchall()
    if results:
        print("Triggers on upload_file table:")
        print("=" * 70)
        for row in results:
            print(f"Trigger: {row[0]}")
            print(f"Event: {row[1]}")
            print(f"Table: {row[2]}")
            print()
            
            # Get trigger definition
            cur.execute(f"""
                SET search_path TO "Finances";
                SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname = '{row[0]}';
            """)
            trig_def = cur.fetchone()
            if trig_def:
                print(f"Definition: {trig_def[0][:200]}...")
                print("-" * 70)
    else:
        print("[NO] No triggers found on upload_file table")

conn.close()
