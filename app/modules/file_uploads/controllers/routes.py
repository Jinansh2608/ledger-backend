"""
FastAPI routes for file upload system
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, List
from app.modules.file_uploads.schemas.requests import (
    CreateSessionRequest,
    CreateClientSessionRequest,
    SessionResponse,
    FileUploadResponse,
    ListFilesResponse,
    POFilesResponse,
    DeleteFileResponse,
    ErrorResponse,
    FileMetadata,
    SessionStatsResponse,
    ParsedPOResponse
)
from app.modules.file_uploads.services.session_service import SessionService
from app.modules.file_uploads.services.file_service import FileService
from app.modules.file_uploads.services.parser_factory import ParserFactory
from app.modules.file_uploads.services.parsing_service import FileParsingService
from app.repository.client_po_repo import insert_client_po
from datetime import datetime
import io

# Create router
router = APIRouter(prefix="/uploads", tags=["file-uploads"])
file_service = FileService()


@router.post("/session", response_model=SessionResponse)
async def create_upload_session(request: CreateSessionRequest):
    """
    Create a new upload session
    
    Request body:
    ```json
    {
        "metadata": {"project": "test"},
        "ttl_hours": 24,
        "client_id": 1
    }
    ```
    """
    try:
        # Add client_id to metadata if provided
        metadata = request.metadata or {}
        if request.client_id:
            metadata['client_id'] = request.client_id
            metadata['client_name'] = ParserFactory.get_client_name(request.client_id)
        
        session = SessionService.create_session(
            metadata=metadata,
            ttl_hours=request.ttl_hours
        )
        
        return SessionResponse(
            session_id=session['session_id'],
            created_at=session['created_at'],
            expires_at=session['expires_at'],
            metadata=session['metadata'],
            status=session['status'],
            file_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get session details with file count
    """
    try:
        session = SessionService.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        return SessionResponse(
            session_id=session['session_id'],
            created_at=session['created_at'],
            expires_at=session['expires_at'],
            metadata=session['metadata'],
            status=session['status'],
            file_count=session.get('file_count', 0)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/{session_id}/files", response_model=FileUploadResponse)
async def upload_file(
    session_id: str,
    request_obj: Request,
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Query(None),
    po_number: Optional[str] = Query(None),
    auto_parse: bool = Query(True, description="Auto-parse file if client_id in session")
):
    """
    Upload a file to a session
    
    - Validates file type and size
    - Stores file securely
    - Auto-parses if client_id in session metadata (if auto_parse=True)
    - Returns file metadata with access URL
    
    Auto-parsing behavior:
    - Only triggers if session has client_id in metadata
    - Client-specific parser selected automatically (Bajaj PO or Dava India invoice)
    - Parsing errors don't fail the upload (graceful degradation)
    """
    try:
        # Validate session exists
        is_valid, error = SessionService.validate_session(session_id)
        if not is_valid:
            raise HTTPException(status_code=404, detail=f"Invalid session: {error}")
        
        # Upload file
        file_metadata = file_service.upload_file(
            session_id=session_id,
            file_content=file.file,
            original_filename=file.filename,
            uploaded_by=uploaded_by,
            po_number=po_number
        )
        
        file_id = str(file_metadata['id'])
        
        # Get session to check for client_id
        session = SessionService.get_session(session_id)
        client_id = None
        # Session returned is a dict-like object; access metadata via dict keys
        if session and isinstance(session, dict) and session.get('metadata'):
            client_id = session['metadata'].get('client_id')
        
        # Auto-parse if enabled and client_id present
        parse_status = "SKIPPED"
        parse_error = None
        client_po_id = None
        
        if auto_parse and client_id:
            try:
                file.file.seek(0)
                file_content = file.file.read()
                
                parsed_data = FileParsingService.parse_uploaded_file(
                    file_content=file_content,
                    filename=file.filename,
                    client_id=client_id,
                    session_id=session_id,
                    file_id=file_id
                )
                
                # Parsing successful - now insert into database
                if parsed_data:
                    parse_status = "SUCCESS"
                    try:
                        # Get project info from session metadata if available
                        project_id = None
                        project_name = None
                        if session and isinstance(session, dict) and session.get('metadata'):
                            project_id = session['metadata'].get('project_id')
                            project_name = session['metadata'].get('project_name') or session['metadata'].get('project')
                        
                        # Insert parsed data into client_po table
                        client_po_id = insert_client_po(parsed_data, client_id, project_id, project_name)
                        print(f"✅ Successfully inserted PO into database with ID: {client_po_id}")
                    except Exception as db_error:
                        # Log DB error but don't fail the upload (graceful degradation)
                        parse_error = str(db_error)
                        print(f"⚠️  Auto-parse succeeded but DB insertion failed for {file.filename}: {str(db_error)}")
            except Exception as parse_error_exc:
                # Capture parsing error for response
                parse_status = "FAILED"
                parse_error = str(parse_error_exc)
                # Log parsing error but don't fail the upload
                print(f"Auto-parse failed for {file.filename}: {str(parse_error_exc)}")
                import traceback
                traceback.print_exc()
        
        # Generate access URL using request base URL
        base_url = str(request_obj.base_url).rstrip("/")
        access_url = file_service.generate_access_url(
            file_id=file_id,
            session_id=session_id,
            base_url=base_url
        )
        
        # Also generate direct file URL for simple download
        direct_url = f"{base_url}/uploads/{session_id}/{file_metadata['storage_filename']}"
        
        return FileUploadResponse(
            file_id=file_id,
            session_id=file_metadata['session_id'],
            original_filename=file_metadata['original_filename'],
            file_size=file_metadata['file_size'],
            compressed_size=file_metadata.get('compressed_size'),
            is_compressed=file_metadata.get('is_compressed', True),
            mime_type=file_metadata['mime_type'],
            original_mime_type=file_metadata.get('original_mime_type'),
            file_hash=file_metadata['file_hash'],
            compressed_hash=file_metadata.get('compressed_hash'),
            upload_timestamp=file_metadata['upload_timestamp'],
            po_number=file_metadata.get('po_number'),
            access_url=access_url,
            direct_url=direct_url,
            parse_status=parse_status,
            parse_error=parse_error,
            po_id=client_po_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/po/upload", response_model=ParsedPOResponse)
async def upload_and_parse_po(
    client_id: int = Query(..., ge=1, description="Client ID (Bajaj=1, Dava India=2)"),
    project_id: Optional[int] = Query(None, description="Optional Project ID to link PO"),
    request_obj: Request = None,
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Query(None),
    auto_save: bool = Query(True, description="Automatically save parsed PO to database")
):
    """
    Upload a PO Excel file and automatically parse it based on client
    
    - Validates client_id exists
    - Creates upload session with client metadata
    - Parses file using appropriate client parser (Bajaj PO or Dava India Proforma Invoice)
    - Automatically inserts into client_po table if auto_save is True
    - Returns parsed PO data
    """
    try:
        # Validate client_id
        try:
            client_config = ParserFactory.get_parser_for_client(client_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Create session for this client
        session = SessionService.create_session(
            metadata={
                'client_id': client_id,
                'client_name': client_config['name'],
                'parser_type': client_config['parser_type'],
                'upload_type': 'po',
                'project_id': project_id
            },
            ttl_hours=24
        )
        
        session_id = session['session_id']
        
        # Upload file
        file_metadata = file_service.upload_file(
            session_id=session_id,
            file_content=file.file,
            original_filename=file.filename,
            uploaded_by=uploaded_by,
            po_number=None
        )
        
        file_id = str(file_metadata['id'])
        
        # Read file content for parsing
        file.file.seek(0)
        file_content = file.file.read()
        
        # Parse file using client-specific parser
        try:
            parsed_data = FileParsingService.parse_uploaded_file(
                file_content=file_content,
                filename=file.filename,
                client_id=client_id,
                session_id=session_id,
                file_id=file_id
            )
            
            client_po_id = None
            insertion_error = None
            if auto_save and parsed_data:
                try:
                    # Insert into business database
                    client_po_id = insert_client_po(parsed_data, client_id, project_id)
                    print(f"✅ Successfully inserted PO into database with ID: {client_po_id}")
                except ValueError as validation_error:
                    # Validation error - log but return it in response
                    insertion_error = str(validation_error)  
                    print(f"⚠️  Validation error: {insertion_error}")
                except Exception as db_error:
                    # Other DB error - log but don't fail the response
                    insertion_error = f"Database error: {str(db_error)}"
                    import traceback
                    print(f"❌ Database insertion failed: {insertion_error}")
                    traceback.print_exc()
            
            # If insertion failed due to validation, return error in po_details
            po_details_response = parsed_data.get('po_details', {})
            if insertion_error and not client_po_id:
                # Add error message to response
                if isinstance(po_details_response, dict):
                    po_details_response = {**po_details_response, "insertion_error": insertion_error}
                else:
                    po_details_response = {"insertion_error": insertion_error}
            
            return ParsedPOResponse(
                status="SUCCESS" if client_po_id else "UPLOAD_SUCCESS_PARSE_FAILED",
                file_id=file_id,
                session_id=session_id,
                client_id=client_id,
                client_name=parsed_data.get('client_name'),
                parser_type=parsed_data.get('parser_type'),
                po_details=po_details_response,
                line_items=parsed_data.get('line_items', []),
                line_item_count=parsed_data.get('line_item_count', 0),
                client_po_id=client_po_id,
                original_filename=file.filename,
                upload_timestamp=file_metadata['upload_timestamp']
            )
        except Exception as parse_error:
            # Upload succeeded but parsing failed
            return ParsedPOResponse(
                status="UPLOAD_SUCCESS_PARSE_FAILED",
                file_id=file_id,
                session_id=session_id,
                client_id=client_id,
                client_name=client_config['name'],
                parser_type=client_config['parser_type'],
                po_details={"error": str(parse_error)},
                line_items=[],
                line_item_count=0,
                original_filename=file.filename,
                upload_timestamp=file_metadata['upload_timestamp']
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/po/{po_number}", response_model=POFilesResponse)
async def get_po_files(po_number: str):
    """
    Get all files associated with a specific PO number
    """
    try:
        files = file_service.get_files_by_po_number(po_number)
        
        # Convert to response format
        file_list = [
            FileMetadata(
                id=str(f['id']),
                session_id=f['session_id'],
                original_filename=f['original_filename'],
                storage_filename=f['storage_filename'],
                file_size=f['file_size'],
                mime_type=f.get('mime_type'),
                file_hash=f.get('file_hash'),
                upload_timestamp=f['upload_timestamp'],
                uploaded_by=f.get('uploaded_by'),
                status=f['status'],
                metadata=f.get('metadata')
            )
            for f in files
        ]
        
        # Get statistics
        stats = file_service.get_po_statistics(po_number)
        
        return POFilesResponse(
            status="SUCCESS",
            po_number=po_number,
            file_count=len(files),
            total_size=stats.get('total_size_bytes', 0),
            compressed_size=stats.get('compressed_size_bytes', 0),
            compression_ratio=stats.get('compression_ratio', 0.0),
            files=file_list,
            skip=0,
            limit=50,
            total_count=len(files)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/files", response_model=ListFilesResponse)
async def list_session_files(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List all files in a session
    
    Supports pagination with skip/limit parameters
    """
    try:
        # Validate session
        session = SessionService.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get files
        files = FileService.list_session_files(session_id)
        
        # Apply pagination
        paginated_files = files[skip:skip + limit]
        
        # Convert to response format
        file_list = [
            FileMetadata(
                id=str(f['id']),
                session_id=f['session_id'],
                original_filename=f['original_filename'],
                storage_filename=f['storage_filename'],
                file_size=f['file_size'],
                mime_type=f.get('mime_type'),
                file_hash=f.get('file_hash'),
                upload_timestamp=f['upload_timestamp'],
                uploaded_by=f.get('uploaded_by'),
                status=f['status']
            )
            for f in paginated_files
        ]
        
        # Calculate total size
        total_size = sum(f['file_size'] for f in files)
        
        return ListFilesResponse(
            status="SUCCESS",
            session_id=session_id,
            file_count=len(files),
            total_size=total_size,
            files=file_list
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}/files/{file_id}/download")
async def download_file(
    session_id: str,
    file_id: str,
    token: Optional[str] = Query(None)
):
    """
    Download a file from a session
    
    Returns file as binary stream with proper Content-Disposition header
    """
    try:
        # In production, validate token for additional security
        
        file_content = file_service.download_file(
            file_id=file_id,
            session_id=session_id
        )
        
        # Return as streaming response
        return StreamingResponse(
            iter([file_content]),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=file-{file_id}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}/files/{file_id}", response_model=DeleteFileResponse)
async def delete_file(
    session_id: str,
    file_id: str,
    user_id: Optional[str] = Query(None)
):
    """
    Delete a file from a session
    
    Performs soft-delete (marks as deleted, doesn't remove from storage immediately)
    """
    try:
        success = file_service.delete_file(
            file_id=file_id,
            session_id=session_id,
            user_id=user_id
        )
        
        return DeleteFileResponse(
            file_id=file_id,
            session_id=session_id,
            deleted=success
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete an entire session and all its files
    """
    try:
        success = SessionService.delete_session(session_id)
        
        return {
            "status": "SUCCESS" if success else "ERROR",
            "message": "Session deleted successfully" if success else "Failed to delete session",
            "data": {"session_id": session_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(session_id: str):
    """
    Get statistics for an upload session
    Returns file count, total size, and other metrics
    """
    try:
        session = SessionService.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Query database directly for file statistics
        from app.database import get_db
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as file_count,
                        COALESCE(SUM(file_size), 0) as total_size
                    FROM upload_file
                    WHERE session_id = %s AND status != 'deleted'
                """, (session_id,))
                
                result = cur.fetchone()
                total_files = result['file_count'] if result else 0
                total_size = result['total_size'] if result else 0
        finally:
            conn.close()
        
        return SessionStatsResponse(
            session_id=session_id,
            total_files=total_files,
            total_size_bytes=total_size,
            total_downloads=0,  # Downloads not tracked in current schema
            created_at=session.get('created_at'),
            expires_at=session.get('expires_at'),
            status=session.get('status')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))













