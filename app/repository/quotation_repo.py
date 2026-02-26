"""
Quotation Repository
Handles all database operations for store-based quotations and BOQ line items with GST support
"""

from app.database import get_db
from typing import List, Dict, Optional

def create_quotation(header: Dict, line_items: List[Dict]):
    """
    Create a new quotation with its line items
    """
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # 1. Insert Header
                cur.execute("""
                    INSERT INTO quotation 
                    (store_id, store_location, full_address, company_name, total_area, total_amount, subtotal, total_gst, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'saved')
                    RETURNING id
                """, (
                    header.get('storeId'),
                    header.get('storeLocation'),
                    header.get('fullAddress'),
                    header.get('companyName'),
                    header.get('totalArea'),
                    header.get('totalAmount', 0),
                    header.get('subtotal', 0),
                    header.get('totalGST', 0)
                ))
                
                quotation_id = cur.fetchone()['id']
                
                # 2. Insert Line Items
                for item in line_items:
                    cur.execute("""
                        INSERT INTO quotation_line_item 
                        (quotation_id, name, hsn_sac_code, type_of_boq, quantity, units, price, tax, gst_amount, total)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        quotation_id,
                        item.get('name'),
                        item.get('hsn_sac_code'),
                        item.get('type_of_boq'),
                        item.get('quantity', 1),
                        item.get('units'),
                        item.get('price', 0),
                        item.get('tax', 18),
                        item.get('gst_amount', 0),
                        item.get('total', 0)
                    ))
                
                return get_quotation_details(quotation_id)
    finally:
        conn.close()

def get_quotations_by_store_id(store_id: str):
    """
    Get all quotations filtered by store ID
    """
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM quotation 
                    WHERE store_id = %s 
                    ORDER BY created_at DESC
                """, (store_id,))
                return cur.fetchall()
    finally:
        conn.close()

def get_quotation_details(quotation_id: int):
    """
    Get a single quotation with all its line items
    """
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM quotation WHERE id = %s", (quotation_id,))
                header = cur.fetchone()
                
                if not header:
                    return None
                
                cur.execute("SELECT * FROM quotation_line_item WHERE quotation_id = %s", (quotation_id,))
                items = cur.fetchall()
                
                return {
                    "header": header,
                    "line_items": items
                }
    finally:
        conn.close()

def delete_quotation(quotation_id: int):
    """
    Delete a quotation
    """
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM quotation WHERE id = %s", (quotation_id,))
                return True
    finally:
        conn.close()
