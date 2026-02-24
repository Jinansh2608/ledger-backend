#!/usr/bin/env python3
"""Check upload_file schema"""

from app.database import get_db
from app.config import settings

conn = get_db()
try:
    with conn.cursor() as cur:
        # Get upload_file table structure
        cur.execute('''
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = %s
            ORDER BY ordinal_position
        ''', ('upload_file', settings.DB_SCHEMA))
        
        print('\n=== upload_file table ===')
        rows = cur.fetchall()
        if rows:
            for row in rows:
                col_name = row.get('column_name') or row[0]
                data_type = row.get('data_type') or row[1]
                print(f'  {col_name}: {data_type}')
        else:
            print('  Table does not exist!')
finally:
    conn.close()
