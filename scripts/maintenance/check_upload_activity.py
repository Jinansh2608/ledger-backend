#!/usr/bin/env python3
"""Check upload activity"""

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host='localhost', port=5432, dbname='Nexgen_erp',
    user='postgres', password='toor', cursor_factory=RealDictCursor
)

try:
    cur = conn.cursor()
    cur.execute('SET search_path TO "Finances"')
    
    print("=" * 80)
    print("UPLOAD ACTIVITY CHECK")
    print("=" * 80)
    print()
    
    # Check upload_file table
    cur.execute('SELECT COUNT(*) as count FROM upload_file')
    file_count = cur.fetchone()['count']
    print(f"📁 Total files uploaded: {file_count}")
    
    if file_count > 0:
        print()
        print("Recent uploads:")
        cur.execute('''
            SELECT original_filename, upload_timestamp, metadata 
            FROM upload_file 
            ORDER BY upload_timestamp DESC 
            LIMIT 5
        ''')
        files = cur.fetchall()
        for i, f in enumerate(files, 1):
            print(f"  {i}. {f['original_filename']}")
            print(f"     Time: {f['upload_timestamp']}")
            print(f"     Metadata: {f['metadata']}")
    
    print()
    
    # Check sessions
    cur.execute('SELECT COUNT(*) as count FROM upload_session')
    session_count = cur.fetchone()['count']
    print(f"🔗 Total sessions: {session_count}")
    
    if session_count > 0:
        print()
        print("Recent sessions:")
        cur.execute('''
            SELECT session_id, created_at, metadata 
            FROM upload_session 
            ORDER BY created_at DESC 
            LIMIT 3
        ''')
        sessions = cur.fetchall()
        for i, s in enumerate(sessions, 1):
            print(f"  {i}. Session: {s['session_id'][:8]}...")
            print(f"     Created: {s['created_at']}")
            print(f"     Metadata: {s['metadata']}")
    
    print()
    print("=" * 80)
    
    # Check client_po again
    cur.execute('SELECT COUNT(*) as count FROM client_po')
    po_count = cur.fetchone()['count']
    print(f"📊 POs in database: {po_count}")
    print()
    
    if file_count > 0 and po_count == 0:
        print("⚠️  FILES UPLOADED BUT NO POs CREATED")
        print()
        print("Possible issues:")
        print("  1. Files uploaded but parsing not triggered")
        print("  2. Parsing failed silently")
        print("  3. auto_parse not enabled in upload")
        print("  4. client_id not in session metadata")
        print()
        print("ACTION: Check backend logs for parse errors")
    elif po_count > 0:
        print("✅ POs ARE BEING CREATED!")
        print(f"    {po_count} POs successfully saved")
    else:
        print("⚠️  No uploads and no POs")
        print("    Check if frontend is actually sending files")
    
    print("=" * 80)
    
    cur.close()
    
finally:
    conn.close()
