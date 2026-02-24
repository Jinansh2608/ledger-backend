"""
Enhanced PO Repository with support for:
1. Adding/managing line items
2. Linking multiple POs to same project
3. Verbal agreements
"""

from app.database import get_db
from datetime import date
from typing import List, Dict, Optional


# ==========================================
# LINE ITEMS MANAGEMENT
# ==========================================

def add_line_item(client_po_id: int, item_name: str, quantity: float, unit_price: float):
    """Add a new line item to an existing PO"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Calculate total price
                total_price = quantity * unit_price
                
                # Insert line item
                cur.execute("""
                    INSERT INTO client_po_line_item (
                        client_po_id,
                        item_name,
                        quantity,
                        unit_price,
                        total_price
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (client_po_id, item_name, quantity, unit_price, total_price))
                
                line_item_id = cur.fetchone()["id"]
                
                # Update PO value
                cur.execute("""
                    UPDATE client_po
                    SET po_value = po_value + %s,
                        receivable_amount = receivable_amount + %s
                    WHERE id = %s
                """, (total_price, total_price, client_po_id))
                
                return {
                    "line_item_id": line_item_id,
                    "item_name": item_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                }
    
    finally:
        conn.close()


def update_line_item(line_item_id: int, item_name: str = None, quantity: float = None, unit_price: float = None):
    """Update an existing line item"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Get current item to calculate difference
                cur.execute("""
                    SELECT client_po_id, total_price FROM client_po_line_item
                    WHERE id = %s
                """, (line_item_id,))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                client_po_id = result["client_po_id"]
                old_total = result["total_price"]
                
                # Build update query
                update_fields = []
                values = []
                
                if item_name is not None:
                    update_fields.append("item_name = %s")
                    values.append(item_name)
                
                if quantity is not None:
                    update_fields.append("quantity = %s")
                    values.append(quantity)
                
                if unit_price is not None:
                    update_fields.append("unit_price = %s")
                    values.append(unit_price)
                
                # Calculate new total if quantity or price changed
                if quantity is not None or unit_price is not None:
                    cur.execute("""
                        SELECT quantity, unit_price FROM client_po_line_item
                        WHERE id = %s
                    """, (line_item_id,))
                    
                    current = cur.fetchone()
                    new_qty = quantity if quantity is not None else current["quantity"]
                    new_price = unit_price if unit_price is not None else current["unit_price"]
                    new_total = new_qty * new_price
                    
                    update_fields.append("total_price = %s")
                    values.append(new_total)
                    
                    # Update PO value with difference
                    diff = new_total - old_total
                    cur.execute("""
                        UPDATE client_po
                        SET po_value = po_value + %s,
                            receivable_amount = receivable_amount + %s
                        WHERE id = %s
                    """, (diff, diff, client_po_id))
                
                values.append(line_item_id)
                
                if update_fields:
                    query = f"UPDATE client_po_line_item SET {', '.join(update_fields)} WHERE id = %s"
                    cur.execute(query, values)
                
                # Fetch updated item
                cur.execute("""
                    SELECT * FROM client_po_line_item WHERE id = %s
                """, (line_item_id,))
                
                item = cur.fetchone()
                return {
                    "line_item_id": item["id"],
                    "item_name": item["item_name"],
                    "quantity": float(item["quantity"]),
                    "unit_price": float(item["unit_price"]),
                    "total_price": float(item["total_price"])
                }
    
    finally:
        conn.close()


def delete_line_item(line_item_id: int):
    """Delete a line item and update PO total"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Get item details
                cur.execute("""
                    SELECT client_po_id, total_price FROM client_po_line_item
                    WHERE id = %s
                """, (line_item_id,))
                
                result = cur.fetchone()
                if not result:
                    return False
                
                client_po_id = result["client_po_id"]
                total_price = result["total_price"]
                
                # Delete line item
                cur.execute("DELETE FROM client_po_line_item WHERE id = %s", (line_item_id,))
                
                # Update PO value
                cur.execute("""
                    UPDATE client_po
                    SET po_value = po_value - %s,
                        receivable_amount = receivable_amount - %s
                    WHERE id = %s
                """, (total_price, total_price, client_po_id))
                
                return True
    
    finally:
        conn.close()


