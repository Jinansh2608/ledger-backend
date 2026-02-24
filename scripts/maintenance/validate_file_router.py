#!/usr/bin/env python3
"""
File Upload Router Validation Test
Verifies that the client-based parser routing is working correctly
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api"
CREDENTIALS = ("admin", "password")  # Default credentials

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def test_backend_health():
    """Test if backend is running"""
    print_header("Test 1: Backend Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"Backend is running on {BASE_URL}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_info("Make sure backend is running: python run.py")
        return False

def test_get_supported_clients():
    """Test GET /api/clients endpoint"""
    print_header("Test 2: Get Supported Clients")
    
    try:
        response = requests.get(
            f"{BASE_URL}/clients",
            auth=CREDENTIALS
        )
        
        if response.status_code != 200:
            print_error(f"Failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
        
        data = response.json()
        
        if data.get("status") != "SUCCESS":
            print_error("Response status is not SUCCESS")
            return False
        
        clients = data.get("data", {}).get("clients", [])
        
        if len(clients) < 2:
            print_error("Expected at least 2 clients")
            return False
        
        print_success("Successfully retrieved supported clients:")
        for client in clients:
            print_info(f"  • {client['name']} (ID: {client['id']})")
        
        # Verify expected clients
        client_ids = {c['id'] for c in clients}
        if 1 not in client_ids or 2 not in client_ids:
            print_error("Missing expected clients (Bajaj ID=1, Dava India ID=2)")
            return False
        
        print_success("All expected clients are configured")
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_parser_factory():
    """Test that ParserFactory can be loaded and has correct config"""
    print_header("Test 3: Parser Factory Configuration")
    
    try:
        from app.modules.file_uploads.services.parser_factory import ParserFactory
        
        # Check CLIENT_CONFIGS
        configs = ParserFactory.CLIENT_CONFIGS
        
        if 1 not in configs:
            print_error("Bajaj (Client ID 1) not configured in ParserFactory")
            return False
        
        if 2 not in configs:
            print_error("Dava India (Client ID 2) not configured in ParserFactory")
            return False
        
        # Verify Bajaj config
        bajaj_config = configs[1]
        if bajaj_config['name'] != 'Bajaj':
            print_error(f"Bajaj name mismatch: {bajaj_config['name']}")
            return False
        if bajaj_config['parser_type'] != 'po':
            print_error(f"Bajaj parser_type mismatch: {bajaj_config['parser_type']}")
            return False
        
        print_success("Bajaj Configuration (ID=1):")
        print_info(f"  Name: {bajaj_config['name']}")
        print_info(f"  Parser Type: {bajaj_config['parser_type']}")
        print_info(f"  Parser Function: parse_bajaj_po")
        
        # Verify Dava India config
        dava_config = configs[2]
        if dava_config['name'] != 'Dava India':
            print_error(f"Dava India name mismatch: {dava_config['name']}")
            return False
        if dava_config['parser_type'] != 'proforma_invoice':
            print_error(f"Dava India parser_type mismatch: {dava_config['parser_type']}")
            return False
        
        print_success("Dava India Configuration (ID=2):")
        print_info(f"  Name: {dava_config['name']}")
        print_info(f"  Parser Type: {dava_config['parser_type']}")
        print_info(f"  Parser Function: parse_proforma_invoice")
        
        return True
        
    except ImportError as e:
        print_error(f"Could not import ParserFactory: {str(e)}")
        print_info("Make sure you're running this from the Backend directory")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_parsers_exist():
    """Test that parser functions exist and are callable"""
    print_header("Test 4: Parser Functions Exist")
    
    try:
        from app.utils.bajaj_po_parser import parse_bajaj_po, BajajPOParserError
        from app.utils.proforma_invoice_parser import parse_proforma_invoice, ProformaInvoiceParserError
        
        print_success("parse_bajaj_po function imported successfully")
        print_info(f"  Callable: {callable(parse_bajaj_po)}")
        print_info(f"  Error class: BajajPOParserError")
        
        print_success("parse_proforma_invoice function imported successfully")
        print_info(f"  Callable: {callable(parse_proforma_invoice)}")
        print_info(f"  Error class: ProformaInvoiceParserError")
        
        return True
        
    except ImportError as e:
        print_error(f"Could not import parsers: {str(e)}")
        return False

def test_upload_endpoint_exists():
    """Test that upload endpoint exists"""
    print_header("Test 5: Upload Endpoint Configuration")
    
    try:
        from app.modules.file_uploads.controllers.routes import router
        
        # Check if router has the upload route
        routes = [route.path for route in router.routes]
        
        if "/po/upload" not in routes:
            print_error("POST /po/upload route not found in router")
            return False
        
        print_success("POST /uploads/po/upload endpoint is configured")
        print_info("  Required parameters: client_id (1 or 2)")
        print_info("  Optional parameters: project_id, auto_save")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_file_routing_logic():
    """Test the file routing logic without files"""
    print_header("Test 6: File Routing Logic")
    
    try:
        from app.modules.file_uploads.services.parser_factory import ParserFactory
        
        # Test Bajaj routing
        try:
            parser_config = ParserFactory.get_parser_for_client(1)
            if parser_config['name'] == 'Bajaj':
                print_success("Routing for client_id=1 returns Bajaj configuration")
            else:
                print_error(f"Routing for client_id=1 returns unexpected config: {parser_config['name']}")
                return False
        except Exception as e:
            print_error(f"Error routing client_id=1: {str(e)}")
            return False
        
        # Test Dava India routing
        try:
            parser_config = ParserFactory.get_parser_for_client(2)
            if parser_config['name'] == 'Dava India':
                print_success("Routing for client_id=2 returns Dava India configuration")
            else:
                print_error(f"Routing for client_id=2 returns unexpected config: {parser_config['name']}")
                return False
        except Exception as e:
            print_error(f"Error routing client_id=2: {str(e)}")
            return False
        
        # Test invalid client_id
        try:
            parser_config = ParserFactory.get_parser_for_client(999)
            print_error("Routing for client_id=999 should raise ValueError")
            return False
        except ValueError:
            print_success("Routing for invalid client_id correctly raises ValueError")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_manual_file_upload(test_file_path, client_id, project_id=1):
    """Test actual file upload if test file exists"""
    print_header(f"Test 7: Upload {['Bajaj', '', 'Dava India'][client_id]} File (client_id={client_id})")
    
    if not Path(test_file_path).exists():
        print_warning(f"Test file not found: {test_file_path}")
        print_info("Skipping actual file upload test")
        return None
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            params = {
                'client_id': client_id,
                'project_id': project_id,
                'auto_save': True
            }
            
            response = requests.post(
                f"{BASE_URL}/uploads/po/upload",
                files=files,
                params=params,
                auth=CREDENTIALS,
                timeout=30
            )
        
        if response.status_code != 200:
            print_error(f"Upload failed with status {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        if result.get('status') == 'SUCCESS':
            print_success("File uploaded and parsed successfully")
            print_info(f"  File ID: {result.get('file_id')}")
            print_info(f"  Client PO ID: {result.get('client_po_id')}")
            print_info(f"  PO Details: {json.dumps(result.get('po_details', {}), indent=2)}")
            print_info(f"  Line Items: {result.get('line_item_count')} items")
            return True
        else:
            print_warning(f"Upload succeeded but parsing had issues: {result.get('status')}")
            print_info(f"  Error: {result.get('po_details', {}).get('error')}")
            return False
        
    except requests.exceptions.Timeout:
        print_error("Upload request timed out (30s)")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Nexgen Finance - File Upload Router Validation{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    results = {}
    
    # Test 1: Backend health
    results['Backend Health'] = test_backend_health()
    if not results['Backend Health']:
        print_error("Backend is not running. Tests cannot continue.")
        sys.exit(1)
    
    # Test 2: Get supported clients
    results['Get Supported Clients'] = test_get_supported_clients()
    
    # Test 3: Parser Factory
    results['Parser Factory Config'] = test_parser_factory()
    
    # Test 4: Parsers
    results['Parser Functions'] = test_parsers_exist()
    
    # Test 5: Upload endpoint
    results['Upload Endpoint'] = test_upload_endpoint_exists()
    
    # Test 6: Routing logic
    results['File Routing Logic'] = test_file_routing_logic()
    
    # Test 7: Actual file upload (optional)
    # results['File Upload'] = test_manual_file_upload('test_files/bajaj_po.xlsx', 1)
    
    # Print summary
    print_header("Summary")
    
    passed = sum(1 for v in results.values() if v is True)
    total = len([v for v in results.values() if v is not None])
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: PASSED")
        elif result is False:
            print_error(f"{test_name}: FAILED")
        else:
            print_warning(f"{test_name}: SKIPPED")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("All tests passed! File router is working correctly.")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
