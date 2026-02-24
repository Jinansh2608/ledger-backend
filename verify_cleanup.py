#!/usr/bin/env python3
"""
Verify database structure after cleanup
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

conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
cur = conn.cursor()
cur.execute('SET search_path TO "Finances";')

print("\n" + "="*70)
print("  📊 DATABASE STRUCTURE - AFTER CLEANUP")
print("="*70 + "\n")

# Get all tables
cur.execute("""SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'Finances' ORDER BY table_name;""")

tables = cur.fetchall()

print("  REMAINING TABLES AND DATA:\n")

for row in tables:
    table = row['table_name']
    try:
        cur.execute(f'SELECT COUNT(*) as cnt FROM "{table}";')
        count = cur.fetchone()['cnt']
        print(f"  • {table:.<40} {count:>6} records")
    except:
        print(f"  • {table:.<40} (unable to read)")

print("\n" + "="*70)
print("  ✅ DATABASE SUMMARY")
print("="*70 + "\n")

# Summary stats
cur.execute('SELECT COUNT(*) as cnt FROM client;')
client_count = cur.fetchone()['cnt']

cur.execute('SELECT COUNT(*) as cnt FROM vendor;')
vendor_count = cur.fetchone()['cnt']

cur.execute('SELECT COUNT(*) as cnt FROM project;')
project_count = cur.fetchone()['cnt']

print(f"  ✅ Clients (KEPT):        {client_count} records")
print(f"  ✅ Vendors (KEPT):        {vendor_count} records")
print(f"  ✅ Projects (REMOVED):    {project_count} records")

if project_count == 0:
    print(f"\n  🎉 Successfully cleaned! Ready for new data.\n")
else:
    print(f"\n  ⚠️  {project_count} projects still in database!\n")

conn.close()
