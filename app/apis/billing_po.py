from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.repository.billing_po_repo import (
    create_billing_po,
    add_billing_line_item,
    get_billing_po,
    get_project_billing_po,
    get_project_billing_summary,
    get_project_pl_analysis,
    approve_billing_po,
    update_billing_po,
    delete_billing_line_item
)
from app.repository.client_po_repo import get_client_po_with_items

router = APIRouter(prefix="/api", tags=["Billing PO"])


class BillingLineItemRequest(BaseModel):
    description: str
    qty: float
    rate: float


class CreateBillingPORequest(BaseModel):
    client_po_id: int
    billed_value: float
    billed_gst: Optional[float] = 0.0
    billing_notes: Optional[str] = None


class UpdateBillingPORequest(BaseModel):
    billed_value: Optional[float] = None
    billed_gst: Optional[float] = None
    billing_notes: Optional[str] = None


class ApproveBillingPORequest(BaseModel):
    notes: Optional[str] = None


@router.post("/projects/{project_id}/billing-po")
def create_project_billing_po(project_id: int, request: CreateBillingPORequest):
    try:
        client_po = get_client_po_with_items(request.client_po_id)
        if not client_po:
            raise HTTPException(status_code=404, detail=f"Client PO {request.client_po_id} not found")

        existing = get_project_billing_po(project_id)
        if existing:
            raise HTTPException(status_code=409, detail="Project already has an active billing PO")

        po_number = client_po.get('po', {}).get('po_number', f"BILLING-{project_id}")

        result = create_billing_po(
            client_po_id=request.client_po_id,
            project_id=project_id,
            po_number=po_number,
            billed_value=request.billed_value,
            billed_gst=request.billed_gst,
            billing_notes=request.billing_notes
        )
        return {
            "status": "SUCCESS",
            "message": "Billing PO created",
            "billing_po": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create billing PO: {str(e)}")


@router.get("/billing-po/{billing_po_id}")
def get_billing_po_details(billing_po_id: str):
    try:
        result = get_billing_po(billing_po_id)
        if not result:
            raise HTTPException(status_code=404, detail="Billing PO not found")
        return {
            "status": "SUCCESS",
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch billing PO: {str(e)}")


@router.get("/projects/{project_id}/billing-summary")
def get_project_billing_summary_endpoint(project_id: int):
    try:
        summary = get_project_billing_summary(project_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Project not found")
        return {
            "status": "SUCCESS",
            "data": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch billing summary: {str(e)}")


@router.post("/billing-po/{billing_po_id}/line-items")
def add_billing_line(billing_po_id: str, item: BillingLineItemRequest):
    try:
        po = get_billing_po(billing_po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Billing PO not found")

        result = add_billing_line_item(
            billing_po_id=billing_po_id,
            description=item.description,
            qty=item.qty,
            rate=item.rate
        )
        return {
            "status": "SUCCESS",
            "message": "Line item added",
            "line_item": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add line item: {str(e)}")


@router.get("/billing-po/{billing_po_id}/line-items")
def get_billing_line_items(billing_po_id: str):
    try:
        result = get_billing_po(billing_po_id)
        if not result:
            raise HTTPException(status_code=404, detail="Billing PO not found")

        line_items = result.get('line_items', [])
        total_value = sum(float(item['total']) for item in line_items) if line_items else 0
        return {
            "status": "SUCCESS",
            "billing_po_id": billing_po_id,
            "line_item_count": len(line_items),
            "total_value": total_value,
            "line_items": line_items
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch line items: {str(e)}")


@router.put("/billing-po/{billing_po_id}")
def update_billing_po_details(billing_po_id: str, request: UpdateBillingPORequest):
    try:
        po = get_billing_po(billing_po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Billing PO not found")

        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        if not updates:
            return {
                "status": "SUCCESS",
                "message": "No updates provided",
                "billing_po": po['billing_po']
            }

        result = update_billing_po(billing_po_id, updates)
        return {
            "status": "SUCCESS",
            "message": "Billing PO updated",
            "billing_po": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update billing PO: {str(e)}")


@router.post("/billing-po/{billing_po_id}/approve")
def approve_billing_po_endpoint(billing_po_id: str, request: ApproveBillingPORequest):
    """Approve a billing PO"""
    try:
        result = approve_billing_po(billing_po_id, notes=request.notes)
        if not result:
            raise HTTPException(status_code=404, detail="Billing PO not found")
        return {
            "status": "SUCCESS",
            "message": "Billing PO approved",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve billing PO: {str(e)}")


@router.delete("/billing-po/{billing_po_id}/line-items/{line_item_id}")
def delete_billing_line(billing_po_id: str, line_item_id: str):
    try:
        po = get_billing_po(billing_po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Billing PO not found")

        success = delete_billing_line_item(line_item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Line item not found")
        return {"status": "SUCCESS", "message": "Line item deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete line item: {str(e)}")


@router.get("/projects/{project_id}/billing-pl-analysis")
def get_project_profit_loss(project_id: int):
    """
    [DEPRECATED] Get P&L analysis for a project
    Use GET /api/projects/{project_id}/pl-analysis instead
    This endpoint is maintained for backward compatibility only
    """
    try:
        summary = get_project_billing_summary(project_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Project not found")

        financial = summary['financial_summary']
        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "analysis": {
                "baseline": {
                    "po_value": summary['original_po']['total']
                },
                "billing": {
                    "billed_value": summary['billing_po']['total']
                },
                "variance": {
                    "delta": financial['delta_value'],
                    "delta_percent": financial['delta_percent'],
                    "direction": "up" if financial['delta_value'] > 0 else "down"
                },
                "costs": {
                    "vendor_costs": financial['vendor_costs']
                },
                "profit_loss": {
                    "amount": financial['profit'],
                    "margin_percent": financial['profit_margin_percent'],
                    "status": "profit" if financial['profit'] > 0 else "loss"
                },
                "totals": {
                    "revenue": financial['final_revenue'],
                    "costs": financial['vendor_costs'],
                    "profit": financial['profit']
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate P&L analysis: {str(e)}")


@router.get("/projects/{project_id}/pl-analysis")
def get_project_pl_analysis_endpoint(project_id: int):
    """Get P&L analysis for a project (alias for billing-pl-analysis)"""
    try:
        summary = get_project_pl_analysis(project_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Project not found")

        financial = summary['financial_summary']
        return {
            "status": "SUCCESS",
            "project_id": project_id,
            "data": {
                "total_po_value": summary['original_po']['total'],
                "total_billed": summary['billing_po']['total'],
                "total_vendor_costs": summary['vendor_costs']['total'],
                "net_profit": financial['profit'],
                "profit_margin_percentage": financial['profit_margin_percent'],
                "variance": financial['delta_value'],
                "variance_percentage": financial['delta_percent'],
                "original_budget": summary['original_po']['total'],
                "final_revenue": financial['final_revenue'],
                "analysis": {
                    "baseline": {
                        "po_value": summary['original_po']['total']
                    },
                    "billing": {
                        "billed_value": summary['billing_po']['total']
                    },
                    "variance": {
                        "delta": financial['delta_value'],
                        "delta_percent": financial['delta_percent'],
                        "direction": "up" if financial['delta_value'] > 0 else "down"
                    },
                    "costs": {
                        "vendor_costs": financial['vendor_costs']
                    },
                    "profit_loss": {
                        "amount": financial['profit'],
                        "margin_percent": financial['profit_margin_percent'],
                        "status": "profit" if financial['profit'] > 0 else "loss"
                    },
                    "totals": {
                        "revenue": financial['final_revenue'],
                        "costs": financial['vendor_costs'],
                        "profit": financial['profit']
                    }
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate P&L analysis: {str(e)}")
