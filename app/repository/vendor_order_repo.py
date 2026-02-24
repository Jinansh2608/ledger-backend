"""
Vendor Order Repository
Handles all database operations for vendor management, vendor orders, and payment linking
"""

from app.database import get_db
from datetime import date
from typing import List, Dict, Optional


# ==========================================
# VENDOR MANAGEMENT
# ==========================================

def create_vendor(name: str, contact_person: str = None, email: str = None, 
                 phone: str = None, address: str = None, payment_terms: str = None):
    """Create a new vendor"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO vendor (name, contact_person, email, phone, address, payment_terms, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'active')
                    RETURNING id, name, contact_person, email, phone, address, payment_terms, status, created_at
                """, (name, contact_person, email, phone, address, payment_terms))
                
                return cur.fetchone()
    finally:
        conn.close()


def get_all_vendors(status: str = None):
    """Get all vendors, optionally filtered by status"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                if status:
                    cur.execute("""
                        SELECT id, name, contact_person, email, phone, address, payment_terms, status, created_at
                        FROM vendor
                        WHERE status = %s
                        ORDER BY name
                    """, (status,))
                else:
                    cur.execute("""
                        SELECT id, name, contact_person, email, phone, address, payment_terms, status, created_at
                        FROM vendor
                        ORDER BY name
                    """)
                
                return cur.fetchall()
    finally:
        conn.close()


def get_vendor_details(vendor_id: int):
    """Get complete vendor information with summary"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get vendor info
                cur.execute("""
                    SELECT id, name, contact_person, email, phone, address, payment_terms, status, created_at, updated_at
                    FROM vendor
                    WHERE id = %s
                """, (vendor_id,))
                
                vendor = cur.fetchone()
                if not vendor:
                    return None
                
                # Get orders count
                cur.execute("""
                    SELECT COUNT(*) as count FROM vendor_order
                    WHERE vendor_id = %s
                """, (vendor_id,))
                
                total_orders = cur.fetchone()['count']
                
                # Get total order value
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as total FROM vendor_order
                    WHERE vendor_id = %s
                """, (vendor_id,))
                
                total_order_value = cur.fetchone()['total']
                
                # Get total paid
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as total FROM vendor_payment
                    WHERE vendor_id = %s AND status = 'cleared'
                """, (vendor_id,))
                
                total_paid = cur.fetchone()['total']
                
                return {
                    **vendor,
                    'total_orders': total_orders,
                    'total_order_value': total_order_value,
                    'total_paid': total_paid,
                    'balance': float(total_order_value) - float(total_paid)
                }
    finally:
        conn.close()