def get_line_items(client_po_id: int):
    """Get all line items for a PO"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, item_name, quantity, unit_price, total_price, hsn_code, unit, rate, gst_amount, gross_amount
                FROM client_po_line_item
                WHERE client_po_id = %s
                ORDER BY id
            """, (client_po_id,))
            
            items = cur.fetchall()
            return [
                {
                    "line_item_id": item["id"],
                    "item_name": item["item_name"],
                    "quantity": float(item["quantity"]) if item["quantity"] else None,
                    "unit_price": float(item["unit_price"]) if item["unit_price"] else None,
                    "total_price": float(item["total_price"]) if item["total_price"] else None,
                    "hsn_code": item.get("hsn_code"),
                    "unit": item.get("unit"),
                    "rate": float(item["rate"]) if item.get("rate") else None,
                    "gst_amount": float(item["gst_amount"]) if item.get("gst_amount") else None,
                    "gross_amount": float(item["gross_amount"]) if item.get("gross_amount") else None
                }
                for item in items
            ]
    
    finally:
        conn.close()


# ==========================================
# GET ALL POs
# ==========================================

def get_po_by_id(po_id: int):
    """Get a single PO by ID with all details"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            # Fetch PO header
            cur.execute("""
                SELECT 
                    cp.id,
                    cp.client_id,
                    cp.project_id,
                    cp.po_number,
                    cp.po_date,
                    cp.po_value,
                    cp.receivable_amount,
                    cp.status,
                    cp.po_type,
                    cp.parent_po_id,
                    cp.pi_number,
                    cp.pi_date,
                    cp.notes,
                    cp.created_at,
                    cp.store_id,
                    c.name as client_name,
                    p.name as project_name
                FROM client_po cp
                LEFT JOIN client c ON cp.client_id = c.id
                LEFT JOIN project p ON cp.project_id = p.id
                WHERE cp.id = %s
            """, (po_id,))
            
            po = cur.fetchone()
            if not po:
                return None
            
            # Fetch line items
            cur.execute("""
                SELECT id, item_name, quantity, unit_price, total_price, hsn_code, unit, rate, gst_amount, gross_amount
                FROM client_po_line_item
                WHERE client_po_id = %s
                ORDER BY id
            """, (po_id,))
            
            line_items = cur.fetchall()
            
            return {
                "id": po["id"],
                "client_po_id": po["id"],
                "client_id": po["client_id"],
                "client_name": po["client_name"],
                "project_id": po["project_id"],
                "project_name": po["project_name"],
                "store_id": po["store_id"],
                "po_number": po["po_number"],
                "po_date": po["po_date"].isoformat() if po["po_date"] else None,
                "po_value": float(po["po_value"]) if po["po_value"] else 0,
                "receivable_amount": float(po["receivable_amount"]) if po["receivable_amount"] else 0,
                "status": po["status"],
                "po_type": po["po_type"],
                "parent_po_id": po["parent_po_id"],
                "pi_number": po["pi_number"],
                "pi_date": po["pi_date"].isoformat() if po["pi_date"] else None,
                "notes": po["notes"],
                "created_at": po["created_at"].isoformat() if po["created_at"] else None,
                "line_items": [
                    {
                        "line_item_id": item["id"],
                        "item_name": item["item_name"],
                        "quantity": float(item["quantity"]) if item["quantity"] else None,
                        "unit_price": float(item["unit_price"]) if item["unit_price"] else None,
                        "total_price": float(item["total_price"]) if item["total_price"] else None,
                        "hsn_code": item.get("hsn_code"),
                        "unit": item.get("unit"),
                        "rate": float(item["rate"]) if item.get("rate") else None,
                        "gst_amount": float(item["gst_amount"]) if item.get("gst_amount") else None,
                        "gross_amount": float(item["gross_amount"]) if item.get("gross_amount") else None
                    }
                    for item in line_items
                ],
                "line_item_count": len(line_items)
            }
    
    finally:
        conn.close()


def get_all_pos(client_id: int = None):
    """Get all POs, optionally filtered by client_id. Aggregates POs with same store_id."""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            # Query with safe handling of optional columns (may not exist in old schema)
            if client_id:
                cur.execute("""
                    SELECT 
                        cp.id,
                        cp.client_id,
                        cp.project_id,
                        cp.po_number,
                        cp.po_date,
                        cp.po_value,
                        cp.receivable_amount,
                        cp.status,
                        cp.po_type,
                        cp.parent_po_id,
                        cp.pi_number,
                        cp.pi_date,
                        cp.notes,
                        cp.created_at,
                        cp.store_id,
                        c.name as client_name,
                        p.name as project_name
                    FROM client_po cp
                    LEFT JOIN client c ON cp.client_id = c.id
                    LEFT JOIN project p ON cp.project_id = p.id
                    WHERE cp.client_id = %s
                    ORDER BY cp.store_id DESC, cp.created_at DESC
                """, (client_id,))
            else:
                cur.execute("""
                    SELECT 
                        cp.id,
                        cp.client_id,
                        cp.project_id,
                        cp.po_number,
                        cp.po_date,
                        cp.po_value,
                        cp.receivable_amount,
                        cp.status,
                        cp.po_type,
                        cp.parent_po_id,
                        cp.pi_number,
                        cp.pi_date,
                        cp.notes,
                        cp.created_at,
                        cp.store_id,
                        c.name as client_name,
                        p.name as project_name
                    FROM client_po cp
                    LEFT JOIN client c ON cp.client_id = c.id
                    LEFT JOIN project p ON cp.project_id = p.id
                    ORDER BY cp.store_id DESC, cp.created_at DESC
                """)
            
            pos = cur.fetchall()
            
            # Aggregate POs with same store_id
            aggregated = {}
            for po in pos:
                store_key = po["store_id"] or po["id"]  # Use store_id if available, otherwise use po.id
                
                if store_key not in aggregated:
                    aggregated[store_key] = {
                        "id": po["id"],
                        "client_po_id": po["id"],
                        "client_id": po["client_id"],
                        "client_name": po["client_name"],
                        "project_id": po["project_id"],
                        "project_name": po["project_name"],
                        "store_id": po["store_id"],
                        "po_number": po["po_number"],
                        "po_date": po["po_date"].isoformat() if po["po_date"] else None,
                        "po_value": float(po["po_value"]) if po["po_value"] else 0,
                        "receivable_amount": float(po["receivable_amount"]) if po["receivable_amount"] else 0,
                        "status": po["status"],
                        "po_type": po["po_type"],
                        "parent_po_id": po["parent_po_id"],
                        "pi_number": po["pi_number"],
                        "pi_date": po["pi_date"].isoformat() if po["pi_date"] else None,
                        "notes": po["notes"],
                        "created_at": po["created_at"].isoformat() if po["created_at"] else None,
                        "line_count": 0,
                        "po_ids": [po["id"]]  # Track all PO IDs for same store

                    }
                else:
                    # Aggregate values for same store
                    aggregated[store_key]["po_value"] += float(po["po_value"]) if po["po_value"] else 0
                    aggregated[store_key]["receivable_amount"] += float(po["receivable_amount"]) if po["receivable_amount"] else 0
                    aggregated[store_key]["po_ids"].append(po["id"])

                    # If project info was missing in the first PO, try to fill it from this one
                    if not aggregated[store_key].get("project_name") and po.get("project_name"):
                         aggregated[store_key]["project_name"] = po["project_name"]
                         aggregated[store_key]["project_id"] = po["project_id"]

            
            return list(aggregated.values())
    
    finally:
        conn.close()


# ==========================================
# MULTIPLE POs PER PROJECT
# ==========================================

def create_po_for_project(client_id: int, project_id: int, po_number: str = None, po_date: date = None, 
                         po_value: float = 0, po_type: str = "standard", 
                         parent_po_id: int = None, is_primary: bool = False, 
                         notes: str = None):
    """Create a new PO for a project (can be linked to parent PO)"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Insert PO
                cur.execute("""
                    INSERT INTO client_po (
                        client_id,
                        project_id,
                        po_number,
                        po_date,
                        po_value,
                        receivable_amount,
                        status,
                        po_type,
                        parent_po_id,
                        notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (client_id, project_id, po_number, po_date, po_value, po_value, 
                      "pending", po_type, parent_po_id, notes))
                
                client_po_id = cur.fetchone()["id"]
                
                # Add to PO project mapping (is_primary and sequence_order don't exist in schema)
                cur.execute("""
                    INSERT INTO po_project_mapping (
                        project_id,
                        client_po_id
                    )
                    VALUES (%s, %s)
                """, (project_id, client_po_id))
                
                return client_po_id
    
    finally:
        conn.close()


def get_all_pos_for_project(project_id: int):
    """Get all POs linked to a project with their details"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            # Get project details (basic info only - location columns may not exist yet)
            try:
                cur.execute("""
                    SELECT name FROM project WHERE id = %s
                """, (project_id,))
                project_info = cur.fetchone()
            except:
                project_info = None
            
            cur.execute("""
                SELECT 
                    cp.id,
                    cp.po_number,
                    cp.po_date,
                    cp.po_value,
                    cp.status,
                    cp.po_type,
                    cp.parent_po_id,
                    cp.notes,
                    cp.store_id
                FROM client_po cp
                LEFT JOIN po_project_mapping ppm ON cp.id = ppm.client_po_id AND ppm.project_id = %s
                WHERE ppm.project_id = %s OR cp.project_id = %s
                ORDER BY cp.created_at
            """, (project_id, project_id, project_id))
            
            pos = cur.fetchall()
            result = []
            
            for po in pos:
                # Get line items for each PO
                cur.execute("""
                    SELECT id, item_name, quantity, unit_price, total_price, hsn_code, unit, rate, gst_amount, gross_amount
                    FROM client_po_line_item
                    WHERE client_po_id = %s
                """, (po["id"],))
                
                line_items = cur.fetchall()
                
                result.append({
                    "po_id": po["id"],
                    "po_number": po["po_number"],
                    "po_date": po["po_date"].isoformat() if po["po_date"] else None,
                    "po_value": float(po["po_value"]) if po["po_value"] else 0,
                    "status": po["status"],
                    "po_type": po["po_type"],
                    "parent_po_id": po["parent_po_id"],
                    "notes": po["notes"],
                    "store_id": po["store_id"],
                    "line_items": [
                        {
                            "line_item_id": item["id"],
                            "item_name": item["item_name"],
                            "quantity": float(item["quantity"]) if item["quantity"] else None,
                            "unit_price": float(item["unit_price"]) if item["unit_price"] else None,
                            "total_price": float(item["total_price"]) if item["total_price"] else None,
                            "hsn_code": item.get("hsn_code"),
                            "unit": item.get("unit"),
                            "rate": float(item["rate"]) if item.get("rate") else None,
                            "gst_amount": float(item["gst_amount"]) if item.get("gst_amount") else None,
                            "gross_amount": float(item["gross_amount"]) if item.get("gross_amount") else None
                        }
                        for item in line_items
                    ],
                    "line_item_count": len(line_items)
                })
            
            return result
    
    finally:
        conn.close()


def attach_po_to_project(client_po_id: int, project_id: int, sequence_order: int = None):
    """Attach an existing PO to a project (sequence_order parameter ignored - not in schema)"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Check if already mapped
                cur.execute("""
                    SELECT id FROM po_project_mapping
                    WHERE project_id = %s AND client_po_id = %s
                """, (project_id, client_po_id))
                
                if cur.fetchone():
                    return {"error": "PO already attached to this project"}
                
                # Insert mapping (sequence_order doesn't exist in schema)
                cur.execute("""
                    INSERT INTO po_project_mapping (
                        project_id,
                        client_po_id
                    )
                    VALUES (%s, %s)
                """, (project_id, client_po_id))

                # Also update the direct project_id in client_po for simpler lookups
                cur.execute("""
                    UPDATE client_po
                    SET project_id = %s
                    WHERE id = %s
                """, (project_id, client_po_id))
                
                return {"status": "success"}
    
    finally:
        conn.close()


def set_primary_po(client_po_id: int, project_id: int):
    """Set a PO as primary for a project (Feature not available in current schema)"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Note: is_primary column doesn't exist in po_project_mapping table
                # This feature is not currently supported by the database schema
                # Simply verify the PO is attached to the project
                cur.execute("""
                    SELECT id FROM po_project_mapping
                    WHERE project_id = %s AND client_po_id = %s
                """, (project_id, client_po_id))
                
                if not cur.fetchone():
                    return {"error": "PO not attached to this project"}
                
                # Return success - primary PO concept not implemented in schema
                return {"status": "success", "note": "PO is attached to project. Primary PO feature not available in current schema."}
    
    finally:
        conn.close()


# ==========================================
# VERBAL AGREEMENTS
# ==========================================

def create_verbal_agreement(client_id: int, project_id: int, pi_number: str, 
                           pi_date: date, value: float = 0, notes: str = None):
    """Create a verbal agreement with PI number (PO number added later when issued)"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Insert as verbal_agreement type with PI number (no PO number yet)
                cur.execute("""
                    INSERT INTO client_po (
                        client_id,
                        project_id,
                        pi_number,
                        pi_date,
                        po_value,
                        receivable_amount,
                        status,
                        po_type,
                        notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (client_id, project_id, pi_number, pi_date, value, 
                      value, "pending", "verbal_agreement", notes))
                
                agreement_id = cur.fetchone()["id"]
                
                # Add to project mapping
                cur.execute("""
                    INSERT INTO po_project_mapping (
                        project_id,
                        client_po_id
                    )
                    VALUES (%s, %s)
                """, (project_id, agreement_id))
                
                return agreement_id
    
    finally:
        conn.close()


def get_verbal_agreements_for_project(project_id: int):
    """Get all verbal agreements for a project"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    cp.id,
                    cp.pi_number,
                    cp.pi_date,
                    cp.po_number,
                    cp.po_date,
                    cp.po_value,
                    cp.status,
                    cp.notes,
                    cp.created_at
                FROM client_po cp
                JOIN po_project_mapping ppm ON cp.id = ppm.client_po_id
                WHERE ppm.project_id = %s AND cp.po_type = 'verbal_agreement'
                ORDER BY cp.pi_date DESC
            """, (project_id,))
            
            agreements = cur.fetchall()
            return [
                {
                    "agreement_id": a["id"],
                    "pi_number": a["pi_number"],
                    "pi_date": a["pi_date"].isoformat() if a["pi_date"] else None,
                    "po_number": a["po_number"],  # Will be NULL until PO is issued
                    "po_date": a["po_date"].isoformat() if a["po_date"] else None,
                    "value": float(a["po_value"]) if a["po_value"] else 0,
                    "status": a["status"],
                    "has_po": a["po_number"] is not None,  # Indicates if PO has been issued
                    "notes": a["notes"],
                    "created_at": a["created_at"].isoformat()
                }
                for a in agreements
            ]
    
    finally:
        conn.close()


