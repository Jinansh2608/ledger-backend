"""
Project repository - handles all project-related database operations
"""
from app.database import get_db
from typing import Optional, List, Dict


def get_all_projects(skip: int = 0, limit: int = 50):
    """Get all projects with pagination"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, location, city, state, country, latitude, longitude
                FROM project
                ORDER BY id DESC
                OFFSET %s LIMIT %s
            """, (skip, limit))
            projects = cur.fetchall()
            return projects
    finally:
        conn.close()


def get_project_by_id(project_id: int):
    """Get a specific project by ID"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, location, city, state, country, latitude, longitude
                FROM project
                WHERE id = %s
            """, (project_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_project_by_name(name: str):
    """Get a specific project by name"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, location, city, state, country, latitude, longitude
                FROM project
                WHERE name = %s
            """, (name,))
            return cur.fetchone()
    finally:
        conn.close()


def create_project(name: str, location: Optional[str] = None, city: Optional[str] = None, 
                   state: Optional[str] = None, country: Optional[str] = None, 
                   latitude: Optional[float] = None, longitude: Optional[float] = None):
    """Create a new project"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO project (name, location, city, state, country, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, name, location, city, state, country, latitude, longitude
            """, (name, location, city, state, country, latitude, longitude))
            conn.commit()
            return cur.fetchone()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_project(project_id: int, **kwargs):
    """Update a project"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            allowed_fields = ['name', 'location', 'city', 'state', 'country', 'latitude', 'longitude']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
            
            if not updates:
                cur.execute("""
                    SELECT id, name, location, city, state, country, latitude, longitude
                    FROM project
                    WHERE id = %s
                """, (project_id,))
                return cur.fetchone()
            
            set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [project_id]
            
            cur.execute(f"""
                UPDATE project
                SET {set_clause}
                WHERE id = %s
                RETURNING id, name, location, city, state, country, latitude, longitude
            """, values)
            conn.commit()
            return cur.fetchone()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_project_by_id(project_id: int) -> bool:
    """Delete a project by ID"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Check if project exists
            cur.execute("SELECT id FROM project WHERE id = %s", (project_id,))
            if not cur.fetchone():
                return False
            
            # Delete client payments for all POs in this project
            cur.execute("SAVEPOINT sp_payments")
            try:
                cur.execute("""
                    DELETE FROM client_payment WHERE client_po_id IN (
                        SELECT id FROM client_po WHERE project_id = %s
                    )
                """, (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_payments")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_payments")
            
            # Delete vendor data
            cur.execute("SAVEPOINT sp_vendor")
            try:
                cur.execute("DELETE FROM payment_vendor_link WHERE vendor_order_id IN (SELECT id FROM vendor_order WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM vendor_payment WHERE vendor_order_id IN (SELECT id FROM vendor_order WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM vendor_order_line_item WHERE vendor_order_id IN (SELECT id FROM vendor_order WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM vendor_order WHERE project_id = %s", (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_vendor")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_vendor")
            
            # Delete billing PO data
            cur.execute("SAVEPOINT sp_billing")
            try:
                cur.execute("DELETE FROM billing_po_line_item WHERE billing_po_id IN (SELECT id FROM billing_po WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM billing_po WHERE project_id = %s", (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_billing")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_billing")
            
            # Delete PO line items
            cur.execute("SAVEPOINT sp_lineitems")
            try:
                cur.execute("""
                    DELETE FROM client_po_line_item WHERE client_po_id IN (
                        SELECT id FROM client_po WHERE project_id = %s
                    )
                """, (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_lineitems")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_lineitems")
            
            # Delete project mappings
            cur.execute("SAVEPOINT sp_mappings")
            try:
                cur.execute("DELETE FROM po_project_mapping WHERE project_id = %s", (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_mappings")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_mappings")
            
            cur.execute("DELETE FROM client_po WHERE project_id = %s", (project_id,))
            cur.execute("DELETE FROM project WHERE id = %s", (project_id,))
            conn.commit()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_project_by_name(name: str) -> bool:
    """Delete a project by name"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Get the project ID
            cur.execute("SELECT id FROM project WHERE name = %s", (name,))
            project = cur.fetchone()
            if not project:
                return False
            
            project_id = project['id']
            
            # Delete client payments for all POs in this project
            cur.execute("SAVEPOINT sp_payments")
            try:
                cur.execute("""
                    DELETE FROM client_payment WHERE client_po_id IN (
                        SELECT id FROM client_po WHERE project_id = %s
                    )
                """, (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_payments")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_payments")
            
            # Delete vendor data
            cur.execute("SAVEPOINT sp_vendor")
            try:
                cur.execute("DELETE FROM payment_vendor_link WHERE vendor_order_id IN (SELECT id FROM vendor_order WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM vendor_payment WHERE vendor_order_id IN (SELECT id FROM vendor_order WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM vendor_order_line_item WHERE vendor_order_id IN (SELECT id FROM vendor_order WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM vendor_order WHERE project_id = %s", (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_vendor")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_vendor")
            
            # Delete billing PO data
            cur.execute("SAVEPOINT sp_billing")
            try:
                cur.execute("DELETE FROM billing_po_line_item WHERE billing_po_id IN (SELECT id FROM billing_po WHERE project_id = %s)", (project_id,))
                cur.execute("DELETE FROM billing_po WHERE project_id = %s", (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_billing")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_billing")
            
            # Delete PO line items
            cur.execute("SAVEPOINT sp_lineitems")
            try:
                cur.execute("""
                    DELETE FROM client_po_line_item WHERE client_po_id IN (
                        SELECT id FROM client_po WHERE project_id = %s
                    )
                """, (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_lineitems")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_lineitems")
            
            # Delete project mappings
            cur.execute("SAVEPOINT sp_mappings")
            try:
                cur.execute("DELETE FROM po_project_mapping WHERE project_id = %s", (project_id,))
                cur.execute("RELEASE SAVEPOINT sp_mappings")
            except:
                cur.execute("ROLLBACK TO SAVEPOINT sp_mappings")
            
            cur.execute("DELETE FROM client_po WHERE project_id = %s", (project_id,))
            cur.execute("DELETE FROM project WHERE id = %s", (project_id,))
            conn.commit()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def search_projects(search_term: str):
    """Search projects by name or location"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            search_pattern = f"%{search_term}%"
            cur.execute("""
                SELECT id, name, location, city, state, country, latitude, longitude
                FROM project
                WHERE name ILIKE %s OR location ILIKE %s
                ORDER BY id DESC
            """, (search_pattern, search_pattern))
            return cur.fetchall()
    finally:
        conn.close()
