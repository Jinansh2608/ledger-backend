from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.repository.vendor_order_repo import (
    create_vendor_payment,
    get_vendor_order_payments,
    update_vendor_payment,
    delete_vendor_payment
)

router = APIRouter(prefix="/api", tags=["Vendor Payments"])


class VendorPaymentRequest(BaseModel):
    vendor_order_id: int
    payment_date: date
    amount: float
    payment_mode: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class VendorPaymentForOrderRequest(BaseModel):
    payment_date: date
    amount: float
    payment_mode: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class VendorPaymentUpdateRequest(BaseModel):
    payment_date: Optional[date] = None
    amount: Optional[float] = None
    payment_mode: Optional[str] = None
    status: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


@router.post("/vendor-orders/{vendor_order_id}/payments")
def create_payment(vendor_order_id: int, payment: VendorPaymentForOrderRequest):
    try:
        result = create_vendor_payment(
            vendor_order_id,
            payment.payment_date,
            payment.amount,
            payment.payment_mode,
            payment.reference_number,
            payment.notes
        )
        return {
            "status": "SUCCESS",
            "message": "Vendor payment recorded",
            "payment": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record vendor payment: {str(e)}")


@router.get("/vendor-orders/{vendor_order_id}/payments")
def get_payments(vendor_order_id: int):
    try:
        result = get_vendor_order_payments(vendor_order_id)
        return {
            "status": "SUCCESS",
            "vendor_order_id": vendor_order_id,
            "payments": result['payments'],
            "payment_count": result['payment_count'],
            "summary": result['summary']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendor payments: {str(e)}")


@router.put("/vendor-payments/{payment_id}")
def update_payment(payment_id: int, payment: VendorPaymentUpdateRequest):
    try:
        updates = {k: v for k, v in payment.model_dump().items() if v is not None}
        result = update_vendor_payment(payment_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Vendor payment not found")
        return {
            "status": "SUCCESS",
            "message": "Vendor payment updated",
            "payment": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update vendor payment: {str(e)}")


@router.delete("/vendor-payments/{payment_id}")
def delete_payment(payment_id: int):
    try:
        success = delete_vendor_payment(payment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Vendor payment not found")
        return {"status": "SUCCESS", "message": "Vendor payment deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete vendor payment: {str(e)}")


@router.post("/projects/{project_id}/vendor-payments")
def create_vendor_payment_record(project_id: int, payment: VendorPaymentRequest):
    try:
        result = create_vendor_payment(
            payment.vendor_order_id,
            payment.payment_date,
            payment.amount,
            payment.payment_mode,
            payment.reference_number,
            payment.notes
        )
        return {
            "status": "SUCCESS",
            "message": "Vendor payment recorded",
            "payment": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record vendor payment: {str(e)}")
