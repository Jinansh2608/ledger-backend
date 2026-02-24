import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db

def inspect_db():
    print("Inspecting client_payment table...")
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Check columns
                cur.execute("""
                    SELECT column_name, data_type, column_default 
                    FROM information_schema.columns 
                    WHERE table_schema = 'Finances' AND table_name = 'client_payment';
                """)
                columns = cur.fetchall()
                print("\nColumns:")
                for col in columns:
                    print(f"- {col['column_name']} ({col['data_type']}) Default: {col['column_default']}")
                
                # Check recent payments
                print("\nRecent Payments:")
                cur.execute("SELECT id, amount, status, transaction_type, created_at FROM client_payment ORDER BY created_at DESC LIMIT 5")
                payments = cur.fetchall()
                for p in payments:
                    print(f"ID: {p['id']}, Amount: {p['amount']}, Status: '{p['status']}', Type: '{p['transaction_type']}'")
                
                if not payments:
                    print("No payments found.")
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_db()