def update_vendor(vendor_id: int, updates: Dict):
    """Update vendor details"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                update_fields = []
                values = []
                
                if 'name' in updates:
                    update_fields.append("name = %s")
                    values.append(updates['name'])
                if 'contact_person' in updates:
                    update_fields.append("contact_person = %s")
                    values.append(updates['contact_person'])
                if 'email' in updates:
                    update_fields.append("email = %s")
                    values.append(updates['email'])
                if 'phone' in updates:
                    update_fields.append("phone = %s")
                    values.append(updates['phone'])
                if 'address' in updates:
                    update_fields.append("address = %s")
                    values.append(updates['address'])
                if 'payment_terms' in updates:
                    update_fields.append("payment_terms = %s")
                    values.append(updates['payment_terms'])
                if 'status' in updates:
                    update_fields.append("status = %s")
                    values.append(updates['status'])
                
                if not update_fields:
                    return get_vendor_details(vendor_id)
                
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                values.append(vendor_id)
                
                query = f"UPDATE vendor SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                cur.execute(query, values)
                
                return cur.fetchone()
    finally:
        conn.close()


# ==========================================
# VENDOR ORDER MANAGEMENT
# ==========================================

def create_vendor_order(vendor_id: int, project_id: int, po_number: str = None, po_date: date = None, 
                       po_value: float = 0.0, due_date: date = None, description: str = None):
    """Create a new vendor order"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO vendor_order 
                    (vendor_id, project_id, po_number, po_date, po_value, due_date, description, 
                     work_status, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')
                    RETURNING id, vendor_id, project_id, po_number, po_date, po_value, due_date, 
                              work_status, payment_status, description, created_at
                """, (vendor_id, project_id, po_number, po_date, po_value, due_date, description))
                
                return cur.fetchone()
    finally:
        conn.close()


def bulk_create_vendor_orders(project_id: int, orders: List[Dict]):
    """Create multiple vendor orders in a single transaction"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                created_orders = []
                
                for order_data in orders:
                    cur.execute("""
                        INSERT INTO vendor_order 
                        (vendor_id, project_id, po_number, po_date, po_value, due_date, description, 
                         work_status, payment_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')
                        RETURNING id, vendor_id, project_id, po_number, po_date, po_value, due_date, 
                                  work_status, payment_status, description, created_at
                    """, (
                        order_data.get('vendor_id'),
                        project_id,
                        order_data.get('po_number'),
                        order_data.get('po_date'),
                        order_data.get('po_value', 0.0),
                        order_data.get('due_date'),
                        order_data.get('description')
                    ))
                    
                    created_orders.append(cur.fetchone())
                
                return created_orders
    finally:
        conn.close()


def get_project_vendor_orders(project_id: int):
    """Get all vendor orders for a project"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT vo.id, vo.vendor_id, v.name as vendor_name, vo.po_number, vo.po_date, 
                           vo.po_value, vo.due_date, vo.work_status, vo.payment_status, 
                           vo.description, vo.created_at,
                           COUNT(DISTINCT pvl.id) as linked_payments_count
                    FROM vendor_order vo
                    JOIN vendor v ON vo.vendor_id = v.id
                    LEFT JOIN payment_vendor_link pvl ON vo.id = pvl.vendor_order_id
                    WHERE vo.project_id = %s
                    GROUP BY vo.id, v.name
                    ORDER BY vo.created_at DESC
                """, (project_id,))
                
                return cur.fetchall()
    finally:
        conn.close()


def get_vendor_order_details(vendor_order_id: int):
    """Get complete vendor order details with summary"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get order details
                cur.execute("""
                    SELECT vo.*, v.name as vendor_name, v.contact_person, v.email, v.phone
                    FROM vendor_order vo
                    JOIN vendor v ON vo.vendor_id = v.id
                    WHERE vo.id = %s
                """, (vendor_order_id,))
                
                order = cur.fetchone()
                if not order:
                    return None
                
                # Get line items
                cur.execute("""
                    SELECT id, item_name, quantity, unit_price, total_price
                    FROM vendor_order_line_item
                    WHERE vendor_order_id = %s
                """, (vendor_order_id,))
                
                line_items = cur.fetchall()
                
                # Get linked payments count
                cur.execute("""
                    SELECT COUNT(*) as count FROM payment_vendor_link
                    WHERE vendor_order_id = %s
                """, (vendor_order_id,))
                
                linked_count = cur.fetchone()['count']
                
                return {
                    **order,
                    'line_items': line_items,
                    'line_item_count': len(line_items),
                    'linked_payments_count': linked_count
                }
    finally:
        conn.close()


def update_vendor_order(vendor_order_id: int, updates: Dict):
    """Update vendor order details"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                update_fields = ["updated_at = CURRENT_TIMESTAMP"]
                values = []
                
                if 'po_value' in updates:
                    update_fields.append("po_value = %s")
                    values.append(updates['po_value'])
                elif 'amount' in updates:
                    update_fields.append("po_value = %s")
                    values.append(updates['amount'])
                    
                if 'due_date' in updates:
                    update_fields.append("due_date = %s")
                    values.append(updates['due_date'])
                if 'description' in updates:
                    update_fields.append("description = %s")
                    values.append(updates['description'])
                if 'work_status' in updates:
                    update_fields.append("work_status = %s")
                    values.append(updates['work_status'])
                elif 'status' in updates:
                    update_fields.append("work_status = %s")
                    values.append(updates['status'])
                if 'payment_status' in updates:
                    update_fields.append("payment_status = %s")
                    values.append(updates['payment_status'])
                
                if len(update_fields) == 1:
                    return get_vendor_order_details(vendor_order_id)
                
                values.append(vendor_order_id)
                
                query = f"UPDATE vendor_order SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                cur.execute(query, values)
                
                return cur.fetchone()
    finally:
        conn.close()


