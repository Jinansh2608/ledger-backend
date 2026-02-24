from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.repository.vendor_order_repo import (
    create_vendor,
    get_all_vendors,
    get_vendor_details,
    update_vendor,
    delete_vendor,
    get_vendor_payments,
    get_vendor_payment_summary,
    get_project_vendor_summary
)

router = APIRouter(prefix="/api", tags=["Vendors"])


class VendorRequest(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None


class VendorUpdateRequest(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = None


@router.post("/vendors")
def create_new_vendor(vendor: VendorRequest):
    try:
        result = create_vendor(
            name=vendor.name,
            contact_person=vendor.contact_person,
            email=vendor.email,
            phone=vendor.phone,
            address=vendor.address,
            payment_terms=vendor.payment_terms
        )
        return {
            "status": "SUCCESS",
            "message": "Vendor created",
            "vendor": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create vendor: {str(e)}")


@router.get("/vendors")
def get_vendors(status: Optional[str] = None):
    try:
        vendors = get_all_vendors(status=status)
        return {
            "status": "SUCCESS",
            "vendor_count": len(vendors),
            "vendors": vendors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendors: {str(e)}")


@router.get("/vendors/{vendor_id}")
def get_vendor(vendor_id: int):
    try:
        vendor = get_vendor_details(vendor_id)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return {
            "status": "SUCCESS",
            "vendor": vendor
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendor: {str(e)}")


@router.put("/vendors/{vendor_id}")
def update_existing_vendor(vendor_id: int, vendor: VendorUpdateRequest):
    try:
        updates = {k: v for k, v in vendor.model_dump().items() if v is not None}
        result = update_vendor(vendor_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return {
            "status": "SUCCESS",
            "message": "Vendor updated",
            "vendor": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update vendor: {str(e)}")


@router.delete("/vendors/{vendor_id}")
def delete_existing_vendor(vendor_id: int):
    try:
        success = delete_vendor(vendor_id)
        if not success:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return {"status": "SUCCESS", "message": "Vendor deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete vendor: {str(e)}")


@router.get("/vendors/{vendor_id}/payments")
def get_vendor_payment_history(vendor_id: int):
    try:
        payments = get_vendor_payments(vendor_id)
        if payments is None:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return {
            "status": "SUCCESS",
            "vendor_id": vendor_id,
            "payments": payments,
            "payment_count": len(payments)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendor payments: {str(e)}")


@router.get("/vendors/{vendor_id}/payment-summary")
def get_vendor_summary(vendor_id: int):
    try:
        summary = get_vendor_payment_summary(vendor_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return {
            "status": "SUCCESS",
            "vendor_id": vendor_id,
            "data": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vendor payment summary: {str(e)}")


@router.get("/projects/{project_id}/vendor-summary")
def get_project_vendor_summary_endpoint(project_id: int):
    try:
        summary = get_project_vendor_summary(project_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Project not found")
        return {
            "status": "SUCCESS",
            "data": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project vendor summary: {str(e)}")
