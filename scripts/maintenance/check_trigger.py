#!/usr/bin/env python3
"""
Check what trigger is actually in the database
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
    # Get trigger function source
    cur.execute("""
        SET search_path TO "Finances";
        SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'update_upload_stats';
    """)
    result = cur.fetchone()
    if result:
        print("Trigger Function Definition:")
        print("=" * 70)
        print(result[0])
        print("=" * 70)
    else:
        print("[NO] Trigger function not found")

conn.close()
