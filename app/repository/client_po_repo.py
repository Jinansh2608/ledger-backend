import json
from app.database import get_db
from typing import Dict, Any, Optional


def _get_or_create_project(cur, project_id: Optional[int], client_id: int) -> Optional[int]:
    """Get or create project record. Returns project_id or None if not provided."""
    if project_id is None:
        return None
    
    # Check if project exists
    cur.execute("SELECT id FROM project WHERE id = %s", (project_id,))
    result = cur.fetchone()
    if result:
        return project_id
    
    # Create project if it doesn't exist
    cur.execute("""
        INSERT INTO project (client_id, name, status)
        VALUES (%s, %s, 'Active')
        ON CONFLICT (id) DO UPDATE SET id = EXCLUDED.id
        RETURNING id
    """, (client_id, f"Project {project_id}"))
    return cur.fetchone()["id"]


def _get_or_create_vendor(cur, vendor_name: str, vendor_gstin: str = None, vendor_address: str = None) -> int:
    """Get or create vendor record. Returns vendor_id."""
    # Try to find existing vendor
    cur.execute("SELECT id FROM vendor WHERE name = %s", (vendor_name,))
    result = cur.fetchone()
    if result:
        return result["id"]
    
    # Create new vendor
    cur.execute("""
        INSERT INTO vendor (name, gstin, address)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (vendor_name, vendor_gstin, vendor_address))
    return cur.fetchone()["id"]


def _get_or_create_site(cur, store_id: str = None, site_name: str = None, address: str = None) -> Optional[int]:
    """Get or create site record. Returns site_id or None."""
    if not store_id and not site_name:
        return None
    
    # Try to find by store_id first
    if store_id:
        cur.execute("SELECT id FROM site WHERE store_id = %s", (store_id,))
        result = cur.fetchone()
        if result:
            return result["id"]
    
    # Try to find by site_name
    if site_name:
        cur.execute("SELECT id FROM site WHERE site_name = %s", (site_name,))
        result = cur.fetchone()
        if result:
            return result["id"]
    
    # Create new site - use store_id as site_name if site_name not provided (required field)
    site_name_to_insert = site_name or store_id or "Unknown Site"
    
    cur.execute("""
        INSERT INTO site (store_id, site_name, address)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (store_id, site_name_to_insert, address))
    return cur.fetchone()["id"]


