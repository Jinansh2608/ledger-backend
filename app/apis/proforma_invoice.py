# app/apis/proforma_invoice.py
"""
Proforma Invoice Upload & Parsing API

Endpoints:
  POST /api/proforma-invoice/upload
    - Upload PI Excel file
    - Parse and validate
    - Insert into database
    - Return parsed data with validation results
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil
import uuid
import zipfile
from typing import List
from app.utils.proforma_invoice_parser import parse_proforma_invoice, ProformaInvoiceParserError
from app.repository.client_po_repo import insert_client_po
from app.repository.document_repo import insert_document

router = APIRouter(prefix="/api", tags=["Proforma Invoice"])


@router.post("/proforma-invoice/upload")
async def upload_proforma_invoice(
    file: UploadFile = File(...),
    client_id: int = Form(...),
    project_name: str = Form(None)
):
    """
    Upload and parse a Proforma Invoice Excel file.
    
    Args:
        file: Excel file (.xlsx)
        client_id: Client ID (required)
        project_name: Project name to link PO (optional, will create if doesn't exist)
    
    Returns:
        {
            "status": "SUCCESS" | "VALIDATION_ERROR" | "PARSE_ERROR",
            "parsed_data": {...},
            "client_po_id": int (if successful),
            "project_name": str (name used for linking),
            "validation_errors": [...] (if any),
            "message": str
        }
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files (.xlsx, .xls) are supported"
        )
    
    # Save uploaded file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file_path = tmp.name
        
        # ========================================
        # Parse the Proforma Invoice
        # ========================================
        try:
            parsed = parse_proforma_invoice(temp_file_path)
        except ProformaInvoiceParserError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Parse error: {str(e)}"
            )
        
        # ========================================
        # Validate parsed data
        # ========================================
        validation_errors = _validate_proforma_invoice(parsed)
        
        if validation_errors:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "VALIDATION_ERROR",
                    "parsed_data": parsed,
                    "validation_errors": validation_errors,
                    "message": f"{len(validation_errors)} validation error(s) found"
                }
            )
        
        # ========================================
        # Resolve project_name to project_id
        # ========================================
        project_id = None
        if project_name:
            try:
                from app.database import get_db
                conn = get_db()
                try:
                    with conn.cursor() as cur:
                        # Try to find existing project by name
                        cur.execute(
                            "SELECT id FROM project WHERE name = %s AND client_id = %s LIMIT 1",
                            (project_name, client_id)
                        )
                        result = cur.fetchone()
                        if result:
                            project_id = result["id"]
                        else:
                            # Create new project if it doesn't exist
                            cur.execute(
                                "INSERT INTO project (client_id, name, status) VALUES (%s, %s, 'Active') RETURNING id",
                                (client_id, project_name)
                            )
                            project_id = cur.fetchone()["id"]
                            conn.commit()
                finally:
                    conn.close()
            except Exception as e:
                # Log error but don't fail - project_id will be None
                print(f"Warning: Could not resolve project name '{project_name}': {str(e)}")
        
        # ========================================
        # Insert into database
        # ========================================
        try:
            client_po_id = insert_client_po(parsed, client_id, project_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
        # Persist uploaded file to uploads folder, compress and map to PO
        try:
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
            uploads_dir = os.path.normpath(os.path.abspath(uploads_dir))
            os.makedirs(uploads_dir, exist_ok=True)

            ext = os.path.splitext(file.filename)[1] or '.xlsx'
            unique_name = f"{uuid.uuid4().hex}{ext}"
            stored_path = os.path.join(uploads_dir, unique_name)

            # Copy temp file to uploads
            shutil.copyfile(temp_file_path, stored_path)
            original_size = os.path.getsize(stored_path)

            # Create compressed zip
            zip_name = f"{uuid.uuid4().hex}.zip"
            zip_path = os.path.join(uploads_dir, zip_name)
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(stored_path, arcname=file.filename)

            compressed_size = os.path.getsize(zip_path)

            # Insert document metadata mapping to PO
            try:
                insert_document(project_id=project_id, client_po_id=client_po_id,
                                original_filename=file.filename, stored_filename=unique_name,
                                compressed_filename=zip_name, mime_type=file.content_type,
                                original_size=original_size, compressed_size=compressed_size,
                                description="Proforma Invoice upload")
            except Exception:
                # On DB failure, cleanup files
                try:
                    os.remove(stored_path)
                except: pass
                try:
                    os.remove(zip_path)
                except: pass

        except Exception:
            # non-fatal for main flow, log could be added
            pass

        return {
            "status": "SUCCESS",
            "client_po_id": client_po_id,
            "project_name": project_name,
            "project_id": project_id,
            "po_number": parsed.get("po_details", {}).get("po_number"),
            "pi_number": parsed.get("po_details", {}).get("pi_number"),
            "parsed_data": parsed,
            "line_item_count": parsed.get("line_item_count", 0),
            "message": f"Proforma Invoice uploaded and parsed. {parsed.get('line_item_count', 0)} line items created.",
            "dashboard_info": {
                "project_name": project_name,
                "po_number": parsed.get("po_details", {}).get("po_number"),
                "client_po_id": client_po_id,
                "line_items_count": parsed.get("line_item_count", 0)
            }
        }
    
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def _validate_proforma_invoice(parsed: dict) -> list:
    """
    Validate parsed Proforma Invoice structure and values.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    po = parsed.get("po_details", {})
    items = parsed.get("line_items", [])
    
    # ========== Required header fields ==========
    if not po.get("client_name"):
        errors.append("Missing: Client name (Bill To)")
    
    if not po.get("vendor_name"):
        errors.append("Missing: Vendor name")
    
    if not po.get("pi_number"):
        errors.append("Missing: PI number")
    
    if not po.get("pi_date"):
        errors.append("Missing: PI date")
    
    # ========== Required GST fields ==========
    if not po.get("bill_to_gstin"):
        errors.append("Missing: Bill To GSTIN")
    
    if not po.get("vendor_gstin"):
        errors.append("Missing: Vendor GSTIN")
    
    # ========== Line items validation ==========
    if not items:
        errors.append("Missing: No BOQ line items found")
    
    for idx, item in enumerate(items, start=1):
        if not item.get("boq_name"):
            errors.append(f"Line {idx}: Missing BOQ name")
        
        if not item.get("quantity"):
            errors.append(f"Line {idx}: Missing or invalid quantity")
        
        if not item.get("rate"):
            errors.append(f"Line {idx}: Missing or invalid rate")
        
        if item.get("gross_amount", 0) <= 0:
            errors.append(f"Line {idx}: Gross amount must be > 0")
    
    # ========== Tax summary validation ==========
    if items and po:
        calculated_total = sum(
            item.get("gross_amount", 0)
            for item in items
        )
        
        reported_total = po.get("total_amount", 0)
        
        # Allow small rounding differences (0.5%)
        if abs(calculated_total - reported_total) > calculated_total * 0.005:
            errors.append(
                f"Total mismatch: Calculated {calculated_total:.2f} vs "
                f"Reported {reported_total:.2f}"
            )
    
    return errors


@router.get("/proforma-invoice/validate/{client_po_id}")
def validate_proforma_invoice(client_po_id: int):
    """
    Validate stored Proforma Invoice data for consistency.
    
    Checks:
      - Line item totals match PO totals
      - Tax breakdown is correct
      - All required fields present
    """
    from app.repository.client_po_repo import get_client_po_with_items
    
    po_data = get_client_po_with_items(client_po_id)
    
    if not po_data:
        raise HTTPException(
            status_code=404,
            detail="Client PO not found"
        )
    
    validation_errors = []
    
    # ========== Validate line item totals ==========
    items = po_data.get("line_items", [])
    calculated_subtotal = sum(
        item.get("taxable_amount", 0) for item in items
    )
    
    reported_subtotal = po_data.get("summary", {}).get("subtotal", 0)
    if abs(calculated_subtotal - reported_subtotal) > 0.01:
        validation_errors.append(
            f"Subtotal mismatch: Calculated {calculated_subtotal:.2f} vs "
            f"Reported {reported_subtotal:.2f}"
        )
    
    # ========== Validate tax totals ==========
    summary = po_data.get("summary", {})
    cgst = summary.get("cgst", 0) or 0
    sgst = summary.get("sgst", 0) or 0
    igst = summary.get("igst", 0) or 0
    reported_total_tax = summary.get("total_tax", 0) or 0
    calculated_total_tax = cgst + sgst + igst
    
    if abs(calculated_total_tax - reported_total_tax) > 0.01:
        validation_errors.append(
            f"Tax total mismatch: Calculated {calculated_total_tax:.2f} vs "
            f"Reported {reported_total_tax:.2f}"
        )
    
    # ========== Validate grand total ==========
    calculated_grand = reported_subtotal + calculated_total_tax
    reported_grand = summary.get("grand_total", 0) or 0
    
    if abs(calculated_grand - reported_grand) > 0.01:
        validation_errors.append(
            f"Grand total mismatch: Calculated {calculated_grand:.2f} vs "
            f"Reported {reported_grand:.2f}"
        )
    
    return {
        "status": "VALID" if not validation_errors else "INVALID",
        "client_po_id": client_po_id,
        "line_item_count": len(items),
        "validation_errors": validation_errors,
        "po_data": po_data
    }

@router.post("/proforma-invoice/bulk")
async def bulk_upload_proforma_invoice(
    files: List[UploadFile] = File(...),
    client_id: int = Query(...),
    project_id: int | None = Query(None)
):
    """
    Bulk upload multiple Proforma Invoice files for a client.
    
    Returns aggregated results for all uploaded files.
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one file must be provided"
        )
    
    results = {
        "status": "SUCCESS",
        "total_files": len(files),
        "successful": 0,
        "failed": 0,
        "uploaded_pis": [],
        "errors": []
    }
    
    for file in files:
        temp_file_path = None
        try:
            if not file.filename.lower().endswith((".xlsx", ".xls")):
                results["errors"].append({
                    "filename": file.filename,
                    "error": "Only Excel files are allowed"
                })
                results["failed"] += 1
                continue
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                content = await file.read()
                tmp.write(content)
                temp_file_path = tmp.name
            
            # Parse the Proforma Invoice
            try:
                parsed = parse_proforma_invoice(temp_file_path)
                
                # Insert into DB
                client_po_id = insert_client_po(
                    parsed=parsed,
                    client_id=client_id,
                    project_id=project_id
                )
                
                # Persist uploaded file
                try:
                    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
                    uploads_dir = os.path.normpath(os.path.abspath(uploads_dir))
                    os.makedirs(uploads_dir, exist_ok=True)
                    
                    ext = os.path.splitext(file.filename)[1] or '.xlsx'
                    unique_name = f"{uuid.uuid4().hex}{ext}"
                    stored_path = os.path.join(uploads_dir, unique_name)
                    shutil.copyfile(temp_file_path, stored_path)
                    original_size = os.path.getsize(stored_path)
                    
                    zip_name = f"{uuid.uuid4().hex}.zip"
                    zip_path = os.path.join(uploads_dir, zip_name)
                    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                        zf.write(stored_path, arcname=file.filename)
                    
                    compressed_size = os.path.getsize(zip_path)
                    
                    try:
                        insert_document(
                            project_id=project_id,
                            client_po_id=client_po_id,
                            original_filename=file.filename,
                            stored_filename=unique_name,
                            compressed_filename=zip_name,
                            mime_type=file.content_type,
                            original_size=original_size,
                            compressed_size=compressed_size,
                            description="Proforma Invoice bulk upload"
                        )
                    except Exception:
                        try:
                            os.remove(stored_path)
                        except:
                            pass
                        try:
                            os.remove(zip_path)
                        except:
                            pass
                except Exception:
                    pass
                
                results["uploaded_pis"].append({
                    "client_po_id": client_po_id,
                    "filename": file.filename,
                    "pi_number": parsed["po_details"].get("pi_number"),
                    "po_value": parsed["po_details"].get("subtotal", 0),
                    "store_id": parsed["po_details"].get("store_id"),
                    "line_item_count": parsed["line_item_count"]
                })
                results["successful"] += 1
            
            except ProformaInvoiceParserError as e:
                results["errors"].append({
                    "filename": file.filename,
                    "error": f"Parse error: {str(e)}"
                })
                results["failed"] += 1
            
            except Exception as e:
                results["errors"].append({
                    "filename": file.filename,
                    "error": str(e)
                })
                results["failed"] += 1
        
        except Exception as e:
            results["errors"].append({
                "filename": file.filename if hasattr(file, 'filename') else 'unknown',
                "error": str(e)
            })
            results["failed"] += 1
        
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
    
    return results