def update_po_details(client_po_id: int, po_number: str = None, po_date: date = None,
                      po_value: float = None, pi_number: str = None, pi_date: date = None,
                      notes: str = None, status: str = None):
    """Update existing PO details (for alterations after Excel upload)"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Check if PO exists
                cur.execute("SELECT id FROM client_po WHERE id = %s", (client_po_id,))
                if not cur.fetchone():
                    return None
                
                # Build update query dynamically
                update_fields = []
                values = []
                
                if po_number is not None:
                    update_fields.append("po_number = %s")
                    values.append(po_number)
                
                if po_date is not None:
                    update_fields.append("po_date = %s")
                    values.append(po_date)
                
                if po_value is not None:
                    update_fields.append("po_value = %s")
                    values.append(po_value)
                    update_fields.append("receivable_amount = %s")
                    values.append(po_value)
                
                if pi_number is not None:
                    update_fields.append("pi_number = %s")
                    values.append(pi_number)
                
                if pi_date is not None:
                    update_fields.append("pi_date = %s")
                    values.append(pi_date)
                
                if notes is not None:
                    update_fields.append("notes = %s")
                    values.append(notes)
                
                if status is not None:
                    update_fields.append("status = %s")
                    values.append(status)
                
                if not update_fields:
                    # Nothing to update, return current data
                    cur.execute("SELECT * FROM client_po WHERE id = %s", (client_po_id,))
                    po = cur.fetchone()
                    return _format_po_result(po)
                
                values.append(client_po_id)
                query = f"UPDATE client_po SET {', '.join(update_fields)} WHERE id = %s"
                cur.execute(query, values)
                
                # Fetch updated PO
                cur.execute("SELECT * FROM client_po WHERE id = %s", (client_po_id,))
                po = cur.fetchone()
                return _format_po_result(po)
    
    finally:
        conn.close()


def add_po_to_verbal_agreement(agreement_id: int, po_number: str, po_date: date):
    """Add PO number to an existing verbal agreement once PO is issued"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Check if it's a verbal agreement
                cur.execute("""
                    SELECT id, pi_number FROM client_po 
                    WHERE id = %s AND po_type = 'verbal_agreement'
                """, (agreement_id,))
                
                agreement = cur.fetchone()
                if not agreement:
                    return None
                
                # Update with PO number
                cur.execute("""
                    UPDATE client_po
                    SET po_number = %s, po_date = %s
                    WHERE id = %s
                """, (po_number, po_date, agreement_id))
                
                return {
                    "agreement_id": agreement_id,
                    "pi_number": agreement["pi_number"],
                    "po_number": po_number,
                    "po_date": po_date.isoformat()
                }
    
    finally:
        conn.close()


