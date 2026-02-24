#!/usr/bin/env python3
"""
List ALL triggers in Finances schema
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
    # Get all triggers
    cur.execute("""
        SET search_path TO "Finances";
        SELECT trigger_name, event_manipulation, event_object_table
        FROM information_schema.triggers
        WHERE trigger_schema = 'Finances'
        ORDER BY event_object_table;
    """)
    
    results = cur.fetchall()
    if results:
        print("ALL TRIGGERS in Finances schema:")
        print("=" * 70)
        for row in results:
            print(f"Trigger: {row[0]}")
            print(f"Event: {row[1]} on table {row[2]}")
            print()
    else:
        print("[NO] No triggers found")

conn.close()
