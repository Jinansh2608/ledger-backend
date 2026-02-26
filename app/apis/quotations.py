from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.database import get_db
from app.repository.quotation_repo import (
    create_quotation,
    get_quotations_by_store_id,
    get_quotation_details,
    delete_quotation
)

router = APIRouter(prefix="/api/quotations", tags=["Quotations"])

class QuotationHeader(BaseModel):
    storeId: str
    storeLocation: str
    fullAddress: str
    companyName: str
    totalArea: str
    totalAmount: Optional[float] = 0
    subtotal: Optional[float] = 0
    totalGST: Optional[float] = 0

class QuotationLineItem(BaseModel):
    name: str
    hsn_sac_code: Optional[str] = None
    type_of_boq: Optional[str] = None
    quantity: float = 1
    units: Optional[str] = None
    price: float = 0
    tax: float = 18
    gst_amount: float = 0
    total: float = 0

class QuotationCreateRequest(BaseModel):
    header: QuotationHeader
    lineItems: List[QuotationLineItem]

@router.post("")
def save_quotation(data: QuotationCreateRequest):
    try:
        result = create_quotation(data.header.model_dump(), [item.model_dump() for item in data.lineItems])
        return {
            "status": "SUCCESS",
            "message": "Quotation saved successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
def list_all_quotations():
    try:
        conn = get_db()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, store_id, store_location, company_name, total_amount, status, created_at FROM quotation ORDER BY created_at DESC")
                results = cur.fetchall()
        return {
            "status": "SUCCESS",
            "count": len(results),
            "quotations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def list_quotations(store_id: str = Query(..., description="Filter by Store ID")):
    try:
        results = get_quotations_by_store_id(store_id)
        return {
            "status": "SUCCESS",
            "count": len(results),
            "quotations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{quotation_id}")
def get_quotation(quotation_id: int):
    try:
        result = get_quotation_details(quotation_id)
        if not result:
            raise HTTPException(status_code=404, detail="Quotation not found")
        return {
            "status": "SUCCESS",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{quotation_id}")
def delete_quotation_endpoint(quotation_id: int):
    try:
        success = delete_quotation(quotation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Quotation not found")
        return {"status": "SUCCESS", "message": "Quotation deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