def _format_po_result(po):
    """Helper function to format PO result"""
    return {
        "client_po_id": po["id"],
        "po_number": po["po_number"],
        "po_date": po["po_date"].isoformat() if po["po_date"] else None,
        "po_value": float(po["po_value"]) if po["po_value"] else 0,
        "pi_number": po.get("pi_number"),
        "pi_date": po["pi_date"].isoformat() if po.get("pi_date") else None,
        "status": po["status"],
        "po_type": po.get("po_type", "standard"),
        "notes": po.get("notes")
    }


# ==========================================
# DELETE PO
# ==========================================

def delete_po(client_po_id: int):
    """
    Delete a PO and all associated data:
    - Payments (client_payment)
    - Billing PO data
    - Vendor order data
    - Documents
    - Line items
    - Project mappings
    - The PO itself
    
    Returns: True if successful, False if not found
    """
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Check if PO exists
                cur.execute("SELECT id, project_id FROM client_po WHERE id = %s", (client_po_id,))
                po_row = cur.fetchone()
                if not po_row:
                    return False
                
                project_id = po_row["project_id"]
                
                # 1. Delete client payments for this PO
                cur.execute("SAVEPOINT sp_payments")
                try:
                    cur.execute("DELETE FROM client_payment WHERE client_po_id = %s", (client_po_id,))
                    cur.execute("RELEASE SAVEPOINT sp_payments")
                except:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_payments")
                
                # 2. Delete billing PO data linked to this PO's project
                cur.execute("SAVEPOINT sp_billing")
                try:
                    cur.execute("""
                        DELETE FROM billing_po_line_item 
                        WHERE billing_po_id IN (
                            SELECT id FROM billing_po WHERE client_po_id = %s
                        )
                    """, (client_po_id,))
                    cur.execute("DELETE FROM billing_po WHERE client_po_id = %s", (client_po_id,))
                    cur.execute("RELEASE SAVEPOINT sp_billing")
                except:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_billing")
                
                # 3. Delete vendor order data if linked
                cur.execute("SAVEPOINT sp_vendor")
                try:
                    cur.execute("""
                        DELETE FROM payment_vendor_link 
                        WHERE vendor_order_id IN (
                            SELECT id FROM vendor_order WHERE client_po_id = %s
                        )
                    """, (client_po_id,))
                    cur.execute("""
                        DELETE FROM vendor_payment 
                        WHERE vendor_order_id IN (
                            SELECT id FROM vendor_order WHERE client_po_id = %s
                        )
                    """, (client_po_id,))
                    cur.execute("""
                        DELETE FROM vendor_order_line_item 
                        WHERE vendor_order_id IN (
                            SELECT id FROM vendor_order WHERE client_po_id = %s
                        )
                    """, (client_po_id,))
                    cur.execute("DELETE FROM vendor_order WHERE client_po_id = %s", (client_po_id,))
                    cur.execute("RELEASE SAVEPOINT sp_vendor")
                except:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_vendor")
                
                # 4. Delete documents
                cur.execute("SAVEPOINT sp_docs")
                try:
                    cur.execute("DELETE FROM document WHERE client_po_id = %s", (client_po_id,))
                    cur.execute("RELEASE SAVEPOINT sp_docs")
                except:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_docs")
                
                # 5. Delete line items
                cur.execute("DELETE FROM client_po_line_item WHERE client_po_id = %s", (client_po_id,))
                
                # 6. Delete project mappings
                cur.execute("DELETE FROM po_project_mapping WHERE client_po_id = %s", (client_po_id,))
                
                # 7. Delete the PO itself
                cur.execute("DELETE FROM client_po WHERE id = %s", (client_po_id,))
                
                return True
    
    finally:
        conn.close()



