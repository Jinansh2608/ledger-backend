"""
Billing PO Repository
Handles database operations for billing POs and final billing workflows
"""

from app.database import get_db
from typing import Dict, Optional, List, Any
from datetime import datetime
import uuid


# ==========================================
# BILLING PO OPERATIONS
# ==========================================

def create_billing_po(
    client_po_id: int,
    project_id: int,
    po_number: str,
    billed_value: float,
    billed_gst: float = 0.0,
    billing_notes: str = None
) -> Optional[Dict[str, Any]]:
    """Create a new billing PO"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                billing_total = billed_value + billed_gst
                
                cur.execute("""
                    INSERT INTO billing_po 
                    (client_po_id, project_id, po_number, billed_value, billed_gst, billed_total, billing_notes, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'FINAL')
                    RETURNING id, client_po_id, project_id, po_number, billed_value, billed_gst, 
                              billed_total, billing_notes, status, created_at, updated_at
                """, (
                    client_po_id,
                    project_id,
                    po_number,
                    billed_value,
                    billed_gst,
                    billing_total,
                    billing_notes
                ))
                
                return cur.fetchone()
    finally:
        conn.close()


def add_billing_line_item(
    billing_po_id: str,
    description: str,
    qty: float,
    rate: float
) -> Optional[Dict[str, Any]]:
    """Add a line item to billing PO"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                total = qty * rate
                
                cur.execute("""
                    INSERT INTO billing_po_line_item 
                    (billing_po_id, description, qty, rate, total)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, billing_po_id, description, qty, rate, total, created_at
                """, (
                    billing_po_id,
                    description,
                    qty,
                    rate,
                    total
                ))
                
                return cur.fetchone()
    finally:
        conn.close()


