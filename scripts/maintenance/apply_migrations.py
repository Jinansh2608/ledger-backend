#!/usr/bin/env python3
"""Apply upload tables migration"""
from app.database import get_db
import os

migration_file = 'migrations/0006_create_upload_tables.sql'

# Read migration file
with open(migration_file, 'r') as f:
    sql = f.read()

# Execute migration
conn = get_db()
try:
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("✓ Migration applied successfully")
    print("✓ Created upload_session table")
    print("✓ Created upload_file table")
    print("✓ Created upload_stats table")
    print("✓ Created trigger for upload_stats")
except Exception as e:
    conn.rollback()
    print(f"✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
