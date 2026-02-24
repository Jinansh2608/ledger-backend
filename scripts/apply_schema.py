import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database Configuration (Hardcoded as seen in app/config.py)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Nexgen_erp",
    "user": "postgres",
    "password": "toor"
}

SCHEMA_NAME = "Finances"
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migrations")

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def run_sql_file(cursor, filepath):
    print(f"Applying {os.path.basename(filepath)}...")
    with open(filepath, 'r') as f:
        sql = f.read()
        try:
            cursor.execute(sql)
            print("  Success.")
        except Exception as e:
            print(f"  Error applying {os.path.basename(filepath)}: {e}")

def check_table_exists(cursor, table_name):
    cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = '{SCHEMA_NAME}' AND table_name = '{table_name}');")
    return cursor.fetchone()[0]

def main():
    conn = get_connection()
    if not conn:
        return

    cur = conn.cursor()

    # Create Schema if not exists
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS \"{SCHEMA_NAME}\";")
    
    # Check if base tables exist
    client_exists = check_table_exists(cur, 'client')
    
    if not client_exists:
        print("Base tables missing. Running db.sql...")
        db_sql_path = os.path.join(MIGRATIONS_DIR, "db.sql")
        if os.path.exists(db_sql_path):
            run_sql_file(cur, db_sql_path)
        else:
            print("Warning: migrations/db.sql not found!")
    else:
        print("Base tables detected. Skipping db.sql.")

    # Apply migrations in order
    migrations = [
        "0001_add_project_document_client_po.sql",
        "0002_add_transaction_type.sql",
        "0003_consolidated_enhancements.sql",
        "0004_add_billing_po.sql"
    ]

    for mig in migrations:
        path = os.path.join(MIGRATIONS_DIR, mig)
        if os.path.exists(path):
            run_sql_file(cur, path)
        else:
            print(f"Warning: Migration {mig} not found!")

    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    main()
