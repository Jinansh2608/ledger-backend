import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db

def debug_linkage():
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                print("\n--- Project Linkage Debug ---")
                
                # Get the link
                cur.execute("""
                    SELECT 
                        p.id as project_id,
                        cp.id as client_po_id,
                        pm.status as payment_status,
                        pm.amount,
                        pm.transaction_type,
                        ppm.id as mapping_id
                    FROM client_payment pm
                    JOIN client_po cp ON pm.client_po_id = cp.id
                    LEFT JOIN po_project_mapping ppm ON cp.id = ppm.client_po_id
                    LEFT JOIN project p ON ppm.project_id = p.id
                    LIMIT 5
                """)
                
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                    
                # Test the aggregate query manually for project_id that appears above
                if rows:
                    pid = rows[0]['project_id']
                    if pid:
                        print(f"\nTesting aggregation for Project {pid}...")
                        cur.execute("""
                            SELECT 
                                SUM(CASE WHEN cp.transaction_type = 'debit' THEN -cp.amount ELSE cp.amount END) as total_collected
                            FROM client_payment cp
                            JOIN client_po cpo ON cp.client_po_id = cpo.id
                            JOIN po_project_mapping ppm ON cpo.id = ppm.client_po_id
                            WHERE ppm.project_id = %s AND cp.status = 'cleared'
                        """, (pid,))
                        result = cur.fetchone()
                        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_linkage()
