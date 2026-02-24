"""
PO Management APIs:
- Line items (add, update, delete)
- Multiple POs per project (create, attach, set-primary)
- Verbal agreements (create, add PO, list)
- Financial summary & enriched PO views
- Project CRUD
- PO deletion
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.repository.po_management_repo import (
    add_line_item,
    update_line_item,
    delete_line_item,
    get_line_items,
    get_all_pos,
    get_po_by_id,
    create_po_for_project,
    get_all_pos_for_project,
    attach_po_to_project,
    set_primary_po,
    create_verbal_agreement,
    get_verbal_agreements_for_project,
    update_po_details,
    add_po_to_verbal_agreement,
    delete_po,
    delete_project,
    create_project
)
from app.repository.payment_repo import get_project_payment_summary

router = APIRouter(prefix="/api", tags=["PO Management"])


# ==========================================
# PYDANTIC MODELS
# ==========================================

class LineItemRequest(BaseModel):
    """Model for creating a new line item"""
    item_name: Optional[str] = None
    description: Optional[str] = None
    quantity: float
    unit_price: float
    amount: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "Material A",
                "quantity": 100,
                "unit_price": 50.00
            }
        }


class LineItemUpdateRequest(BaseModel):
    """Model for updating line item (all fields optional)"""
    item_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 120,
                "unit_price": 55.00
            }
        }


class BulkLineItemRequest(BaseModel):
    """Model for adding multiple line items at once"""
    items: list[LineItemRequest]
    
    class Config:
        example = {
            "items": [
                {"item_name": "Material A", "quantity": 100, "unit_price": 50.00},
                {"item_name": "Material B", "quantity": 200, "unit_price": 25.00}
            ]
        }


class LineItemResponse(BaseModel):
    """Common response for line item operations"""
    line_item_id: int
    item_name: str
    quantity: float
    unit_price: float
    total_price: float
    
    class Config:
        example = {
            "line_item_id": 1,
            "item_name": "Material A",
            "quantity": 100,
            "unit_price": 50.00,
            "total_price": 5000.00
        }


class CreatePORequest(BaseModel):
    po_number: Optional[str] = None
    po_date: date
    po_value: float = 0.0
    po_type: str = "standard"
    parent_po_id: Optional[int] = None
    notes: Optional[str] = None


class VerbalAgreementRequest(BaseModel):
    pi_number: str
    pi_date: date
    value: float = 0.0
    notes: Optional[str] = None


class AddPOToVerbalAgreementRequest(BaseModel):
    po_number: str
    po_date: date


class UpdatePORequest(BaseModel):
    po_number: Optional[str] = None
    po_date: Optional[date] = None
    po_value: Optional[float] = None
    pi_number: Optional[str] = None
    pi_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class CreateProjectRequest(BaseModel):
    name: str
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ==========================================
# LINE ITEMS
# ==========================================

@router.post("/po/{client_po_id}/line-items")
def add_new_line_item(client_po_id: int, item: LineItemRequest):
    """
    Add a new line item to a PO
    
    Args:
        client_po_id: ID of the PO
        item: Line item details (item_name, quantity, unit_price)
    
    Returns:
        Created line item with calculated total_price
    
    Example:
        POST /api/po/1/line-items
        {
            "item_name": "Material A",
            "quantity": 100,
            "unit_price": 50.00
        }
        
        Response:
        {
            "status": "SUCCESS",
            "message": "Line item added successfully",
            "line_item": {
                "line_item_id": 1,
                "item_name": "Material A",
                "quantity": 100,
                "unit_price": 50.00,
                "total_price": 5000.00
            }
        }
    """
    try:
        # Support both item_name and description
        final_item_name = item.item_name or item.description
        
        # Validate input
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if item.unit_price < 0:
            raise HTTPException(status_code=400, detail="Unit price cannot be negative")
        if not final_item_name or not final_item_name.strip():
            raise HTTPException(status_code=400, detail="Item name or description is required")
        
        result = add_line_item(
            client_po_id=client_po_id,
            item_name=final_item_name.strip(),
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        return {
            "status": "SUCCESS",
            "message": "Line item added successfully",
            "line_item": {
                "line_item_id": result["line_item_id"],
                "item_name": result["item_name"],
                "quantity": float(result["quantity"]),
                "unit_price": float(result["unit_price"]),
                "total_price": float(result["total_price"])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add line item: {str(e)}")


@router.post("/po/{client_po_id}/line-items/bulk")
def add_bulk_line_items(client_po_id: int, bulk_request: BulkLineItemRequest):
    """
    Add multiple line items to a PO at once
    
    Args:
        client_po_id: ID of the PO
        bulk_request: List of line items to add
    
    Returns:
        List of created line items
    
    Example:
        POST /api/po/1/line-items/bulk
        {
            "items": [
                {"item_name": "Material A", "quantity": 100, "unit_price": 50.00},
                {"item_name": "Material B", "quantity": 200, "unit_price": 25.00}
            ]
        }
    """
    try:
        if not bulk_request.items or len(bulk_request.items) == 0:
            raise HTTPException(status_code=400, detail="Items list cannot be empty")
        
        if len(bulk_request.items) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 items per request")
        
        created_items = []
        failed_items = []
        
        for idx, item in enumerate(bulk_request.items):
            try:
                # Support both item_name and description
                final_item_name = item.item_name or item.description

                # Validate each item
                if item.quantity <= 0:
                    failed_items.append({"index": idx, "reason": "Quantity must be > 0"})
                    continue
                if item.unit_price < 0:
                    failed_items.append({"index": idx, "reason": "Unit price cannot be negative"})
                    continue
                if not final_item_name or not final_item_name.strip():
                    failed_items.append({"index": idx, "reason": "Item name or description is required"})
                    continue
                
                result = add_line_item(
                    client_po_id=client_po_id,
                    item_name=final_item_name.strip(),
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                created_items.append({
                    "line_item_id": result["line_item_id"],
                    "item_name": result["item_name"],
                    "quantity": float(result["quantity"]),
                    "unit_price": float(result["unit_price"]),
                    "total_price": float(result["total_price"])
                })
            except Exception as e:
                failed_items.append({"index": idx, "reason": str(e)})
        
        return {
            "status": "PARTIAL_SUCCESS" if failed_items else "SUCCESS",
            "message": f"Added {len(created_items)} items successfully",
            "line_items": created_items,
            "failed_count": len(failed_items),
            "failed_items": failed_items if failed_items else []
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk add failed: {str(e)}")


@router.get("/po/{client_po_id}/line-items")
def get_po_line_items(client_po_id: int):
    """
    Get all line items for a PO
    
    Args:
        client_po_id: ID of the PO
    
    Returns:
        List of line items with totals and summary
    
    Example:
        GET /api/po/1/line-items
        
        Response:
        {
            "status": "SUCCESS",
            "client_po_id": 1,
            "line_items": [...],
            "line_item_count": 5,
            "total_quantity": 550,
            "total_value": 12500.00,
            "average_unit_price": 45.45
        }
    """
    try:
        items = get_line_items(client_po_id)
        
        if not items:
            return {
                "status": "SUCCESS",
                "client_po_id": client_po_id,
                "line_items": [],
                "line_item_count": 0,
                "total_quantity": 0,
                "total_value": 0,
                "average_unit_price": 0
            }
        
        total_value = sum(float(item["total_price"]) for item in items if item["total_price"])
        total_quantity = sum(float(item["quantity"]) for item in items if item["quantity"])
        average_price = total_value / total_quantity if total_quantity > 0 else 0
        
        return {
            "status": "SUCCESS",
            "client_po_id": client_po_id,
            "line_items": items,
            "line_item_count": len(items),
            "total_quantity": float(total_quantity),
            "total_value": float(total_value),
            "average_unit_price": float(average_price)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch line items: {str(e)}")


@router.put("/line-items/{line_item_id}")
def update_existing_line_item(line_item_id: int, item: LineItemUpdateRequest):
    """
    Update a line item (partial update supported)
    
    Args:
        line_item_id: ID of the line item to update
        item: Fields to update (all optional - partial update supported)
    
    Returns:
        Updated line item with new total_price
    
    Example:
        PUT /api/line-items/1
        {
            "quantity": 120,
            "unit_price": 55.00
        }
        
        Response:
        {
            "status": "SUCCESS",
            "message": "Line item updated successfully",
            "line_item": {
                "line_item_id": 1,
                "item_name": "Material A",
                "quantity": 120,
                "unit_price": 55.00,
                "total_price": 6600.00
            }
        }
    """
    try:
        # Support both item_name and description
        final_item_name = item.item_name or item.description

        # Check if at least one field is being updated
        if not any([final_item_name, item.quantity is not None, item.unit_price is not None, item.amount is not None]):
            raise HTTPException(status_code=400, detail="At least one field must be provided for update")
        
        # Validate input values
        if item.quantity is not None and item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if item.unit_price is not None and item.unit_price < 0:
            raise HTTPException(status_code=400, detail="Unit price cannot be negative")
        if final_item_name is not None and (not final_item_name or not final_item_name.strip()):
            raise HTTPException(status_code=400, detail="Item name or description cannot be empty if provided")
        
        result = update_line_item(
            line_item_id=line_item_id,
            item_name=final_item_name.strip() if final_item_name else None,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Line item {line_item_id} not found")
        
        return {
            "status": "SUCCESS",
            "message": "Line item updated successfully",
            "line_item": {
                "line_item_id": result["line_item_id"],
                "item_name": result["item_name"],
                "quantity": float(result["quantity"]),
                "unit_price": float(result["unit_price"]),
                "total_price": float(result["total_price"])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update line item: {str(e)}")


@router.delete("/line-items/{line_item_id}")
def remove_line_item(line_item_id: int):
    """
    Delete a line item from a PO
    
    Args:
        line_item_id: ID of the line item to delete
    
    Returns:
        Success message
    
    Example:
        DELETE /api/line-items/1
        
        Response:
        {
            "status": "SUCCESS",
            "message": "Line item deleted successfully"
        }
    """
    try:
        success = delete_line_item(line_item_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Line item {line_item_id} not found")
        return {
            "status": "SUCCESS",
            "message": "Line item deleted successfully",
            "line_item_id": line_item_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete line item: {str(e)}")


# ==========================================
# GET ALL POs
# ==========================================

@router.get("/po")
def get_all_purchase_orders(client_id: int = Query(None)):
    """Get all POs with optional client_id filter"""
    try:
        pos = get_all_pos(client_id=client_id)
        total_value = sum(po["po_value"] for po in pos)
        return {
            "status": "SUCCESS",
            "data": {
                "pos": pos,
                "total_count": len(pos),
                "total_value": total_value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch POs: {str(e)}")


@router.get("/po/aggregated/by-store")
def get_aggregated_pos_by_store(client_id: int = Query(None)):
    """
    Get POs with different handling for each client:
    
    Returns:
    - All individual POs from client_id 1 (NO bundling)
    - Bundled POs (grouped by store) from client_id 2
    
    When multiple POs have the same store_id (for client 2):
    - They are grouped as a single bundle
    - Line items from all POs are combined
    - A bundling note indicates they are bundled together
    - is_bundled flag shows if multiple POs are combined
    - badge field shows visual indicator for frontend
    
    Returns list of POs/bundles with aggregated data and all line items.
    """
    try:
        from app.database import get_db
        bundles = []
        
        # Determine which clients to fetch
        target_clients = [client_id] if client_id else [1, 2]
        
        # Get individual POs for client 1 (no bundling)
        if 1 in target_clients:
            conn = get_db()
            try:
                with conn.cursor() as cur:
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
                            cp.created_at,
                            cp.store_id,
                            c.name as client_name,
                            p.name as project_name
                        FROM client_po cp
                        LEFT JOIN client c ON cp.client_id = c.id
                        LEFT JOIN project p ON cp.project_id = p.id
                        WHERE cp.client_id = 1
                        ORDER BY cp.created_at DESC
                    """)
                    client1_rows = cur.fetchall()
                    
                    # Convert to individual PO objects (not bundled)
                    for row in client1_rows:
                        bundle = {
                            "id": row["id"],
                            "client_po_id": row["id"],
                            "client_id": row["client_id"],
                            "client_name": row["client_name"],
                            "project_id": row["project_id"],
                            "project_name": row["project_name"],
                            "po_number": row["po_number"],
                            "po_date": row["po_date"],
                            "po_value": float(row["po_value"]) if row["po_value"] else 0,
                            "receivable_amount": float(row["receivable_amount"]) if row["receivable_amount"] else 0,
                            "status": row["status"],
                            "created_at": row["created_at"],
                            "po_ids": [row["id"]],  # Single PO
                            "store_id": row["store_id"],
                            "is_bundled": False
                        }
                        bundles.append(bundle)
            finally:
                conn.close()
        
        # Get bundled POs for client 2 (aggregated by store)
        if 2 in target_clients:
            client2_bundles = get_all_pos(client_id=2)
            bundles.extend(client2_bundles)
        
        # Add frontend identifiers to each bundle
        for bundle in bundles:
            # Set is_bundled flag based on po_ids length
            is_bundled = len(bundle.get("po_ids", [])) > 1
            bundle["is_bundled"] = is_bundled

            # Alias po_value to total_po_value for consistency with frontend expectations if needed,
            # but frontend probably expects po_value since it's mapped to ClientPO.
            # However, po_management.py uses total_po_value below, so let's set it.
            # Ensure it's float to avoid Decimal/float type mismatch in calculations
            po_val = bundle.get("po_value", 0)
            bundle["total_po_value"] = float(po_val) if po_val else 0

            if is_bundled:
                # Add badge for bundled POs
                bundle["badge"] = {
                    "type": "bundled",
                    "label": f"Bundle ({len(bundle.get('po_ids', []))} POs)",
                    "color": "blue",
                    "icon": "package"
                }
                bundle["display_identifier"] = f"BUNDLED-{bundle.get('store_id', bundle.get('id'))}"
            else:
                # Single PO display
                bundle["badge"] = {
                    "type": "single",
                    "label": "Single PO",
                    "color": "gray",
                    "icon": "file"
                }
                bundle["display_identifier"] = bundle.get("po_number") or f"PO-{bundle['po_ids'][0]}"
        
        # Count bundled vs single POs
        bundled_count = sum(1 for b in bundles if b.get("is_bundled"))
        single_count = len(bundles) - bundled_count
        
        total_value = sum(float(b.get("total_po_value", 0)) for b in bundles)
        total_line_items = sum(int(b.get("line_count", 0)) for b in bundles)
        
        return {
            "status": "SUCCESS",
            "data": {
                "bundles": bundles,
                "bundle_count": len(bundles),
                "bundled_groups": bundled_count,
                "single_po_groups": single_count,
                "total_po_value": total_value,
                "total_line_items": total_line_items,
                "summary": {
                    "bundled_count": bundled_count,
                    "single_count": single_count
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch aggregated POs: {str(e)}")


@router.get("/po/{po_id}")
def get_single_po(po_id: int):
    """Get a single PO by ID with all details including line items"""
    try:
        po = get_po_by_id(po_id)
        if not po:
            raise HTTPException(status_code=404, detail=f"PO {po_id} not found")
        return {
            "status": "SUCCESS",
            "data": po
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PO: {str(e)}")


@router.get("/po/{po_id}/details")
def get_po_order_details(po_id: int):
    """Get order details for a specific PO (enhanced response)"""
    try:
        po = get_po_by_id(po_id)
        if not po:
            raise HTTPException(status_code=404, detail=f"PO {po_id} not found")
        
        # Get payment info if available
        from app.repository.payment_repo import get_payment_summary
        try:
            payment_summary = get_payment_summary(po_id)
        except:
            payment_summary = {"total_paid": 0, "total_tds": 0}
        
        return {
            "status": "SUCCESS",
            "data": {
                **po,
                "payment_status": "paid" if payment_summary.get("total_paid", 0) >= po["po_value"] else 
                                  "partial" if payment_summary.get("total_paid", 0) > 0 else "pending",
                "total_paid": payment_summary.get("total_paid", 0),
                "total_tds": payment_summary.get("total_tds", 0),
                "outstanding_amount": po["po_value"] - payment_summary.get("total_paid", 0)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PO details: {str(e)}")


# ==========================================
# MULTIPLE POs PER PROJECT
# ==========================================

@router.post("/projects/{project_id}/po")
def create_new_po_for_project(
    project_id: int,
    po: CreatePORequest,
    client_id: int = Query(...)
):
    try:
        client_po_id = create_po_for_project(
            client_id=client_id,
            project_id=project_id,
            po_number=po.po_number,
            po_date=po.po_date,
            po_value=po.po_value,
            po_type=po.po_type,
            parent_po_id=po.parent_po_id,
            notes=po.notes
        )
        return {
            "status": "SUCCESS",
            "message": "PO created",
            "client_po_id": client_po_id,
            "po_number": po.po_number,
            "po_type": po.po_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create PO: {str(e)}")


@router.get("/projects/{project_id}/po")
def get_project_all_pos(project_id: int):
    try:
        pos = get_all_pos_for_project(project_id)
        if not pos:
            return {
                "status": "SUCCESS",
                "project_id": project_id,
                "pos": [],
                "total_po_count": 0,
                "total_project_value": 0
            }
        total_value = sum(po["po_value"] for po in pos)
        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "pos": pos,
            "total_po_count": len(pos),
            "total_project_value": total_value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch POs: {str(e)}")


@router.post("/projects/{project_id}/po/{client_po_id}/attach")
def attach_existing_po_to_project(
    project_id: int,
    client_po_id: int,
    sequence_order: int = Query(None)
):
    try:
        result = attach_po_to_project(
            client_po_id=client_po_id,
            project_id=project_id,
            sequence_order=sequence_order
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {
            "status": "SUCCESS",
            "message": "PO attached to project"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to attach PO: {str(e)}")


@router.put("/projects/{project_id}/po/{client_po_id}/set-primary")
def set_po_as_primary(project_id: int, client_po_id: int):
    try:
        set_primary_po(client_po_id=client_po_id, project_id=project_id)
        return {
            "status": "SUCCESS",
            "message": "Primary PO set",
            "primary_po_id": client_po_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set primary PO: {str(e)}")


# ==========================================
# UPDATE PO
# ==========================================

@router.put("/po/{client_po_id}")
def update_existing_po(client_po_id: int, po: UpdatePORequest):
    try:
        result = update_po_details(
            client_po_id=client_po_id,
            po_number=po.po_number,
            po_date=po.po_date,
            po_value=po.po_value,
            pi_number=po.pi_number,
            pi_date=po.pi_date,
            notes=po.notes,
            status=po.status
        )
        if not result:
            raise HTTPException(status_code=404, detail="PO not found")
        return {
            "status": "SUCCESS",
            "message": "PO updated",
            "po": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update PO: {str(e)}")


# ==========================================
# VERBAL AGREEMENTS
# ==========================================

@router.post("/projects/{project_id}/verbal-agreement")
def create_new_verbal_agreement(
    project_id: int,
    agreement: VerbalAgreementRequest,
    client_id: int = Query(...)
):
    try:
        agreement_id = create_verbal_agreement(
            client_id=client_id,
            project_id=project_id,
            pi_number=agreement.pi_number,
            pi_date=agreement.pi_date,
            value=agreement.value,
            notes=agreement.notes
        )
        return {
            "status": "SUCCESS",
            "message": "Verbal agreement created",
            "agreement_id": agreement_id,
            "pi_number": agreement.pi_number,
            "pi_date": agreement.pi_date.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create verbal agreement: {str(e)}")


@router.put("/verbal-agreement/{agreement_id}/add-po")
def add_po_number_to_verbal_agreement(agreement_id: int, po_data: AddPOToVerbalAgreementRequest):
    try:
        result = add_po_to_verbal_agreement(
            agreement_id=agreement_id,
            po_number=po_data.po_number,
            po_date=po_data.po_date
        )
        if not result:
            raise HTTPException(status_code=404, detail="Verbal agreement not found")
        return {
            "status": "SUCCESS",
            "message": "PO number added to verbal agreement",
            "agreement_id": agreement_id,
            "pi_number": result["pi_number"],
            "po_number": result["po_number"],
            "po_date": result["po_date"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add PO to verbal agreement: {str(e)}")


@router.get("/projects/{project_id}/verbal-agreements")
def get_project_verbal_agreements(project_id: int):
    try:
        agreements = get_verbal_agreements_for_project(project_id)
        if not agreements:
            return {
                "status": "SUCCESS",
                "project_id": project_id,
                "agreements": [],
                "total_agreement_count": 0,
                "total_agreement_value": 0
            }
        total_value = sum(a["value"] for a in agreements)
        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "agreements": agreements,
            "total_agreement_count": len(agreements),
            "total_agreement_value": total_value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch verbal agreements: {str(e)}")


# ==========================================
# FINANCIAL SUMMARY
# ==========================================

@router.get("/projects/{project_id}/financial-summary")
def get_project_financial_summary(project_id: int):
    try:
        pos = get_all_pos_for_project(project_id)
        agreements = get_verbal_agreements_for_project(project_id)

        po_value = sum(po["po_value"] for po in pos)
        agreement_value = sum(a["value"] for a in agreements)
        total_project_value = po_value + agreement_value

        payment_summary = get_project_payment_summary(project_id)
        total_collected = payment_summary["total_collected"]
        outstanding_amount = total_project_value - total_collected

        vendor_count = len(set(po.get("vendor_name") for po in pos if po.get("vendor_name"))) + \
                       len(set(a.get("vendor_name") for a in agreements if a.get("vendor_name")))
        client_count = len(set(po.get("client_name") for po in pos if po.get("client_name"))) + \
                       len(set(a.get("client_name") for a in agreements if a.get("client_name")))
        active_orders = sum(1 for po in pos if po.get("status") == "active")

        net_profit = total_collected - outstanding_amount
        profit_margin = ((net_profit / total_project_value) * 100) if total_project_value > 0 else 0

        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "financial_summary": {
                "total_po_value": po_value,
                "total_agreement_value": agreement_value,
                "total_project_value": total_project_value,
                "documents": len(pos),
                "verbal_agreements": len(agreements),
                "total_collected": total_collected,
                "outstanding_amount": outstanding_amount,
                "net_profit": net_profit,
                "profit_margin_percentage": round(profit_margin, 2),
                "active_orders": active_orders,
                "vendor_count": vendor_count,
                "client_count": client_count
            },
            "purchase_orders": {
                "count": len(pos),
                "total_value": po_value,
                "orders": pos
            },
            "verbal_agreements": {
                "count": len(agreements),
                "total_value": agreement_value,
                "agreements": agreements
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch financial summary: {str(e)}")


# ==========================================
# ENRICHED POs (with payment data)
# ==========================================

@router.get("/projects/{project_id}/po/enriched")
def get_enriched_project_pos(project_id: int):
    try:
        from app.repository.payment_repo import get_payments_for_po, get_payment_summary

        pos = get_all_pos_for_project(project_id)
        enriched_pos = []

        for po in pos:
            po_id = po.get("po_id") or po.get("client_po_id")
            payments = get_payments_for_po(po_id)
            payment_summary = get_payment_summary(po_id)

            total_paid = payment_summary["total_paid"]
            total_tds = payment_summary["total_tds"]
            receivable = po["po_value"] - total_paid

            if total_paid >= po["po_value"]:
                payment_status = "paid"
            elif total_paid > 0:
                payment_status = "partial"
            else:
                payment_status = "pending"

            enriched_pos.append({
                **po,
                "total_paid": total_paid,
                "receivable_amount": receivable,
                "payment_status": payment_status,
                "total_tds": total_tds,
                "payment_details": payments,
                "payment_count": len(payments)
            })

        total_value = sum(po["po_value"] for po in enriched_pos)
        total_paid_all = sum(po["total_paid"] for po in enriched_pos)
        total_receivable = sum(po["receivable_amount"] for po in enriched_pos)

        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "pos": enriched_pos,
            "total_po_count": len(enriched_pos),
            "total_project_value": total_value,
            "total_paid": total_paid_all,
            "total_receivable": total_receivable,
            "summary": {
                "paid_count": sum(1 for po in enriched_pos if po["payment_status"] == "paid"),
                "partial_count": sum(1 for po in enriched_pos if po["payment_status"] == "partial"),
                "pending_count": sum(1 for po in enriched_pos if po["payment_status"] == "pending")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch enriched POs: {str(e)}")


# ==========================================
# DELETE PO
# ==========================================

@router.delete("/po/{client_po_id}")
def delete_po_endpoint(client_po_id: int):
    try:
        success = delete_po(client_po_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"PO {client_po_id} not found")
        return {
            "status": "SUCCESS",
            "message": "PO and associated data deleted",
            "client_po_id": client_po_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PO: {str(e)}")


# ==========================================
# PROJECT CRUD
# ==========================================

@router.post("/projects")
def create_project_endpoint(request: CreateProjectRequest):
    try:
        project_id = create_project(
            name=request.name,
            location=request.location,
            city=request.city,
            state=request.state,
            country=request.country,
            latitude=request.latitude,
            longitude=request.longitude
        )
        if project_id is None:
            raise HTTPException(status_code=409, detail=f"Project '{request.name}' already exists")
        return {
            "status": "SUCCESS",
            "message": f"Project '{request.name}' created",
            "project_id": project_id,
            "name": request.name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.delete("/projects")
def delete_project_endpoint(name: str = Query(..., description="Project name to delete")):
    try:
        result = delete_project(name)
        if not result.get("success"):
            error_msg = result.get("error", f"Project '{name}' not found")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        return {
            "status": "SUCCESS",
            "message": result.get("message"),
            "project_id": result.get("project_id"),
            "pos_deleted": result.get("pos_deleted", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")