def insert_client_po(parsed: Dict[str, Any], client_id: int, project_id: Optional[int] = None, project_name: Optional[str] = None) -> int:
    """
    Insert client PO with support for both traditional POs and Proforma Invoices.
    
    Args:
        parsed: Dictionary from parser with po_details and line_items
        client_id: Client ID
        project_id: Optional project ID
    
    Returns:
        client_po_id
    
    Raises:
        ValueError: If required fields are missing
    """
    # Validate required fields
    if not parsed.get("po_details"):
        raise ValueError("po_details is required")
    
    po_details = parsed["po_details"]
    if isinstance(po_details, dict) and "error" in po_details:
        raise ValueError(f"Cannot insert PO with parser error: {po_details.get('error')}")
    
    if not po_details.get("po_number"):
        raise ValueError("PO number is required in po_details")
    
    line_items = parsed.get("line_items", [])
    if not line_items or len(line_items) == 0:
        raise ValueError(f"PO {po_details.get('po_number')} has no line items - cannot create PO")
    
    conn = get_db()

    try:
        with conn:
            with conn.cursor() as cur:

                po = parsed["po_details"]

                # ========================================
                # Calculate totals
                # ========================================
                
                # Support both 'amount' and 'gross_amount' keys
                po_total = sum(
                    item.get("gross_amount") or item.get("amount") or 0
                    for item in parsed["line_items"]
                )
                
                # Get tax totals if available
                subtotal = po.get("subtotal") or sum(
                    item.get("taxable_amount") or item.get("amount") or 0
                    for item in parsed["line_items"]
                )
                cgst = po.get("cgst")
                sgst = po.get("sgst")
                igst = po.get("igst")
                total_tax = (cgst or 0) + (sgst or 0) + (igst or 0)

                # ========================================
                # Get or create project if needed
                # ========================================
                if not project_id and not project_name:
                    # Fallback: create/link project based on store_id or site_name extracted from PO
                    fallback_name = po.get("store_id") or po.get("site_name")
                    if fallback_name and fallback_name not in ("UNKNOWN_STORE", "UNKNOWN_SITE"):
                        project_name = fallback_name
                    else:
                        project_name = f"Unassigned PO Project ({po.get('po_number')})"

                if project_id:
                    project_id = _get_or_create_project(cur, project_id, client_id)
                elif project_name:
                    # Try to find or create by name
                    cur.execute("SELECT id FROM project WHERE name = %s AND client_id = %s", (project_name, client_id))
                    p_result = cur.fetchone()
                    if p_result:
                        project_id = p_result["id"]
                    else:
                        cur.execute("""
                            INSERT INTO project (client_id, name, status)
                            VALUES (%s, %s, 'Active')
                            RETURNING id
                        """, (client_id, project_name))
                        project_id = cur.fetchone()["id"]

                # ========================================
                # Get or create vendor and site
                # ========================================
                vendor_id = None
                site_id = None
                
                if po.get("vendor_name"):
                    vendor_id = _get_or_create_vendor(
                        cur,
                        po.get("vendor_name"),
                        po.get("vendor_gstin"),
                        po.get("vendor_address")
                    )
                
                if po.get("site_name") or po.get("store_id"):
                    site_id = _get_or_create_site(
                        cur,
                        po.get("store_id"),
                        po.get("site_name")
                    )

                # ========================================
                # Insert client_po
                # ========================================
                cur.execute("""
                    INSERT INTO client_po (
                        client_id,
                        project_id,
                        po_number,
                        po_date,
                        pi_number,
                        pi_date,
                        po_value,
                        subtotal,
                        cgst,
                        sgst,
                        igst,
                        total_tax,
                        receivable_amount,
                        vendor_id,
                        vendor_gstin,
                        vendor_address,
                        bill_to_gstin,
                        bill_to_address,
                        ship_to_address,
                        site_id,
                        store_id,
                        status
                    )
                    VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
                    RETURNING id
                """, (
                    client_id,
                    project_id,
                    po.get("client_po_number") or po.get("po_number"),
                    po.get("po_date"),
                    po.get("pi_number"),
                    po.get("pi_date"),
                    po_total,
                    subtotal,
                    cgst,
                    sgst,
                    igst,
                    total_tax,
                    po_total,
                    vendor_id,
                    po.get("vendor_gstin"),
                    po.get("vendor_address"),
                    po.get("bill_to_gstin"),
                    po.get("bill_to_address"),
                    po.get("ship_to_address"),
                    site_id,
                    po.get("store_id"),
                    "pending"
                ))

                client_po_id = cur.fetchone()["id"]

                # ========================================
                # Insert line items with extended fields
                # ========================================
                for item in parsed["line_items"]:
                    cur.execute("""
                        INSERT INTO client_po_line_item (
                            client_po_id,
                            item_name,
                            quantity,
                            unit,
                            unit_price,
                            total_price,
                            hsn_code,
                            rate,
                            gst_amount,
                            gross_amount
                        )
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        client_po_id,
                        item.get("boq_name") or item.get("description"),
                        item.get("quantity"),
                        item.get("unit"),
                        item.get("rate") or item.get("unit_price"),
                        item.get("taxable_amount") or item.get("amount"),
                        item.get("hsn_code"),
                        item.get("rate"),
                        item.get("gst_amount"),
                        item.get("gross_amount")
                    ))

                return client_po_id

    finally:
        conn.close()
def get_client_po_with_items(client_po_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch PO details with line items.
    
    Returns complete PO information including header, tax breakdown, and line items.
    """
    conn = get_db()

    try:
        with conn.cursor() as cur:
            # ========================================
            # Fetch PO header + summary with all fields
            # ========================================
            cur.execute("""
                SELECT
                    cp.id,
                    cp.po_number,
                    cp.po_date,
                    cp.pi_number,
                    cp.pi_date,
                    cp.po_value,
                    cp.subtotal,
                    cp.cgst,
                    cp.sgst,
                    cp.igst,
                    cp.total_tax,
                    cp.vendor_id,
                    cp.vendor_gstin,
                    cp.vendor_address,
                    cp.bill_to_gstin,
                    cp.bill_to_address,
                    cp.ship_to_address,
                    cp.site_id,
                    cp.project_id,
                    cp.client_id,
                    cp.status,
                    cp.notes,
                    cp.created_at,
                    p.name as project_name,
                    c.name as client_name,
                    v.name as vendor_name
                FROM client_po cp
                LEFT JOIN project p ON cp.project_id = p.id
                LEFT JOIN client c ON cp.client_id = c.id
                LEFT JOIN vendor v ON cp.vendor_id = v.id
                WHERE cp.id = %s
            """, (client_po_id,))

            po = cur.fetchone()
            if not po:
                return None

            po_data = {
                "client_po_id": po["id"],
                "po": {
                    "po_number": po["po_number"],
                    "po_date": po["po_date"].isoformat() if po["po_date"] else None,
                    "pi_number": po["pi_number"],
                    "pi_date": po["pi_date"].isoformat() if po["pi_date"] else None
                },
                "project": {
                    "id": po["project_id"],
                    "name": po["project_name"]
                },
                "client": {
                    "id": po["client_id"],
                    "name": po["client_name"]
                },
                "vendor": {
                    "vendor_gstin": po["vendor_gstin"],
                    "vendor_address": po["vendor_address"],
                    "vendor_id": po["vendor_id"],
                    "vendor_name": po["vendor_name"]
                },
                "billing": {
                    "bill_to_gstin": po["bill_to_gstin"],
                    "bill_to_address": po["bill_to_address"],
                    "ship_to_address": po["ship_to_address"]
                },
                "summary": {
                    "subtotal": float(po["subtotal"]) if po["subtotal"] else None,
                    "cgst": float(po["cgst"]) if po["cgst"] else None,
                    "sgst": float(po["sgst"]) if po["sgst"] else None,
                    "igst": float(po["igst"]) if po["igst"] else None,
                    "total_tax": float(po["total_tax"]) if po["total_tax"] else None,
                    "grand_total": float(po["po_value"]) if po["po_value"] else None
                },
                "site_id": po["site_id"],
                "status": po["status"],
                "notes": po["notes"],
                "created_at": po["created_at"].isoformat() if po["created_at"] else None
            }

            # ========================================
            # Fetch line items with extended fields
            # ========================================
            cur.execute("""
                SELECT
                    item_name,
                    quantity,
                    unit,
                    unit_price,
                    total_price,
                    hsn_code,
                    rate,
                    gst_amount,
                    gross_amount
                FROM client_po_line_item
                WHERE client_po_id = %s
                ORDER BY id
            """, (client_po_id,))

            items = cur.fetchall()

            po_data["line_items"] = [
                {
                    "boq_name": r["item_name"],
                    "hsn_code": r["hsn_code"],
                    "quantity": float(r["quantity"]) if r["quantity"] is not None else None,
                    "unit": r["unit"],
                    "rate": float(r["rate"]) if r["rate"] is not None else None,
                    "taxable_amount": float(r["total_price"]) if r["total_price"] is not None else None,
                    "gst_amount": float(r["gst_amount"]) if r["gst_amount"] is not None else None,
                    "gross_amount": float(r["gross_amount"]) if r["gross_amount"] is not None else None
                }
                for r in items
            ]

            po_data["line_item_count"] = len(po_data["line_items"])

            return po_data

    finally:
        conn.close()