# ==========================================
# CREATE PROJECT
# ==========================================

def create_project(name: str, location: str = None, city: str = None, state: str = None, 
                  country: str = None, latitude: float = None, longitude: float = None):
    """
    Create a new project
    
    Returns: Project ID if successful, None if project already exists
    """
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Check if project already exists
                cur.execute("SELECT id FROM project WHERE name = %s", (name,))
                if cur.fetchone():
                    return None  # Project already exists
                
                # Create new project
                cur.execute("""
                    INSERT INTO project (name, location, city, state, country, latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, location, city, state, country, latitude, longitude))
                
                project_id = cur.fetchone()["id"]
                return project_id
    
    finally:
        conn.close()


# ==========================================
# DELETE PROJECT
# ==========================================

def delete_project(project_name: str):
    """
    Delete a project and all associated data:
    - All payments for the project POs
    - All billing PO data
    - All vendor order data
    - All POs for the project
    - All line items for those POs
    - All project mappings
    - All related documents
    - The project itself
    
    Returns: Dict with status and details
    """
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # 1. Find the project by name
                cur.execute("SELECT id FROM project WHERE name = %s", (project_name,))
                project = cur.fetchone()
                
                if not project:
                    return {"success": False, "error": f"Project '{project_name}' not found"}
                
                project_id = project["id"]
                
                # 2. Find all POs for this project
                cur.execute("""
                    SELECT DISTINCT cp.id
                    FROM client_po cp
                    LEFT JOIN po_project_mapping ppm ON cp.id = ppm.client_po_id
                    WHERE cp.project_id = %s OR ppm.project_id = %s
                """, (project_id, project_id))
                
                po_ids = [row["id"] for row in cur.fetchall()]
                
                # 3. Delete all data associated with these POs (correct FK order)
                for po_id in po_ids:
                    # Delete client payments for this PO
                    cur.execute("SAVEPOINT sp_payment")
                    try:
                        cur.execute("DELETE FROM client_payment WHERE client_po_id = %s", (po_id,))
                        cur.execute("RELEASE SAVEPOINT sp_payment")
                    except:
                        cur.execute("ROLLBACK TO SAVEPOINT sp_payment")
                    
                    # Delete line items
                    cur.execute("""
                        DELETE FROM client_po_line_item 
                        WHERE client_po_id = %s
                    """, (po_id,))
                    
                    # Delete documents
                    cur.execute("SAVEPOINT sp_doc")
                    try:
                        cur.execute("""
                            DELETE FROM document 
                            WHERE client_po_id = %s
                        """, (po_id,))
                        cur.execute("RELEASE SAVEPOINT sp_doc")
                    except:
                        cur.execute("ROLLBACK TO SAVEPOINT sp_doc")
                
                # 4. Delete billing PO data for this project
                cur.execute("SAVEPOINT sp_billing")
                try:
                    cur.execute("""
                        DELETE FROM billing_po_line_item 
                        WHERE billing_po_id IN (
                            SELECT id FROM billing_po WHERE project_id = %s
                        )
                    """, (project_id,))
                    cur.execute("DELETE FROM billing_po WHERE project_id = %s", (project_id,))
                    cur.execute("RELEASE SAVEPOINT sp_billing")
                except:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_billing")
                
                # 5. Delete vendor order data for this project
                cur.execute("SAVEPOINT sp_vendor")
                try:
                    cur.execute("""
                        DELETE FROM payment_vendor_link 
                        WHERE vendor_order_id IN (
                            SELECT id FROM vendor_order WHERE project_id = %s
                        )
                    """, (project_id,))
                    cur.execute("""
                        DELETE FROM vendor_payment 
                        WHERE vendor_order_id IN (
                            SELECT id FROM vendor_order WHERE project_id = %s
                        )
                    """, (project_id,))
                    cur.execute("""
                        DELETE FROM vendor_order_line_item 
                        WHERE vendor_order_id IN (
                            SELECT id FROM vendor_order WHERE project_id = %s
                        )
                    """, (project_id,))
                    cur.execute("DELETE FROM vendor_order WHERE project_id = %s", (project_id,))
                    cur.execute("RELEASE SAVEPOINT sp_vendor")
                except:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_vendor")
                
                # 6. Delete all project mappings
                cur.execute("SAVEPOINT sp_mapping")
                try:
                    cur.execute("""
                        DELETE FROM po_project_mapping 
                        WHERE project_id = %s
                    """, (project_id,))
                    cur.execute("RELEASE SAVEPOINT sp_mapping")
                except:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_mapping")
                
                # 7. Delete all POs for this project
                cur.execute("""
                    DELETE FROM client_po 
                    WHERE project_id = %s
                """, (project_id,))
                
                # 8. Delete the project itself
                cur.execute("""
                    DELETE FROM project 
                    WHERE id = %s
                """, (project_id,))
                
                return {
                    "success": True,
                    "message": f"Project '{project_name}' and all associated data deleted successfully",
                    "project_id": project_id,
                    "pos_deleted": len(po_ids)
                }
    
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    finally:
        conn.close()


# ==========================================
# STORE_ID AGGREGATION (BUNDLED POs)
# ==========================================

def get_pos_aggregated_by_store(client_id: int = None):
    """
    Get POs aggregated by store_id with bundled line items.
    
    When multiple POs have the same store_id:
    - They are grouped together as a single bundle
    - Line items from all POs are combined
    - A 'bundled_po_ids' field shows which POs are included
    - A 'is_bundled' flag indicates if multiple POs are bundled
    
    Returns list of bundles with aggregated data.
    """
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            # Get all POs with their line items
            if client_id:
                cur.execute("""
                    SELECT 
                        cp.id,
                        cp.client_id,
                        cp.project_id,
                        cp.po_number,
                        cp.po_date,
                        cp.po_value,
                        cp.receivable_amount,
                        cp.status,
                        cp.po_type,
                        cp.pi_number,
                        cp.pi_date,
                        cp.notes,
                        cp.created_at,
                        cp.store_id,
                        c.name as client_name,
                        p.name as project_name
                    FROM client_po cp
                    LEFT JOIN client c ON cp.client_id = c.id
                    LEFT JOIN project p ON cp.project_id = p.id
                    WHERE cp.client_id = %s
                    ORDER BY cp.store_id DESC, cp.created_at DESC
                """, (client_id,))
            else:
                cur.execute("""
                    SELECT 
                        cp.id,
                        cp.client_id,
                        cp.project_id,
                        cp.po_number,
                        cp.po_date,
                        cp.po_value,
                        cp.receivable_amount,
                        cp.status,
                        cp.po_type,
                        cp.pi_number,
                        cp.pi_date,
                        cp.notes,
                        cp.created_at,
                        cp.store_id,
                        c.name as client_name,
                        p.name as project_name
                    FROM client_po cp
                    LEFT JOIN client c ON cp.client_id = c.id
                    LEFT JOIN project p ON cp.project_id = p.id
                    ORDER BY cp.store_id DESC, cp.created_at DESC
                """)
            
            pos = cur.fetchall()
            
            # Group POs by store_id
            bundles = {}
            for po in pos:
                store_key = po["store_id"] or f"no_store_{po['id']}"
                
                if store_key not in bundles:
                    bundles[store_key] = {
                        "bundle_id": store_key,
                        "client_id": po["client_id"],
                        "client_name": po["client_name"],
                        "project_id": po["project_id"],
                        "project_name": po["project_name"],
                        "store_id": po["store_id"],
                        "po_numbers": [],
                        "po_ids": [],
                        "po_dates": [],
                        "total_po_value": 0.0,
                        "total_receivable": 0.0,
                        "statuses": [],
                        "pi_numbers": [],
                        "pi_dates": [],
                        "notes_list": [],
                        "created_at": po["created_at"].isoformat() if po["created_at"] else None,
                        "line_items": [],
                        "is_bundled": False,
                        "bundled_po_ids": []
                    }
                
                # Add PO data to bundle
                bundles[store_key]["po_numbers"].append(po["po_number"])
                bundles[store_key]["po_ids"].append(po["id"])
                bundles[store_key]["bundled_po_ids"].append(po["id"])
                if po["po_date"]:
                    bundles[store_key]["po_dates"].append(po["po_date"].isoformat())
                bundles[store_key]["total_po_value"] += float(po["po_value"]) if po["po_value"] else 0
                bundles[store_key]["total_receivable"] += float(po["receivable_amount"]) if po["receivable_amount"] else 0
                bundles[store_key]["statuses"].append(po["status"])
                if po["pi_number"]:
                    bundles[store_key]["pi_numbers"].append(po["pi_number"])
                if po["pi_date"]:
                    bundles[store_key]["pi_dates"].append(po["pi_date"].isoformat())
                if po["notes"]:
                    bundles[store_key]["notes_list"].append(po["notes"])
                
                # Fetch line items for this PO
                cur.execute("""
                    SELECT
                        id,
                        client_po_id,
                        item_name,
                        quantity,
                        unit_price,
                        total_price,
                        hsn_code,
                        unit,
                        rate,
                        gst_amount,
                        gross_amount,
                        taxable_amount,
                        created_at
                    FROM client_po_line_item
                    WHERE client_po_id = %s
                    ORDER BY id ASC
                """, (po["id"],))
                
                line_items = cur.fetchall()
                for item in line_items:
                    line_item_dict = {
                        "id": item["id"],
                        "client_po_id": item["client_po_id"],
                        "item_name": item["item_name"],
                        "quantity": float(item["quantity"]) if item["quantity"] else 0,
                        "unit_price": float(item["unit_price"]) if item["unit_price"] else 0,
                        "total_price": float(item["total_price"]) if item["total_price"] else 0,
                        "hsn_code": item["hsn_code"],
                        "unit": item["unit"],
                        "rate": float(item["rate"]) if item["rate"] else 0,
                        "gst_amount": float(item["gst_amount"]) if item["gst_amount"] else 0,
                        "gross_amount": float(item["gross_amount"]) if item["gross_amount"] else 0,
                        "taxable_amount": float(item["taxable_amount"]) if item["taxable_amount"] else 0,
                    }
                    bundles[store_key]["line_items"].append(line_item_dict)
            
            # Post-process: mark bundles that have multiple POs
            for store_key, bundle in bundles.items():
                bundle["is_bundled"] = len(bundle["po_ids"]) > 1
                if bundle["is_bundled"]:
                    # Create a bundling note
                    bundle["bundling_note"] = f"This bundle contains {len(bundle['po_ids'])} POs combined together: {', '.join(bundle['po_numbers'])}"
                else:
                    bundle["bundling_note"] = None
            
            return list(bundles.values())
    
    finally:
        conn.close()