def update_vendor_order_status(vendor_order_id: int, work_status: str = None, 
                              payment_status: str = None):
    """Update vendor order status"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                update_fields = ["updated_at = CURRENT_TIMESTAMP"]
                values = []
                
                if work_status:
                    update_fields.append("work_status = %s")
                    values.append(work_status)
                if payment_status:
                    update_fields.append("payment_status = %s")
                    values.append(payment_status)
                
                if len(update_fields) == 1:
                    return get_vendor_order_details(vendor_order_id)
                
                values.append(vendor_order_id)
                
                query = f"UPDATE vendor_order SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                cur.execute(query, values)
                
                return cur.fetchone()
    finally:
        conn.close()


def delete_vendor_order(vendor_order_id: int):
    """Delete vendor order and associated data"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Delete associated payment links first (due to FK constraints)
                cur.execute("DELETE FROM payment_vendor_link WHERE vendor_order_id = %s", (vendor_order_id,))
                
                # Delete vendor payments
                cur.execute("DELETE FROM vendor_payment WHERE vendor_order_id = %s", (vendor_order_id,))
                
                # Delete line items (cascade will handle this but be explicit)
                cur.execute("DELETE FROM vendor_order_line_item WHERE vendor_order_id = %s", (vendor_order_id,))
                
                # Delete vendor order
                cur.execute("DELETE FROM vendor_order WHERE id = %s", (vendor_order_id,))
                
                return True
    finally:
        conn.close()


# ==========================================
# VENDOR ORDER LINE ITEMS
# ==========================================

def add_vendor_order_line_item(vendor_order_id: int, item_name: str, quantity: float, 
                              unit_price: float):
    """Add line item to vendor order and update order value"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                total_price = quantity * unit_price
                
                # Insert line item
                cur.execute("""
                    INSERT INTO vendor_order_line_item 
                    (vendor_order_id, item_name, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, item_name, quantity, unit_price, total_price
                """, (vendor_order_id, item_name, quantity, unit_price, total_price))
                
                line_item = cur.fetchone()
                
                # Update vendor order po_value
                cur.execute("""
                    UPDATE vendor_order
                    SET po_value = po_value + %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (total_price, vendor_order_id))
                
                return line_item
    finally:
        conn.close()


def update_vendor_order_line_item(line_item_id: int, updates: Dict):
    """Update line item and recalculate order value"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get current line item
                cur.execute("""
                    SELECT vendor_order_id, total_price FROM vendor_order_line_item
                    WHERE id = %s
                """, (line_item_id,))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                vendor_order_id = result['vendor_order_id']
                old_total = result['total_price']
                
                # Build update query
                update_fields = []
                values = []
                
                if 'item_name' in updates:
                    update_fields.append("item_name = %s")
                    values.append(updates['item_name'])
                
                if 'quantity' in updates or 'unit_price' in updates:
                    quantity = updates.get('quantity')
                    unit_price = updates.get('unit_price')
                    
                    if quantity is not None:
                        update_fields.append("quantity = %s")
                        values.append(quantity)
                    
                    if unit_price is not None:
                        update_fields.append("unit_price = %s")
                        values.append(unit_price)
                    
                    # Recalculate total_price
                    cur.execute("""
                        SELECT quantity, unit_price FROM vendor_order_line_item
                        WHERE id = %s
                    """, (line_item_id,))
                    
                    current = cur.fetchone()
                    new_qty = quantity if quantity is not None else current['quantity']
                    new_price = unit_price if unit_price is not None else current['unit_price']
                    new_total = new_qty * new_price
                    
                    update_fields.append("total_price = %s")
                    values.append(new_total)
                    
                    # Update vendor order po_value with difference
                    difference = new_total - old_total
                    cur.execute("""
                        UPDATE vendor_order
                        SET po_value = po_value + %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (difference, vendor_order_id))
                
                if not update_fields:
                    return cur.execute("""
                        SELECT id, item_name, quantity, unit_price, total_price
                        FROM vendor_order_line_item WHERE id = %s
                    """, (line_item_id,))
                
                values.append(line_item_id)
                query = f"UPDATE vendor_order_line_item SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                cur.execute(query, values)
                
                return cur.fetchone()
    finally:
        conn.close()


