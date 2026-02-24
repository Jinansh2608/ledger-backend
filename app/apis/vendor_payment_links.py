from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.repository.vendor_order_repo import (
    link_payment_to_vendor_order,
    get_vendor_order_linked_payments,
    get_vendor_order_payment_summary,
    unlink_payment_by_payment_id
)

router = APIRouter(prefix="/api", tags=["Payment Links"])


class PaymentLinkRequest(BaseModel):
    payment_id: int
    link_type: str  # incoming or outgoing


@router.post("/vendor-orders/{vendor_order_id}/link-payment")
def link_payment(vendor_order_id: int, link: PaymentLinkRequest):
    try:
        result = link_payment_to_vendor_order(
            vendor_order_id,
            link.payment_id,
            link.link_type
        )
        return {
            "status": "SUCCESS",
            "message": "Payment linked",
            "link": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to link payment: {str(e)}")


@router.get("/vendor-orders/{vendor_order_id}/linked-payments")
def get_linked_payments(vendor_order_id: int):
    try:
        payments = get_vendor_order_linked_payments(vendor_order_id)
        incoming = [p for p in payments if p['link_type'] == 'incoming']
        outgoing = [p for p in payments if p['link_type'] == 'outgoing']
        return {
            "status": "SUCCESS",
            "vendor_order_id": vendor_order_id,
            "incoming_payments": incoming,
            "outgoing_payments": outgoing,
            "total_linked": len(payments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch linked payments: {str(e)}")


@router.get("/vendor-orders/{vendor_order_id}/payment-summary")
def get_payment_summary(vendor_order_id: int):
    try:
        summary = get_vendor_order_payment_summary(vendor_order_id)
        return {
            "status": "SUCCESS",
            "vendor_order_id": vendor_order_id,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment summary: {str(e)}")


@router.delete("/vendor-orders/{vendor_order_id}/payments/{payment_id}")
def unlink_payment_from_order(vendor_order_id: int, payment_id: int):
    try:
        success = unlink_payment_by_payment_id(vendor_order_id, payment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Payment link not found")
        return {"status": "SUCCESS", "message": "Payment unlinked"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlink payment: {str(e)}")
