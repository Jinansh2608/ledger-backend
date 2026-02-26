import os
import uuid
import shutil
import zipfile
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.utils.bajaj_po_parser import parse_bajaj_po, BajajPOParserError
from app.repository.client_po_repo import insert_client_po
from app.repository.document_repo import insert_document

router = APIRouter(prefix="/api", tags=["Bajaj PO"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/bajaj-po/bulk")
async def bulk_upload_bajaj_po(
    files: List[UploadFile] = File(...),
    client_id: int = Query(...),
    project_id: int | None = Query(None)
):
    """
    Bulk upload multiple Bajaj PO files for a client.
    
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
        "uploaded_pos": [],
        "errors": []
    }
    
    for file in files:
        try:
            if not file.filename.lower().endswith((".xlsx", ".xls", ".pdf")):
                results["errors"].append({
                    "filename": file.filename,
                    "error": f"Only PDF and Excel files are allowed. Got {os.path.splitext(file.filename)[1]}"
                })
                results["failed"] += 1
                continue
            
            temp_path = os.path.join(
                UPLOAD_DIR,
                f"{uuid.uuid4()}_{file.filename}"
            )
            
            try:
                # Save uploaded file
                with open(temp_path, "wb") as f:
                    f.write(await file.read())
                
                # Parse PO
                parsed = parse_bajaj_po(temp_path)
                
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
                    shutil.copyfile(temp_path, stored_path)
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
                            description="Bajaj PO bulk upload"
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
                
                results["uploaded_pos"].append({
                    "client_po_id": client_po_id,
                    "filename": file.filename,
                    "po_number": parsed["po_details"].get("po_number"),
                    "po_value": parsed["po_details"] .get("po_value", 0),
                    "store_id": parsed["po_details"].get("store_id"),
                    "line_item_count": parsed["line_item_count"]
                })
                results["successful"] += 1
            
            except BajajPOParserError as e:
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
            
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
        
        except Exception as e:
            results["errors"].append({
                "filename": file.filename if hasattr(file, 'filename') else 'unknown',
                "error": str(e)
            })
            results["failed"] += 1
    
    return results

