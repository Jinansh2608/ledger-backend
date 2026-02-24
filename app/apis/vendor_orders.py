from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

from app.repository.vendor_order_repo import (
    create_vendor_order,
    bulk_create_vendor_orders,
    get_project_vendor_orders,
    get_vendor_order_details,
    update_vendor_order,
    update_vendor_order_status,
    delete_vendor_order,
    add_vendor_order_line_item,
    update_vendor_order_line_item,
    delete_vendor_order_line_item,
    get_vendor_order_line_items,
    get_vendor_order_payment_summary,
    link_payment_to_vendor_order
)

router = APIRouter(prefix="/api", tags=["Vendor Orders"])


class VendorOrderRequest(BaseModel):
    vendor_id: int
    po_number: Optional[str] = None
    po_date: date
    po_value: Optional[float] = 0.0
    amount: Optional[float] = None
    due_date: Optional[date] = None
    description: Optional[str] = None


class VendorOrderUpdateRequest(BaseModel):
    po_value: Optional[float] = None
    amount: Optional[float] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    work_status: Optional[str] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None


class VendorOrderStatusRequest(BaseModel):
    work_status: Optional[str] = None
    payment_status: Optional[str] = None


class LineItemRequest(BaseModel):
    item_name: str
    quantity: float
    unit_price: float


class LineItemUpdateRequest(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None


class BulkCreateRequest(BaseModel):
    orders: List[VendorOrderRequest]


class LinkPaymentRequest(BaseModel):
    link_type: str  # "incoming" or "outgoing"
    amount: Optional[float] = None
    payment_id: Optional[str] = None


# ==========================================
# VENDOR ORDER ENDPOINTS
# ==========================================

@router.post("/projects/{project_id}/vendor-orders")
def create_order(project_id: int, order: VendorOrderRequest):
    try:
        # Support both po_value and amount
        final_value = order.amount if (order.po_value is None or order.po_value == 0) and order.amount is not None else order.po_value
        
        result = create_vendor_order(
            vendor_id=order.vendor_id,
            project_id=project_id,
            po_number=order.po_number,
            po_date=order.po_date,
            po_value=final_value,
            due_date=order.due_date,
            description=order.description
        )
        return {
            "status": "SUCCESS",
            "message": "Vendor order created",
            "vendor_order": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create vendor order: {str(e)}")


@router.post("/projects/{project_id}/vendor-orders/bulk")
def bulk_create_orders(project_id: int, request: BulkCreateRequest):
    try:
        orders_data = [order.model_dump() for order in request.orders]
        results = bulk_create_vendor_orders(project_id, orders_data)
        return {
            "status": "SUCCESS",
            "message": f"Created {len(results)} vendor orders",
            "vendor_orders": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk create vendor orders: {str(e)}")


@router.get("/projects/{project_id}/vendor-orders")
def get_project_orders(project_id: int):
    try:
        orders = get_project_vendor_orders(project_id)
        return {
            "status": "SUCCESS",
            "vendor_order_count": len(orders),
            "vendor_orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendor orders: {str(e)}")


@router.get("/vendor-orders/{vendor_order_id}")
def get_order_details(vendor_order_id: int):
    try:
        order = get_vendor_order_details(vendor_order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Vendor order not found")
        return {
            "status": "SUCCESS",
            "vendor_order": order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendor order: {str(e)}")


@router.put("/projects/{project_id}/vendor-orders/{vendor_order_id}")
def update_order(project_id: int, vendor_order_id: int, order: VendorOrderUpdateRequest):
    try:
        updates = {k: v for k, v in order.model_dump().items() if v is not None}
        result = update_vendor_order(vendor_order_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Vendor order not found")
        return {
            "status": "SUCCESS",
            "message": "Vendor order updated",
            "vendor_order": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update vendor order: {str(e)}")


@router.put("/vendor-orders/{vendor_order_id}/status")
def update_order_status(vendor_order_id: int, status: VendorOrderStatusRequest):
    try:
        result = update_vendor_order_status(
            vendor_order_id,
            work_status=status.work_status,
            payment_status=status.payment_status
        )
        if not result:
            raise HTTPException(status_code=404, detail="Vendor order not found")
        return {
            "status": "SUCCESS",
            "message": "Status updated",
            "vendor_order": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.delete("/projects/{project_id}/vendor-orders/{vendor_order_id}")
def delete_order(project_id: int, vendor_order_id: int):
    try:
        success = delete_vendor_order(vendor_order_id)
        if not success:
            raise HTTPException(status_code=404, detail="Vendor order not found")
        return {"status": "SUCCESS", "message": "Vendor order deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete vendor order: {str(e)}")


# ==========================================
# LINE ITEM ENDPOINTS
# ==========================================

@router.post("/vendor-orders/{vendor_order_id}/line-items")
def add_line_item(vendor_order_id: int, item: LineItemRequest):
    try:
        result = add_vendor_order_line_item(
            vendor_order_id,
            item.item_name,
            item.quantity,
            item.unit_price
        )
        return {
            "status": "SUCCESS",
            "message": "Line item added",
            "line_item": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add line item: {str(e)}")


@router.get("/vendor-orders/{vendor_order_id}/line-items")
def get_line_items(vendor_order_id: int):
    try:
        items = get_vendor_order_line_items(vendor_order_id)
        total_value = sum(float(item['total_price']) for item in items if item.get('total_price'))
        return {
            "status": "SUCCESS",
            "vendor_order_id": vendor_order_id,
            "line_items": items,
            "line_item_count": len(items),
            "total_value": total_value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch line items: {str(e)}")


@router.put("/vendor-line-items/{item_id}")
def update_line_item(item_id: int, item: LineItemUpdateRequest):
    try:
        updates = {k: v for k, v in item.model_dump().items() if v is not None}
        result = update_vendor_order_line_item(item_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Line item not found")
        return {
            "status": "SUCCESS",
            "message": "Line item updated",
            "line_item": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update line item: {str(e)}")


@router.delete("/vendor-line-items/{item_id}")
def delete_line_item(item_id: int):
    try:
        success = delete_vendor_order_line_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Line item not found")
        return {"status": "SUCCESS", "message": "Line item deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete line item: {str(e)}")


# ==========================================
# PAYMENT LINKS
# ==========================================

@router.post("/vendor-orders/{vendor_order_id}/link-payment")
def link_payment_to_order(vendor_order_id: int, request: LinkPaymentRequest):
    """Link a payment to a vendor order"""
    try:
        order = get_vendor_order_details(vendor_order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Vendor order not found")
        
        # Link the payment
        result = link_payment_to_vendor_order(
            vendor_order_id=vendor_order_id,
            payment_id=request.payment_id,
            link_type=request.link_type
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to link payment")
        
        return {
            "status": "SUCCESS",
            "message": "Payment linked to vendor order",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to link payment: {str(e)}")


# ==========================================
# PROFIT ANALYSIS
# ==========================================

@router.get("/vendor-orders/{vendor_order_id}/profit-analysis")
def get_profit_analysis(vendor_order_id: int):
    try:
        order = get_vendor_order_details(vendor_order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Vendor order not found")
        
        summary = get_vendor_order_payment_summary(vendor_order_id)
        
        return {
            "status": "SUCCESS",
            "vendor_order_id": vendor_order_id,
            "po_value": float(order.get('po_value', 0)),
            "profit_analysis": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profit analysis: {str(e)}")
