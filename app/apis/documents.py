from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
import os
import uuid
import zipfile
from app.repository.document_repo import insert_document, get_documents_for_project, get_document_by_id
from app.repository.document_repo import get_documents_for_po
from app.database import get_db

router = APIRouter(prefix="/api", tags=["Documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
UPLOAD_DIR = os.path.normpath(os.path.abspath(UPLOAD_DIR))


@router.post('/documents/upload')
async def upload_document(request: Request,
                          file: UploadFile = File(...),
                          project_id: int = Form(None),
                          client_po_id: int = Form(None),
                          po_number: str = Form(None),
                          description: str = Form(None)):
    # Ensure upload dir exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save original file with unique name
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(stored_path, 'wb') as f:
        f.write(content)

    original_size = os.path.getsize(stored_path)

    # Create compressed zip
    zip_name = f"{uuid.uuid4().hex}.zip"
    zip_path = os.path.join(UPLOAD_DIR, zip_name)
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(stored_path, arcname=file.filename)

    compressed_size = os.path.getsize(zip_path)

    # Map PO number to client_po_id/project_id if provided
    resolved_client_po_id = None
    resolved_project_id = project_id

    if client_po_id:
        resolved_client_po_id = client_po_id
        # try to fetch project_id from PO
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT project_id FROM client_po WHERE id = %s", (client_po_id,))
                r = cur.fetchone()
                if r and r.get("project_id"):
                    resolved_project_id = r.get("project_id")
        finally:
            conn.close()
    elif po_number:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, project_id FROM client_po WHERE po_number = %s OR pi_number = %s LIMIT 1", (po_number, po_number))
                r = cur.fetchone()
                if r:
                    resolved_client_po_id = r.get("id")
                    if r.get("project_id"):
                        resolved_project_id = r.get("project_id")
        finally:
            conn.close()

    # Persist metadata in DB
    try:
        doc_id = insert_document(
            project_id=resolved_project_id,
            client_po_id=resolved_client_po_id,
            original_filename=file.filename,
            stored_filename=unique_name,
            compressed_filename=zip_name,
            mime_type=file.content_type,
            original_size=original_size,
            compressed_size=compressed_size,
            description=description
        )
    except Exception as e:
        # Cleanup files on DB failure
        try:
            os.remove(stored_path)
        except:  # noqa: E722
            pass
        try:
            os.remove(zip_path)
        except:  # noqa: E722
            pass
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    # Build absolute download URL using request base
    base = str(request.base_url).rstrip("/")
    download_url = f"{base}/uploads/{zip_name}"

    return {
        "status": "SUCCESS",
        "document_id": doc_id,
        "download_url": download_url,
        "original_filename": file.filename,
        "compressed_filename": zip_name,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "project_id": resolved_project_id,
        "client_po_id": resolved_client_po_id
    }


@router.get('/documents/project/{project_id}')
def list_documents_for_project(project_id: int):
    docs = get_documents_for_project(project_id)
    # Attach public URL
    for d in docs:
        d['download_url'] = f"/uploads/{d['compressed_filename']}"
    return {"status": "SUCCESS", "documents": docs}


@router.get('/documents/po/{client_po_id}')
def list_documents_for_po(client_po_id: int):
    docs = get_documents_for_po(client_po_id)
    for d in docs:
        d['download_url'] = f"/uploads/{d['compressed_filename']}"
    return {"status": "SUCCESS", "documents": docs}


@router.get('/documents/{doc_id}')
def get_document(doc_id: int):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc['download_url'] = f"/uploads/{doc['compressed_filename']}"
    return doc


@router.get('/documents/download/{doc_id}')
def download_document(doc_id: int):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
    uploads_dir = os.path.normpath(os.path.abspath(uploads_dir))
    file_path = os.path.join(uploads_dir, doc['compressed_filename'])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # Serve compressed file but set filename to original name + .zip for client
    suggested_name = f"{os.path.splitext(doc['original_filename'])[0]}.zip"
    return FileResponse(path=file_path, filename=suggested_name, media_type='application/zip')
