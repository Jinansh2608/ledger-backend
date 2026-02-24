from app.database import get_db

def check_po(po_number):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            print(f"--- Checking PO: {po_number} ---")
            cur.execute("SELECT id, project_id, po_number, client_id, store_id FROM client_po WHERE po_number = %s", (po_number,))
            po = cur.fetchone()
            if po:
                print(f"PO found: ID={po['id']}, ProjectID={po['project_id']}, ClientID={po['client_id']}, StoreID={po['store_id']}")
                
                # Check mapping
                cur.execute("SELECT project_id FROM po_project_mapping WHERE client_po_id = %s", (po['id'],))
                mappings = cur.fetchall()
                print(f"Mappings in po_project_mapping: {mappings}")
                
                # Check project existence
                if po['project_id']:
                    cur.execute("SELECT id, name FROM project WHERE id = %s", (po['project_id'],))
                    proj = cur.fetchone()
                    print(f"Linked Project: {proj}")
                elif not mappings:
                    print("WARNING: No project link in client_po OR po_project_mapping!")
            else:
                print("PO NOT found in client_po table.")
                # Maybe it's bundled? Check if it exists as part of a bundle or pi_number
                cur.execute("SELECT id, project_id, po_number, pi_number FROM client_po WHERE pi_number = %s", (po_number,))
                po_pi = cur.fetchone()
                if po_pi:
                    print(f"Found as PI: ID={po_pi['id']}, ProjectID={po_pi['project_id']}, PO Number={po_pi['po_number']}")
                else:
                    print("Checked pi_number as well - not found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_po("4100130800")
