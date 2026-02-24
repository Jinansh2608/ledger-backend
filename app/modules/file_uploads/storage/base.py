"""
Abstract storage interface for file uploads
"""

from abc import ABC, abstractmethod
from typing import Optional, BinaryIO, Dict, Any
from pathlib import Path


class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    def save_file(
        self,
        file_content: BinaryIO,
        file_path: str,
        file_name: str
    ) -> bool:
        """
        Save file to storage
        
        Args:
            file_content: File object or bytes to save
            file_path: Directory path where file should be saved
            file_name: Name of the file to save
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str, file_name: str) -> bool:
        """
        Delete file from storage
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file to delete
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def get_file(self, file_path: str, file_name: str) -> Optional[bytes]:
        """
        Get file content from storage
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file to retrieve
            
        Returns:
            bytes: File content, or None if not found
        """
        pass
    
    @abstractmethod
    def list_files(self, file_path: str) -> list:
        """
        List all files in a directory
        
        Args:
            file_path: Directory path to list
            
        Returns:
            list: List of file names in the directory
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str, file_name: str) -> bool:
        """
        Check if file exists in storage
        
        Args:
            file_path: Directory path where file should be
            file_name: Name of the file
            
        Returns:
            bool: True if file exists
        """
        pass
    
    @abstractmethod
    def get_file_size(self, file_path: str, file_name: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file
            
        Returns:
            int: File size in bytes, or None if not found
        """
        pass
    
    @abstractmethod
    def get_file_hash(self, file_path: str, file_name: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate hash of file
        
        Args:
            file_path: Directory path where file is stored
            file_name: Name of the file
            algorithm: Hash algorithm to use (default: sha256)
            
        Returns:
            str: Hash value, or None if not found
        """
        pass
