#!/usr/bin/env python3
"""
Export only clients from Nexgen_erp database to SQL file
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'Nexgen_erp',
    'user': 'postgres',
    'password': 'toor'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def export_clients():
    """Export client table data and all schemas to SQL file"""
    print("\n" + "="*80)
    print("  📦 DATABASE EXPORT (CLIENTS ONLY) - Nexgen_erp")
    print("="*80 + "\n")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Set search path
    cur.execute('SET search_path TO "Finances";')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Nexgen_erp_clients_backup_{timestamp}.sql"
    
    # Tables to keep data for
    data_tables = ['client']
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("-- =====================================================\n")
            f.write("-- NEXGEN ERP CLIENTS-ONLY BACKUP\n")
            f.write(f"-- Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- Database: Nexgen_erp\n")
            f.write("-- Schema: Finances\n")
            f.write("-- Only 'client' table data included\n")
            f.write("-- =====================================================\n\n")
            
            f.write("-- Set search path\n")
            f.write('SET search_path TO "Finances";\n\n')
            
            # Get all tables in the schema
            cur.execute('''
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'Finances'
                ORDER BY table_name
            ''')
            
            tables = [row['table_name'] for row in cur.fetchall()]
            print(f"✅ Found {len(tables)} tables in schema\n")
            
            for table in tables:
                print(f"  📋 Processing {table}...", end=" ")
                
                # Get table structure
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'Finances' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                
                columns = cur.fetchall()
                column_names = [col['column_name'] for col in columns]
                
                # Write table header
                f.write(f"-- Table: {table}\n")
                f.write(f"DROP TABLE IF EXISTS \"{table}\" CASCADE;\n")
                
                f.write(f"CREATE TABLE \"{table}\" (\n")
                col_defs = []
                for col in columns:
                    col_def = f'    \"{col["column_name"]}\" {col["data_type"]}'
                    if col['column_default']:
                        col_def += f" DEFAULT {col['column_default']}"
                    if col['is_nullable'] == 'NO':
                        col_def += " NOT NULL"
                    col_defs.append(col_def)
                f.write(",\n".join(col_defs))
                f.write("\n);\n\n")
                
                # Export data ONLY if it's in data_tables
                if table in data_tables:
                    cur.execute(f'SELECT * FROM "Finances"."{table}"')
                    rows = cur.fetchall()
                    if rows:
                        print(f"Exporting {len(rows)} records", end=" ")
                        for row in rows:
                            cols = ", ".join([f'"{c}"' for c in column_names])
                            vals = []
                            for col in column_names:
                                val = row[col]
                                if val is None:
                                    vals.append("NULL")
                                elif isinstance(val, (int, float)):
                                    vals.append(str(val))
                                elif isinstance(val, bool):
                                    vals.append("TRUE" if val else "FALSE")
                                else:
                                    # Basic string escaping
                                    escaped = str(val).replace("'", "''")
                                    vals.append(f"'{escaped}'")
                            
                            vals_str = ", ".join(vals)
                            f.write(f"INSERT INTO \"{table}\" ({cols}) VALUES ({vals_str});\n")
                        f.write("\n")
                    else:
                        print("No records found", end=" ")
                else:
                    print("Skipping data (project data excluded)", end=" ")
                
                print("✅")
            
            print(f"\n✨ Export complete! File saved as: {filename}")
            
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    export_clients()
