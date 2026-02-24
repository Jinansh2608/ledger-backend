from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from datetime import date
from app.repository import payment_repo

router = APIRouter(prefix="/api", tags=["Payments"])


class PaymentCreate(BaseModel):
    payment_date: date
    amount: float
    payment_mode: str
    status: str = "pending"
    payment_stage: str = "other"
    notes: Optional[str] = None
    is_tds_deducted: bool = False
    tds_amount: float = 0
    received_by_account: Optional[str] = None
    transaction_type: str = "credit"
    reference_number: Optional[str] = None


class PaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    amount: Optional[float] = None
    payment_mode: Optional[str] = None
    status: Optional[str] = None
    payment_stage: Optional[str] = None
    notes: Optional[str] = None
    is_tds_deducted: Optional[bool] = None
    tds_amount: Optional[float] = None
    received_by_account: Optional[str] = None
    transaction_type: Optional[str] = None
    reference_number: Optional[str] = None


@router.post("/po/{po_id}/payments")
def create_payment(po_id: int, payment: PaymentCreate):
    try:
        payment_id = payment_repo.create_payment(
            client_po_id=po_id,
            payment_date=payment.payment_date,
            amount=payment.amount,
            payment_mode=payment.payment_mode,
            status=payment.status,
            payment_stage=payment.payment_stage,
            notes=payment.notes,
            is_tds_deducted=payment.is_tds_deducted,
            tds_amount=payment.tds_amount,
            received_by_account=payment.received_by_account,
            transaction_type=payment.transaction_type,
            reference_number=payment.reference_number
        )
        return {
            "status": "SUCCESS",
            "message": "Payment recorded",
            "payment_id": payment_id,
            "payment_date": payment.payment_date.isoformat(),
            "amount": payment.amount,
            "payment_mode": payment.payment_mode,
            "payment_stage": payment.payment_stage,
            "payment_status": payment.status,
            "transaction_type": payment.transaction_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")


@router.get("/payments")
def get_all_payments(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=500)):
    """Get all payments with optional pagination"""
    try:
        payments = payment_repo.get_all_payments(skip=skip, limit=limit)
        total_count = payment_repo.get_total_payment_count()
        return {
            "status": "SUCCESS",
            "payments": payments,
            "payment_count": len(payments),
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payments: {str(e)}")


@router.get("/po/{po_id}/payments")
def get_po_payments(po_id: int):
    try:
        payments = payment_repo.get_payments_for_po(po_id)
        summary = payment_repo.get_payment_summary(po_id)
        return {
            "status": "SUCCESS",
            "po_id": po_id,
            "payments": payments,
            "payment_count": len(payments),
            "summary": {
                "total_paid": summary.get("total_paid", 0),
                "total_tds": summary.get("total_tds", 0),
                "cleared_count": len([p for p in payments if p["status"] == "cleared"]),
                "pending_count": len([p for p in payments if p["status"] == "pending"]),
                "bounced_count": len([p for p in payments if p["status"] == "bounced"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payments: {str(e)}")


@router.put("/payments/{payment_id}")
def update_payment(payment_id: int, payment: PaymentUpdate):
    try:
        success = payment_repo.update_payment(payment_id, **payment.model_dump(exclude_unset=True))
        if not success:
            raise HTTPException(status_code=404, detail="Payment not found")
        return {"status": "SUCCESS", "message": "Payment updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update payment: {str(e)}")


@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):
    try:
        success = payment_repo.delete_payment(payment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Payment not found")
        return {"status": "SUCCESS", "message": "Payment deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete payment: {str(e)}")