def delete_vendor_order_line_item(line_item_id: int):
    """Delete line item and recalculate order value"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get line item details
                cur.execute("""
                    SELECT vendor_order_id, total_price FROM vendor_order_line_item
                    WHERE id = %s
                """, (line_item_id,))
                
                result = cur.fetchone()
                if not result:
                    return False
                
                vendor_order_id = result['vendor_order_id']
                total_price = result['total_price']
                
                # Delete line item
                cur.execute("DELETE FROM vendor_order_line_item WHERE id = %s", (line_item_id,))
                
                # Update vendor order po_value
                cur.execute("""
                    UPDATE vendor_order
                    SET po_value = po_value - %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (total_price, vendor_order_id))
                
                return True
    finally:
        conn.close()


def get_vendor_order_line_items(vendor_order_id: int):
    """Get all line items for a vendor order"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, item_name, quantity, unit_price, total_price
                    FROM vendor_order_line_item
                    WHERE vendor_order_id = %s
                    ORDER BY id
                """, (vendor_order_id,))
                
                return cur.fetchall()
    finally:
        conn.close()


# ==========================================
# PAYMENT LINKING
# ==========================================

def link_payment_to_vendor_order(vendor_order_id: int, payment_id: int, link_type: str):
    """Link existing client payment to vendor order"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO payment_vendor_link 
                    (vendor_order_id, payment_id, link_type)
                    VALUES (%s, %s, %s)
                    RETURNING id, vendor_order_id, payment_id, link_type, linked_at
                """, (vendor_order_id, payment_id, link_type))
                
                return cur.fetchone()
    finally:
        conn.close()


def get_vendor_order_linked_payments(vendor_order_id: int):
    """Get all payments linked to vendor order"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT pvl.id, pvl.vendor_order_id, pvl.payment_id, pvl.link_type, pvl.linked_at,
                           cp.amount, cp.payment_date, cp.payment_mode, cp.status as payment_status
                    FROM payment_vendor_link pvl
                    JOIN client_payment cp ON pvl.payment_id = cp.id
                    WHERE pvl.vendor_order_id = %s
                    ORDER BY pvl.linked_at DESC
                """, (vendor_order_id,))
                
                return cur.fetchall()
    finally:
        conn.close()


def get_vendor_order_payment_summary(vendor_order_id: int):
    """Get payment summary for vendor order"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get linked payments by type
                cur.execute("""
                    SELECT pvl.link_type, SUM(cp.amount) as total
                    FROM payment_vendor_link pvl
                    JOIN client_payment cp ON pvl.payment_id = cp.id
                    WHERE pvl.vendor_order_id = %s
                    GROUP BY pvl.link_type
                """, (vendor_order_id,))
                
                totals = cur.fetchall()
                
                incoming_total = 0
                outgoing_total = 0
                
                for row in totals:
                    if row['link_type'] == 'incoming':
                        incoming_total = float(row['total']) if row['total'] else 0
                    elif row['link_type'] == 'outgoing':
                        outgoing_total = float(row['total']) if row['total'] else 0
                
                # Get link count
                cur.execute("""
                    SELECT COUNT(*) as count FROM payment_vendor_link
                    WHERE vendor_order_id = %s
                """, (vendor_order_id,))
                
                link_count = cur.fetchone()['count']
                
                return {
                    'total_incoming': incoming_total,
                    'total_outgoing': outgoing_total,
                    'profit': incoming_total - outgoing_total,
                    'link_count': link_count
                }
    finally:
        conn.close()


def unlink_payment(link_id: int):
    """Remove payment link by link ID"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM payment_vendor_link WHERE id = %s", (link_id,))
                return True
    finally:
        conn.close()


def unlink_payment_by_payment_id(vendor_order_id: int, payment_id: int):
    """Remove payment link by payment ID"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM payment_vendor_link 
                    WHERE vendor_order_id = %s AND payment_id = %s
                """, (vendor_order_id, payment_id))
                return True
    finally:
        conn.close()


