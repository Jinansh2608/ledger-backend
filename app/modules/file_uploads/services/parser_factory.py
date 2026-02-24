"""
Parser Factory - Selects appropriate parser based on client
"""

from app.utils.bajaj_po_parser import parse_bajaj_po, BajajPOParserError
from app.utils.proforma_invoice_parser import parse_proforma_invoice, ProformaInvoiceParserError


class ParserFactory:
    """Factory for selecting the right parser based on client"""
    
    # Client ID to client name mapping
    CLIENT_CONFIGS = {
        1: {
            "name": "Bajaj",
            "parser_type": "po",
            "parser_function": parse_bajaj_po,
            "error_class": BajajPOParserError
        },
        2: {
            "name": "Dava India",
            "parser_type": "proforma_invoice",
            "parser_function": parse_proforma_invoice,
            "error_class": ProformaInvoiceParserError
        }
    }
    
    @staticmethod
    def get_parser_for_client(client_id: int):
        """
        Get parser function for a specific client
        
        Args:
            client_id: ID of the client
            
        Returns:
            dict with parser config
            
        Raises:
            ValueError: If client_id not found
        """
        if client_id not in ParserFactory.CLIENT_CONFIGS:
            raise ValueError(f"No parser configured for client_id {client_id}")
        
        return ParserFactory.CLIENT_CONFIGS[client_id]
    
    @staticmethod
    def parse_file(file_path: str, client_id: int) -> dict:
        """
        Parse a file using the appropriate parser for the client
        
        Args:
            file_path: Path to the file to parse
            client_id: ID of the client
            
        Returns:
            Parsed data from the file
            
        Raises:
            ValueError: If client not found
            ParserError: If parsing fails
        """
        config = ParserFactory.get_parser_for_client(client_id)
        parser_function = config["parser_function"]
        
        try:
            parsed_data = parser_function(file_path)
            parsed_data["client_id"] = client_id
            parsed_data["client_name"] = config["name"]
            parsed_data["parser_type"] = config["parser_type"]
            return parsed_data
        except Exception as e:
            raise Exception(f"Parser error for {config['name']}: {str(e)}")
    
    @staticmethod
    def get_client_name(client_id: int) -> str:
        """Get client name from ID"""
        config = ParserFactory.get_parser_for_client(client_id)
        return config["name"]
    
    @staticmethod
    def get_all_clients():
        """Get all configured clients"""
        return {
            client_id: config["name"]
            for client_id, config in ParserFactory.CLIENT_CONFIGS.items()
        }
