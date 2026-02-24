"""
Local file system storage provider implementation
"""

from .base import StorageProvider
from typing import Optional, BinaryIO
from pathlib import Path
import os
import hashlib
from datetime import datetime


class LocalStorageProvider(StorageProvider):
    """Local file system implementation of storage provider"""
    
    def __init__(self, base_path: str = None):
        """
        Initialize local storage provider
        
        Args:
            base_path: Base directory for file storage
        """
        self.base_path = Path(base_path) if base_path else Path("uploads/sessions")
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, file_path: str, file_name: str) -> Path:
        """Get full path for a file"""
        # Prevent directory traversal
        session_path = Path(file_path)
        if ".." in session_path.parts:
            raise ValueError("Invalid file path: contains parent directory references")
        
        full_path = self.base_path / session_path / file_name
        
        # Validate path is within base_path
        try:
            full_path.resolve().relative_to(self.base_path.resolve())
        except ValueError:
            raise ValueError(f"File path {full_path} is outside base storage directory")
        
        return full_path
    
    def save_file(
        self,
        file_content: BinaryIO,
        file_path: str,
        file_name: str
    ) -> bool:
        """
        Save file to local storage
        
        Args:
            file_content: File object or bytes to save
            file_path: Directory path where file should be saved
            file_name: Name of the file to save
            
        Returns:
            bool: True if successful
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            if hasattr(file_content, 'read'):
                with open(full_path, 'wb') as f:
                    f.write(file_content.read())
            else:
                with open(full_path, 'wb') as f:
                    f.write(file_content)
            
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def delete_file(self, file_path: str, file_name: str) -> bool:
        """
        Delete file from local storage
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file to delete
            
        Returns:
            bool: True if successful
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file(self, file_path: str, file_name: str) -> Optional[bytes]:
        """
        Get file content from local storage
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file to retrieve
            
        Returns:
            bytes: File content, or None if not found
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def list_files(self, file_path: str) -> list:
        """
        List all files in a directory
        
        Args:
            file_path: Directory path to list
            
        Returns:
            list: List of file names in the directory
        """
        try:
            full_path = self._get_full_path(file_path, "")
            
            if full_path.exists() and full_path.is_dir():
                return [f.name for f in full_path.iterdir() if f.is_file()]
            return []
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def file_exists(self, file_path: str, file_name: str) -> bool:
        """
        Check if file exists in local storage
        
        Args:
            file_path: Directory path where file should be
            file_name: Name of the file
            
        Returns:
            bool: True if file exists
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            return full_path.exists() and full_path.is_file()
        except Exception:
            return False
    
    def get_file_size(self, file_path: str, file_name: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file
            
        Returns:
            int: File size in bytes, or None if not found
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            
            if full_path.exists():
                return full_path.stat().st_size
            return None
        except Exception as e:
            print(f"Error getting file size: {e}")
            return None
    
    def get_file_hash(
        self,
        file_path: str,
        file_name: str,
        algorithm: str = 'sha256'
    ) -> Optional[str]:
        """
        Calculate hash of file
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file
            algorithm: Hash algorithm to use (default: sha256)
            
        Returns:
            str: Hash value, or None if not found
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            
            if not full_path.exists():
                return None
            
            hash_obj = hashlib.new(algorithm)
            with open(full_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return None
    
    def cleanup_empty_directories(self, file_path: str = None) -> int:
        """
        Remove empty directories
        
        Args:
            file_path: Specific directory to clean, or all if None
            
        Returns:
            int: Number of directories removed
        """
        try:
            target_path = self.base_path / file_path if file_path else self.base_path
            removed = 0
            
            # Walk directories from deepest to shallowest
            for dirpath, dirnames, filenames in os.walk(target_path, topdown=False):
                if dirpath == str(self.base_path):
                    continue
                
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    removed += 1
            
            return removed
        except Exception as e:
            print(f"Error cleaning directories: {e}")
            return 0
