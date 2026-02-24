from app.database import get_db
from datetime import date
from typing import List, Dict, Optional

def create_payment(client_po_id: int, payment_date: date, amount: float, 
                  payment_mode: str, status: str = "pending",
                  payment_stage: str = "other", notes: str = None, 
                  is_tds_deducted: bool = False, tds_amount: float = 0,
                  received_by_account: str = None, transaction_type: str = "credit",
                  reference_number: str = None):
    """Record a new payment for a PO"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                # First, get the client_id from the client_po record
                cur.execute("""
                    SELECT client_id FROM client_po WHERE id = %s
                """, (client_po_id,))
                
                po_row = cur.fetchone()
                if not po_row:
                    raise ValueError(f"PO with ID {client_po_id} not found")
                
                client_id = po_row["client_id"]
                
                # Insert payment and return the id
                cur.execute("""
                    INSERT INTO client_payment (
                        client_id,
                        client_po_id,
                        payment_date,
                        amount,
                        payment_mode,
                        status,
                        payment_stage,
                        notes,
                        is_tds_deducted,
                        tds_amount,
                        received_by_account,
                        transaction_type,
                        reference_number
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (client_id, client_po_id, payment_date, amount, payment_mode, status,
                      payment_stage, notes, is_tds_deducted, tds_amount,
                      received_by_account, transaction_type, reference_number))

                payment_id_row = cur.fetchone()
                payment_id = payment_id_row["id"] if payment_id_row else None
                
                # Update PO status logic could go here if needed, or stick to manual update
                
                return payment_id
    finally:
        conn.close()

def get_payments_for_po(client_po_id: int):
    """Get all payments for a specific PO"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    client_po_id,
                    payment_date,
                    amount,
                    payment_mode,
                    reference_number,
                    status,
                    payment_stage,
                    notes,
                    is_tds_deducted,
                    tds_amount,
                    received_by_account,
                    transaction_type,
                    created_at
                FROM client_payment
                WHERE client_po_id = %s
                ORDER BY payment_date DESC, created_at DESC
            """, (client_po_id,))
            
            payments = cur.fetchall()
            return [
                {
                    "id": p["id"],
                    "client_po_id": p["client_po_id"],
                    "payment_date": p["payment_date"].isoformat() if p["payment_date"] else None,
                    "amount": float(p["amount"]) if p["amount"] else 0,
                    "payment_mode": p["payment_mode"],
                    "reference_number": p["reference_number"],
                    "status": p["status"],
                    "payment_stage": p["payment_stage"],
                    "notes": p["notes"],
                    "is_tds_deducted": p["is_tds_deducted"],
                    "tds_amount": float(p["tds_amount"]) if p["tds_amount"] else 0,
                    "received_by_account": p["received_by_account"],
                    "transaction_type": p["transaction_type"],
                    "created_at": p["created_at"].isoformat()
                }
                for p in payments
            ]
    finally:
        conn.close()

def update_payment(payment_id: int, **kwargs):
    """Update payment details"""
    conn = get_db()
    allowed_fields = [
        "payment_date", "amount", "payment_mode", "status", "payment_stage", 
        "notes", "is_tds_deducted", "tds_amount", "received_by_account", 
        "transaction_type", "reference_number"
    ]
    
    try:
        with conn:
            with conn.cursor() as cur:
                # Filter kwargs needed
                updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
                
                if not updates:
                    return False
                
                set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
                values = list(updates.values())
                values.append(payment_id)
                
                cur.execute(f"""
                    UPDATE client_payment
                    SET {set_clause}
                    WHERE id = %s
                """, values)
                
                return cur.rowcount > 0
    finally:
        conn.close()

def delete_payment(payment_id: int):
    """Delete a payment"""
    conn = get_db()
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM client_payment WHERE id = %s", (payment_id,))
                return cur.rowcount > 0
    finally:
        conn.close()

def get_payment_summary(client_po_id: int):
    """Get total paid amount for a PO"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN transaction_type = 'debit' THEN -amount ELSE amount END) as total_paid,
                    SUM(CASE WHEN is_tds_deducted THEN (CASE WHEN transaction_type = 'debit' THEN -tds_amount ELSE tds_amount END) ELSE 0 END) as total_tds
                FROM client_payment
                WHERE client_po_id = %s AND status = 'cleared'
            """, (client_po_id,))
            
            result = cur.fetchone()
            return {
                "total_paid": float(result["total_paid"]) if result["total_paid"] else 0.0,
                "total_tds": float(result["total_tds"]) if result["total_tds"] else 0.0
            }
    finally:
        conn.close()


def get_project_payment_summary(project_id: int):
    """Get detailed payment summary for an entire project (across all POs)
    
    Returns total collected, TDS deducted, and payment status counts
    """
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            # Get comprehensive payment metrics for project
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN cp.transaction_type = 'debit' THEN -cp.amount ELSE cp.amount END) as total_collected,
                    SUM(CASE WHEN cp.is_tds_deducted AND cp.status = 'cleared' THEN cp.tds_amount ELSE 0 END) as total_tds,
                    COUNT(DISTINCT CASE WHEN cp.status = 'cleared' THEN cp.id END) as cleared_payments,
                    COUNT(DISTINCT CASE WHEN cp.status = 'pending' THEN cp.id END) as pending_payments,
                    COUNT(DISTINCT CASE WHEN cp.status = 'bounced' THEN cp.id END) as bounced_payments
                FROM client_payment cp
                JOIN client_po cpo ON cp.client_po_id = cpo.id
                LEFT JOIN po_project_mapping ppm ON cpo.id = ppm.client_po_id
                WHERE (cpo.project_id = %s OR ppm.project_id = %s)
            """, (project_id, project_id))
            
            result = cur.fetchone()
            return {
                "total_collected": float(result["total_collected"]) if result and result["total_collected"] is not None else 0.0,
                "total_tds": float(result["total_tds"]) if result and result["total_tds"] is not None else 0.0,
                "cleared_payments": result["cleared_payments"] if result else 0,
                "pending_payments": result["pending_payments"] if result else 0,
                "bounced_payments": result["bounced_payments"] if result else 0
            }
    finally:
        conn.close()


def get_all_payments(skip: int = 0, limit: int = 50) -> List[Dict]:
    """Get all payments with pagination"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    client_po_id,
                    payment_date,
                    amount,
                    payment_mode,
                    status,
                    payment_stage,
                    notes,
                    is_tds_deducted,
                    tds_amount,
                    received_by_account,
                    transaction_type,
                    reference_number
                FROM client_payment
                ORDER BY payment_date DESC
                LIMIT %s OFFSET %s
            """, (limit, skip))
            
            payments = []
            for row in cur.fetchall():
                payments.append({
                    "id": row["id"],
                    "client_po_id": row["client_po_id"],
                    "payment_date": row["payment_date"].isoformat() if row["payment_date"] else None,
                    "amount": float(row["amount"]),
                    "payment_mode": row["payment_mode"],
                    "status": row["status"],
                    "payment_stage": row["payment_stage"],
                    "notes": row["notes"],
                    "is_tds_deducted": row["is_tds_deducted"],
                    "tds_amount": float(row["tds_amount"]),
                    "received_by_account": row["received_by_account"],
                    "transaction_type": row["transaction_type"],
                    "reference_number": row["reference_number"]
                })
            return payments
    finally:
        conn.close()


def get_total_payment_count() -> int:
    """Get total count of all payments"""
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM client_payment")
            result = cur.fetchone()
            return result["total"] if result else 0
    finally:
        conn.close()