# ==========================================
# VENDOR PAYMENTS (OUTGOING)
# ==========================================

def create_vendor_payment(vendor_order_id: int, payment_date: date, amount: float, 
                         payment_mode: str, reference_number: str = None, notes: str = None):
    """Record outgoing payment to vendor"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO vendor_payment 
                    (vendor_order_id, payment_date, amount, payment_mode, reference_number, notes, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                    RETURNING id, vendor_order_id, payment_date, amount, payment_mode, 
                              reference_number, status, notes, created_at
                """, (vendor_order_id, payment_date, amount, payment_mode, reference_number, notes))
                
                return cur.fetchone()
    finally:
        conn.close()


def get_vendor_order_payments(vendor_order_id: int):
    """Get all vendor payments for order"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, vendor_order_id, payment_date, amount, payment_mode, 
                           reference_number, status, notes, created_at, updated_at
                    FROM vendor_payment
                    WHERE vendor_order_id = %s
                    ORDER BY payment_date DESC
                """, (vendor_order_id,))
                
                payments = cur.fetchall()
                
                # Calculate summary
                total_cleared = 0
                total_pending = 0
                total_bounced = 0
                
                for payment in payments:
                    if payment['status'] == 'cleared':
                        total_cleared += float(payment['amount'])
                    elif payment['status'] == 'pending':
                        total_pending += float(payment['amount'])
                    elif payment['status'] == 'bounced':
                        total_bounced += float(payment['amount'])
                
                return {
                    'payments': payments,
                    'payment_count': len(payments),
                    'summary': {
                        'total_cleared': total_cleared,
                        'total_pending': total_pending,
                        'total_bounced': total_bounced,
                        'cleared_count': len([p for p in payments if p['status'] == 'cleared']),
                        'pending_count': len([p for p in payments if p['status'] == 'pending']),
                        'bounced_count': len([p for p in payments if p['status'] == 'bounced'])
                    }
                }
    finally:
        conn.close()


def update_vendor_payment(payment_id: int, updates: Dict):
    """Update vendor payment"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                update_fields = ["updated_at = CURRENT_TIMESTAMP"]
                values = []
                
                if 'amount' in updates:
                    update_fields.append("amount = %s")
                    values.append(updates['amount'])
                if 'payment_date' in updates:
                    update_fields.append("payment_date = %s")
                    values.append(updates['payment_date'])
                if 'payment_mode' in updates:
                    update_fields.append("payment_mode = %s")
                    values.append(updates['payment_mode'])
                if 'status' in updates:
                    update_fields.append("status = %s")
                    values.append(updates['status'])
                if 'reference_number' in updates:
                    update_fields.append("reference_number = %s")
                    values.append(updates['reference_number'])
                if 'notes' in updates:
                    update_fields.append("notes = %s")
                    values.append(updates['notes'])
                
                if len(update_fields) == 1:
                    cur.execute("""
                        SELECT id, vendor_order_id, payment_date, amount, payment_mode, 
                               reference_number, status, notes
                        FROM vendor_payment WHERE id = %s
                    """, (payment_id,))
                    return cur.fetchone()
                
                values.append(payment_id)
                query = f"UPDATE vendor_payment SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
                cur.execute(query, values)
                
                return cur.fetchone()
    finally:
        conn.close()


def delete_vendor_payment(payment_id: int):
    """Delete vendor payment"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM vendor_payment WHERE id = %s", (payment_id,))
                return True
    finally:
        conn.close()

# ==========================================
# VENDOR DELETE AND SUMMARY FUNCTIONS
# ==========================================

