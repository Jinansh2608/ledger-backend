from fastapi import APIRouter, HTTPException, File, UploadFile, Query, Request
from typing import Optional
from app.repository.client_po_repo import get_client_po_with_items, insert_client_po
from app.modules.file_uploads.services.parser_factory import ParserFactory
from app.modules.file_uploads.services.session_service import SessionService
from app.modules.file_uploads.services.file_service import FileService
from app.modules.file_uploads.services.parsing_service import FileParsingService
from app.modules.file_uploads.schemas.requests import ParsedPOResponse

router = APIRouter(prefix="/api", tags=["Client PO"])
file_service = FileService()


@router.get("/clients")
def get_supported_clients():
    """Get list of supported clients for PO parsing and orders"""
    try:
        clients_map = ParserFactory.get_all_clients()
        # Convert to list of objects
        clients = [
            {"id": client_id, "name": name}
            for client_id, name in clients_map.items()
        ]
        return {
            "status": "SUCCESS",
            "data": {
                "clients": clients,
                "count": len(clients)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/client-po/{client_po_id}")
def get_client_po(client_po_id: int):
    po_data = get_client_po_with_items(client_po_id)

    if not po_data:
        raise HTTPException(
            status_code=404,
            detail="Client PO not found"
        )

    return {
        "status": "SUCCESS",
        **po_data
    }


@router.post("/po/upload", response_model=ParsedPOResponse)
async def upload_and_parse_po(
    client_id: int = Query(..., ge=1, description="Client ID (Bajaj=1, Dava India=2)"),
    project_name: Optional[str] = Query(None, description="Optional Project name to link PO (will create if doesn't exist)"),
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
                'project_name': project_name
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
            project_id = None
            
            # Resolve project_name to project_id if provided
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
                    print(f"Warning: Could not resolve project name '{project_name}': {str(e)}")
            
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
            
            return ParsedPOResponse(
                status="SUCCESS",
                file_id=file_id,
                session_id=session_id,
                client_id=client_id,
                client_name=client_config['name'],
                parser_type=client_config['parser_type'],
                project_name=project_name,
                project_id=project_id,
                po_details=parsed_data.get('po_details', {}),
                line_items=parsed_data.get('line_items', []),
                line_item_count=len(parsed_data.get('line_items', [])),
                client_po_id=client_po_id,
                original_filename=file.filename,
                upload_timestamp=file_metadata['upload_timestamp'],
                dashboard_info={
                    "project_name": project_name,
                    "po_number": parsed_data.get('po_details', {}).get('po_number'),
                    "client_po_id": client_po_id,
                    "line_items_count": len(parsed_data.get('line_items', []))
                }
            )
        except Exception as parse_error:
            raise HTTPException(status_code=422, detail=f"Parsing failed: {str(parse_error)}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
