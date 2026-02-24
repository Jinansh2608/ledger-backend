#!/usr/bin/env python3
"""
Get the trigger_initialize_upload_stats trigger definition
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
    # Get trigger definition
    cur.execute("""
        SET search_path TO "Finances";
        SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname = 'trigger_initialize_upload_stats';
    """)
    
    result = cur.fetchone()
    if result:
        print("trigger_initialize_upload_stats Definition:")
        print("=" * 70)
        print(result[0])
        print("=" * 70)
        
        # Also get the function
        cur.execute("""
            SET search_path TO "Finances";
            SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'initialize_upload_stats';
        """)
        func_result = cur.fetchone()
        if func_result:
            print("\nFunction Definition:")
            print("=" * 70)
            print(func_result[0])
            print("=" * 70)
    else:
        print("Trigger not found")

conn.close()