def delete_vendor(vendor_id: int):
    """Delete vendor (only if no orders exist)"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Check for existing orders
                cur.execute("""
                    SELECT COUNT(*) as count FROM vendor_order
                    WHERE vendor_id = %s
                """, (vendor_id,))
                
                count = cur.fetchone()['count']
                if count > 0:
                    raise Exception(f"Cannot delete vendor with {count} existing orders")
                
                # Delete vendor
                cur.execute("DELETE FROM vendor WHERE id = %s", (vendor_id,))
                return True
    finally:
        conn.close()


def get_vendor_payments(vendor_id: int):
    """Get all payments made to a vendor"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # First verify vendor exists
                cur.execute("SELECT id FROM vendor WHERE id = %s", (vendor_id,))
                if not cur.fetchone():
                    return None
                
                # Get all payments for this vendor
                cur.execute("""
                    SELECT vp.id, vp.vendor_order_id, vp.payment_date, vp.amount, 
                           vp.status, vp.created_at,
                           vo.po_number, vo.amount as order_amount
                    FROM vendor_payment vp
                    JOIN vendor_order vo ON vp.vendor_order_id = vo.id
                    WHERE vo.vendor_id = %s
                    ORDER BY vp.payment_date DESC
                """, (vendor_id,))
                
                return cur.fetchall()
    finally:
        conn.close()


def get_vendor_payment_summary(vendor_id: int):
    """Get vendor payment summary with aggregated statistics"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Verify vendor exists
                cur.execute("SELECT id FROM vendor WHERE id = %s", (vendor_id,))
                if not cur.fetchone():
                    return None
                
                # Total order value
                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) as total FROM vendor_order
                    WHERE vendor_id = %s
                """, (vendor_id,))
                
                row = cur.fetchone()
                total_order_value = float(row['total']) if row else 0
                
                # Total paid
                cur.execute("""
                    SELECT COALESCE(SUM(vp.amount), 0) as total FROM vendor_payment vp
                    JOIN vendor_order vo ON vp.vendor_order_id = vo.id
                    WHERE vo.vendor_id = %s AND vp.status = 'cleared'
                """, (vendor_id,))
                
                row = cur.fetchone()
                total_paid = float(row['total']) if row else 0
                
                # Total payable
                total_payable = total_order_value - total_paid
                
                return {
                    'vendor_id': vendor_id,
                    'total_order_value': total_order_value,
                    'total_paid': total_paid,
                    'total_payable': total_payable
                }
    finally:
        conn.close()


def get_project_vendor_summary(project_id: int):
    """Get aggregated vendor order statistics for a project"""
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Verify project exists
                cur.execute("SELECT id FROM project WHERE id = %s", (project_id,))
                if not cur.fetchone():
                    return None
                
                # Count vendors
                cur.execute("""
                    SELECT COUNT(DISTINCT vendor_id) as count FROM vendor_order
                    WHERE project_id = %s
                """, (project_id,))
                
                total_vendors = cur.fetchone()['count']
                
                # Count orders and total value
                cur.execute("""
                    SELECT COUNT(*) as count, COALESCE(SUM(po_value), 0) as total 
                    FROM vendor_order
                    WHERE project_id = %s
                """, (project_id,))
                
                result = cur.fetchone()
                total_orders = result['count']
                total_value = float(result['total']) if result['total'] else 0
                
                # Total paid
                cur.execute("""
                    SELECT COALESCE(SUM(vp.amount), 0) as total FROM vendor_payment vp
                    JOIN vendor_order vo ON vp.vendor_order_id = vo.id
                    WHERE vo.project_id = %s AND vp.status = 'cleared'
                """, (project_id,))
                
                row = cur.fetchone()
                total_paid = float(row['total']) if row else 0
                total_payable = total_value - total_paid
                
                # Status counts
                cur.execute("""
                    SELECT work_status, COUNT(*) as count FROM vendor_order
                    WHERE project_id = %s
                    GROUP BY work_status
                """, (project_id,))
                
                status_counts = cur.fetchall()
                pending_orders = 0
                ongoing_orders = 0
                completed_orders = 0
                
                for row in status_counts:
                    if row['work_status'] == 'pending':
                        pending_orders = row['count']
                    elif row['work_status'] == 'ongoing':
                        ongoing_orders = row['count']
                    elif row['work_status'] == 'completed':
                        completed_orders = row['count']
                
                return {
                    'project_id': project_id,
                    'total_vendors': total_vendors,
                    'total_vendor_orders': total_orders,
                    'total_order_value': total_value,
                    'total_payable': total_payable,
                    'total_paid': total_paid,
                    'pending_orders': pending_orders,
                    'ongoing_orders': ongoing_orders,
                    'completed_orders': completed_orders
                }
    finally:
        conn.close()