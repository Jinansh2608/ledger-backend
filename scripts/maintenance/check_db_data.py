#!/usr/bin/env python3
"""
Script to check what data is in the database
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Nexgen_erp",
    "user": "postgres",
    "password": "toor"
}

def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def check_database():
    """Check what data exists in the database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        # Set schema to Finances
        cur.execute('SET search_path TO "Finances";')
        
        # Get all tables in Finances schema
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'Finances' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print("=" * 80)
        print("DATABASE INVENTORY - Nexgen_erp (Finances schema)")
        print("=" * 80)
        print()
        
        if not tables:
            print("❌ No tables found in Finances schema")
            return
        
        print(f"✅ Found {len(tables)} tables\n")
        
        table_data = {}
        
        for table_row in tables:
            table_name = table_row['table_name']
            
            # Get row count
            cur.execute(f'SELECT COUNT(*) as count FROM "{table_name}";')
            count = cur.fetchone()['count']
            
            # Get column info
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            
            table_data[table_name] = {
                'count': count,
                'columns': columns
            }
            
            # Get sample data
            if count > 0:
                cur.execute(f'SELECT * FROM "{table_name}" LIMIT 5;')
                samples = cur.fetchall()
                table_data[table_name]['samples'] = samples
        
        # Print summary
        for table_name, info in table_data.items():
            count = info['count']
            columns = info['columns']
            
            print(f"📊 TABLE: {table_name}")
            print(f"   Rows: {count}")
            print(f"   Columns: {len(columns)}")
            
            # Print column names and types
            print("   Schema:")
            for col in columns:
                print(f"      - {col['column_name']}: {col['data_type']}")
            
            # Print sample data
            if 'samples' in info and info['samples']:
                print(f"   Sample Data (showing up to 5 rows):")
                for i, sample in enumerate(info['samples'], 1):
                    print(f"      Row {i}:")
                    for key, value in sample.items():
                        if value is None:
                            print(f"         {key}: NULL")
                        elif isinstance(value, (int, float, str, bool)):
                            print(f"         {key}: {value}")
                        elif isinstance(value, datetime):
                            print(f"         {key}: {value.isoformat()}")
                        else:
                            print(f"         {key}: {str(value)[:100]}")
            
            print()
        
        # Print summary statistics
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        total_rows = sum(info['count'] for info in table_data.values())
        print(f"Total tables: {len(table_data)}")
        print(f"Total rows across all tables: {total_rows}")
        print()
        
        # Show which tables have data
        tables_with_data = [name for name, info in table_data.items() if info['count'] > 0]
        tables_empty = [name for name, info in table_data.items() if info['count'] == 0]
        
        if tables_with_data:
            print("✅ Tables with data:")
            for table in tables_with_data:
                print(f"   - {table}: {table_data[table]['count']} rows")
        
        if tables_empty:
            print("\n⚠️  Empty tables:")
            for table in tables_empty:
                print(f"   - {table}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
