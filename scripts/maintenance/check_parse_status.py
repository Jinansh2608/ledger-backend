#!/usr/bin/env python3
"""Check which files failed to parse"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db

conn = get_db()
with conn.cursor() as cursor:
    # Count files with metadata
    cursor.execute("""
       SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN metadata IS NOT NULL THEN 1 END) as with_metadata,
            COUNT(CASE WHEN metadata IS NULL THEN 1 END) as no_metadata,
            COUNT(CASE WHEN metadata->>'parsed' = 'true' THEN 1 END) as parsed_success,
            COUNT(CASE WHEN metadata->>'parsed' != 'true' THEN 1 END) as parsed_failed,
            COUNT(CASE WHEN metadata->>'line_items' IS NOT NULL THEN 1 END) as has_lineitem_key
        FROM "Finances"."upload_file"
    """)
    result = cursor.fetchone()
    
    print("=" * 70)
    print("UPLOAD_FILE TABLE STATISTICS")
    print("=" * 70)
    print()
    if isinstance(result, dict):
        print(f"Total files: {result['total']}")
        print(f"Files with metadata: {result['with_metadata']}")
        print(f"Files without metadata: {result['no_metadata']}")
        print(f"Successfully parsed (metadata->'parsed' = true): {result['parsed_success']}")
        print(f"Failed/No parse status: {result['parsed_failed']}")
        print(f"Have 'line_items' in metadata: {result['has_lineitem_key']}")
    else:
        print(f"Total files: {result[0]}")
        print(f"Files with metadata: {result[1]}")
        print(f"Files without metadata: {result[2]}")
        print(f"Successfully parsed (metadata->'parsed' = true): {result[3]}")
        print(f"Failed/No parse status: {result[4]}")
        print(f"Have 'line_items' in metadata: {result[5]}")
    print()
    
    # Get files with metadata but no line_items
    print("=" * 70)
    print("FILES WITH SUCCESSFUL PARSE BUT NO LINE ITEMS")
    print("=" * 70)
    cursor.execute("""
        SELECT id, original_filename, metadata->>'parser_type', metadata->>'line_item_count'
        FROM "Finances"."upload_file"
        WHERE metadata IS NOT NULL 
        AND metadata->>'parsed' = 'true'
        AND (metadata->>'line_items' IS NULL 
             OR metadata->>'line_items' = '[]'
             OR metadata->>'line_items' = 'null')
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    if rows:
        print(f"Found {len(rows)} files:")
        for row in rows:
            try:
                if isinstance(row, dict):
                    id_val = row.get('id')
                    name = row.get('original_filename')
                    parser = row.get('parser_type', 'N/A')
                    count = row.get('line_item_count', 'N/A')
                    print(f"  - {name} (ID: {id_val}, Parser: {parser}, Count: {count})")
                else:
                    print(f"  - {row[1]} (ID: {row[0]}, Parser: {row[2] or 'N/A'}, Count: {row[3] or 'N/A'})")
            except Exception as e:
                print(f"  - [ERROR parsing row: {e}]")
    else:
        print("None found")
    
    print()
    print("=" * 70)
    print("FILES WITH NO METADATA AT ALL (PARSING FAILED)")
    print("=" * 70)
    cursor.execute("""
        SELECT id, original_filename, created_at
        FROM "Finances"."upload_file"
        WHERE metadata IS NULL
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    if rows:
        print(f"Found {len(rows)} files with parse errors:")
        for row in rows:
            if isinstance(row, dict):
                print(f"  - {row['original_filename']} (ID: {row['id']}, Uploaded: {row['created_at']})")
            else:
                print(f"  - {row[1]} (ID: {row[0]}, Uploaded: {row[2]})")
    else:
        print("None found")

conn.close()
