import psycopg2
import os
from dotenv import load_dotenv

# Use absolute paths
BASE_DIR = r"c:\Users\Hitansh\Desktop\Nexgen\Finances\Backend"
load_dotenv(os.path.join(BASE_DIR, '.env'))

def run_migration():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "Nexgen_erp")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "toor")
    
    print(f"Connecting to {database} on {host}...")
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cur = conn.cursor()
        
        migration_file = os.path.join(BASE_DIR, 'migrations', 'v2_quotation_and_vendor_master.sql')
        with open(migration_file, 'r') as f:
            sql = f.read()
            
        print("Executing migration...")
        cur.execute(sql)
        conn.commit()
        print("Migration successful!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_migration()