def get_billing_po(billing_po_id: str) -> Optional[Dict[str, Any]]:
    """Get billing PO with all details"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get billing PO
                cur.execute("""
                    SELECT id, client_po_id, project_id, po_number, billed_value, billed_gst,
                           billed_total, billing_notes, status, created_at, updated_at
                    FROM billing_po
                    WHERE id = %s
                """, (billing_po_id,))
                
                billing_po = cur.fetchone()
                if not billing_po:
                    return None
                
                # Get line items
                cur.execute("""
                    SELECT id, billing_po_id, description, qty, rate, total, created_at
                    FROM billing_po_line_item
                    WHERE billing_po_id = %s
                    ORDER BY created_at
                """, (billing_po_id,))
                
                line_items = cur.fetchall()
                
                return {
                    "billing_po": billing_po,
                    "line_items": line_items or []
                }
    finally:
        conn.close()


def get_project_billing_po(project_id: int) -> Optional[Dict[str, Any]]:
    """Get the active billing PO for a project"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, client_po_id, project_id, po_number, billed_value, billed_gst,
                           billed_total, billing_notes, status, created_at, updated_at
                    FROM billing_po
                    WHERE project_id = %s AND status = 'FINAL'
                    LIMIT 1
                """, (project_id,))
                
                return cur.fetchone()
    finally:
        conn.close()


def get_project_billing_summary(project_id: int) -> Optional[Dict[str, Any]]:
    """Get comprehensive billing summary for a project"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get original PO details
                cur.execute("""
                    SELECT COALESCE(SUM(po_value), 0) as original_po_value,
                           COALESCE(SUM(total_tax), 0) as original_tax,
                           COALESCE(SUM(po_value), 0) as original_total
                    FROM client_po
                    WHERE project_id = %s
                """, (project_id,))
                
                original = cur.fetchone()
                
                # Get billing PO details
                cur.execute("""
                    SELECT COALESCE(SUM(billed_value), 0) as billed_value,
                           COALESCE(SUM(billed_gst), 0) as billed_gst,
                           COALESCE(SUM(billed_total), 0) as billed_total,
                           COUNT(*) as billing_po_count
                    FROM billing_po
                    WHERE project_id = %s AND status = 'FINAL'
                """, (project_id,))
                
                billing = cur.fetchone()
                
                # Get vendor costs
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as vendor_total
                    FROM vendor_order
                    WHERE project_id = %s
                """, (project_id,))
                
                vendor = cur.fetchone()
                
                # Calculate P&L
                original_total = original['original_total'] or 0
                billed_total = billing['billed_total'] or 0
                vendor_total = vendor['vendor_total'] or 0
                
                profit = billed_total - vendor_total
                margin_percent = ((profit / billed_total) * 100) if billed_total > 0 else 0
                delta = billed_total - original_total
                
                return {
                    "project_id": project_id,
                    "original_po": {
                        "value": original['original_po_value'] or 0,
                        "tax": original['original_tax'] or 0,
                        "total": original_total
                    },
                    "billing_po": {
                        "value": billing['billed_value'] or 0,
                        "gst": billing['billed_gst'] or 0,
                        "total": billed_total,
                        "count": billing['billing_po_count'] or 0
                    },
                    "vendor_costs": {
                        "total": vendor_total
                    },
                    "financial_summary": {
                        "delta_value": delta,
                        "delta_percent": ((delta / original_total) * 100) if original_total > 0 else 0,
                        "final_revenue": billed_total,
                        "original_budget": original_total,
                        "vendor_costs": vendor_total,
                        "profit": profit,
                        "profit_margin_percent": round(margin_percent, 2)
                    }
                }
    finally:
        conn.close()


def update_billing_po(
    billing_po_id: str,
    updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update billing PO details"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Build dynamic update query
                set_clause = []
                params = []
                
                if 'billed_value' in updates or 'billed_gst' in updates:
                    billed_value = updates.get('billed_value')
                    billed_gst = updates.get('billed_gst')
                    
                    # Get current values if not provided
                    cur.execute("""
                        SELECT billed_value, billed_gst FROM billing_po WHERE id = %s
                    """, (billing_po_id,))
                    current = cur.fetchone()
                    
                    billed_value = billed_value if billed_value is not None else current['billed_value']
                    billed_gst = billed_gst if billed_gst is not None else current['billed_gst']
                    
                    set_clause.extend(['billed_value = %s', 'billed_gst = %s', 'billed_total = %s'])
                    params.extend([billed_value, billed_gst, billed_value + billed_gst])
                
                if 'billing_notes' in updates:
                    set_clause.append('billing_notes = %s')
                    params.append(updates['billing_notes'])
                
                if not set_clause:
                    return get_billing_po(billing_po_id)
                
                set_clause.append('updated_at = CURRENT_TIMESTAMP')
                params.append(billing_po_id)
                
                query = f"""
                    UPDATE billing_po
                    SET {', '.join(set_clause)}
                    WHERE id = %s
                    RETURNING id, client_po_id, project_id, po_number, billed_value, billed_gst,
                              billed_total, billing_notes, status, created_at, updated_at
                """
                
                cur.execute(query, params)
                return cur.fetchone()
    finally:
        conn.close()


def delete_billing_line_item(line_item_id: str) -> bool:
    """Delete a billing line item"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM billing_po_line_item WHERE id = %s
                """, (line_item_id,))
                
                return cur.rowcount > 0
    finally:
        conn.close()


def approve_billing_po(billing_po_id: str, notes: str = None) -> Optional[Dict[str, Any]]:
    """Approve a billing PO (mark as approved)"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Update status to APPROVED
                update_fields = ["status = 'APPROVED'", "updated_at = CURRENT_TIMESTAMP"]
                params = []
                
                if notes:
                    update_fields.append("billing_notes = %s")
                    params.append(notes)
                
                params.append(billing_po_id)
                
                query = f"""
                    UPDATE billing_po
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                    RETURNING id, client_po_id, project_id, po_number, billed_value, billed_gst,
                              billed_total, billing_notes, status, created_at, updated_at
                """
                
                cur.execute(query, params)
                result = cur.fetchone()
                
                if not result:
                    return None
                
                return {
                    "billing_po_id": result["id"],
                    "client_po_id": result["client_po_id"],
                    "project_id": result["project_id"],
                    "po_number": result["po_number"],
                    "billed_value": float(result["billed_value"]) if result["billed_value"] else 0,
                    "billed_gst": float(result["billed_gst"]) if result["billed_gst"] else 0,
                    "billed_total": float(result["billed_total"]) if result["billed_total"] else 0,
                    "billing_notes": result["billing_notes"],
                    "status": result["status"],
                    "created_at": result["created_at"].isoformat() if result["created_at"] else None,
                    "updated_at": result["updated_at"].isoformat() if result["updated_at"] else None
                }
    finally:
        conn.close()


def get_project_pl_analysis(project_id: int) -> Optional[Dict[str, Any]]:
    """Get P&L analysis for a project (wrapper around billing summary)"""
    return get_project_billing_summary(project_id)
