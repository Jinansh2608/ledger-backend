"""
File Parsing Service - Handles automatic parsing of uploaded files based on client
"""

import os
import tempfile
import gzip
import io
from app.modules.file_uploads.services.parser_factory import ParserFactory
from app.database import get_db


class FileParsingService:
    """Service for parsing uploaded files based on client configuration"""
    
    @staticmethod
    def _decompress_if_gzipped(file_content: bytes) -> bytes:
        """
        Decompress file content if it was gzipped, otherwise return as-is
        
        Args:
            file_content: File content (possibly gzipped)
            
        Returns:
            bytes: Decompressed file content
        """
        try:
            # Try to decompress as gzip
            compressed_buffer = io.BytesIO(file_content)
            with gzip.GzipFile(fileobj=compressed_buffer, mode='rb') as gz:
                return gz.read()
        except (OSError, gzip.BadGzipFile, EOFError):
            # Not a gzip file, return as-is
            return file_content
        except Exception as e:
            print(f"Decompression error (returning original): {e}")
            return file_content
    
    @staticmethod
    def parse_uploaded_file(file_content: bytes, filename: str, client_id: int, session_id: str, file_id: str) -> dict:
        """
        Parse an uploaded file using the appropriate parser for the client
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            client_id: ID of the client
            session_id: ID of the upload session
            file_id: ID of the uploaded file
            
        Returns:
            dict with parsing results
            
        Raises:
            ValueError: If client not found
            Exception: If parsing fails
        """
        
        # Handle gzipped files (decompress first)
        decompressed_content = FileParsingService._decompress_if_gzipped(file_content)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(decompressed_content)
            tmp_path = tmp.name
        
        try:
            # Parse using factory
            parsed_data = ParserFactory.parse_file(tmp_path, client_id)
            
            # Add metadata
            parsed_data["file_id"] = file_id
            parsed_data["session_id"] = session_id
            parsed_data["original_filename"] = filename
            parsed_data["parsing_status"] = "SUCCESS"
            
            # Store parsing result in database
            FileParsingService._store_parsing_result(
                file_id=file_id,
                client_id=client_id,
                parsed_data=parsed_data
            )
            
            return parsed_data
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    @staticmethod
    def _store_parsing_result(file_id: str, client_id: int, parsed_data: dict):
        """
        Store parsing results in database
        
        Args:
            file_id: ID of the file
            client_id: ID of the client
            parsed_data: Parsed data dictionary
        """
        try:
            import json
            conn = get_db()
            with conn.cursor() as cursor:
                # Get client name
                client_config = ParserFactory.get_parser_for_client(client_id)
                
                # Prepare metadata as JSON
                metadata = {
                    'parsed': True,
                    'parser_type': parsed_data.get('parser_type'),
                    'client_name': parsed_data.get('client_name'),
                    'po_details': parsed_data.get('po_details'),
                    'line_items': parsed_data.get('line_items', []),
                    'line_item_count': parsed_data.get('line_item_count', 0)
                }
                
                # Convert to JSON string for storage
                metadata_json = json.dumps(metadata)
                
                # Update file record with parsed data
                cursor.execute(
                    """
                    UPDATE "Finances"."upload_file" 
                    SET metadata = %s::jsonb
                    WHERE id = %s
                    """,
                    (metadata_json, file_id)
                )
                conn.commit()
            conn.close()
        except Exception as e:
            # Log error but don't fail - file is already uploaded
            print(f"Error storing parsing result: {e}")
    
    @staticmethod
    def get_parsed_data(file_id: str) -> dict:
        """
        Retrieve parsed data for a file
        
        Args:
            file_id: ID of the file
            
        Returns:
            dict with parsed data or empty dict if not found
        """
        try:
            conn = get_db()
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT metadata FROM "Finances"."upload_file" WHERE id = %s',
                    (file_id,)
                )
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    return result[0]
                return {}
        except:
            return {}
