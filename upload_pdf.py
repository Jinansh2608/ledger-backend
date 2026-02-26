#!/usr/bin/env python3
"""
PDF Upload and Parse Script
Uploads a PDF file to /api/po/upload endpoint for Bajaj PO parsing
"""

import requests
import sys
import os
from pathlib import Path

def upload_pdf(pdf_path, base_url="http://localhost:8000", client_id=1, project_name=None):
    """
    Upload a PDF file to the /api/po/upload endpoint
    
    Args:
        pdf_path: Path to the PDF file to upload
        base_url: Base URL of the API (default: http://localhost:8000)
        client_id: Client ID (1=Bajaj, 2=Dava India)
        project_name: Optional project name to link the PO
    
    Returns:
        Response JSON from the API
    """
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        return None
    
    # Get file size
    file_size = os.path.getsize(pdf_path)
    print(f"📄 PDF File: {os.path.basename(pdf_path)}")
    print(f"📊 File Size: {file_size:,} bytes")
    print(f"🏢 Client ID: {client_id}")
    if project_name:
        print(f"📋 Project Name: {project_name}\n")
    else:
        print()
    
    url = f"{base_url}/api/po/upload"
    
    # Prepare query parameters
    params = {
        "client_id": client_id,
        "auto_save": True
    }
    
    if project_name:
        params["project_name"] = project_name
    
    try:
        print("🚀 Uploading PDF...")
        
        # Open and upload the file
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = requests.post(url, params=params, files=files, timeout=60)
        
        print(f"✅ Upload successful! Status: {response.status_code}\n")
        
        result = response.json()
        
        # Print results
        print("=" * 60)
        print("UPLOAD RESULTS")
        print("=" * 60)
        
        if result.get('status') == 'SUCCESS':
            print(f"✅ Status: {result['status']}")
            print(f"📁 File ID: {result['file_id']}")
            print(f"🔑 Session ID: {result['session_id']}")
            print(f"🏢 Client: {result['client_name']} (ID: {result['client_id']})")
            print(f"📝 Parser Type: {result['parser_type']}")
            
            # PO Details
            po_details = result.get('po_details', {})
            if po_details:
                print(f"\n📋 PO DETAILS:")
                print(f"   PO Number: {po_details.get('po_number')}")
                print(f"   PO Date: {po_details.get('po_date')}")
                print(f"   PO Value: {po_details.get('po_value')}")
            
            # Line Items
            line_items = result.get('line_items', [])
            print(f"\n📦 LINE ITEMS: {result['line_item_count']}")
            if line_items:
                for i, item in enumerate(line_items, 1):
                    print(f"\n   Item {i}:")
                    print(f"      Description: {item.get('description')}")
                    print(f"      Quantity: {item.get('quantity')}")
                    print(f"      Amount: {item.get('amount')}")
            
            # Database Info
            if result.get('client_po_id'):
                print(f"\n💾 Database ID: {result['client_po_id']}")
            
            print("\n" + "=" * 60)
            return result
        
        else:
            print(f"❌ Error: {result.get('message')}")
            if 'errors' in result:
                for error in result['errors']:
                    print(f"   - {error['field']}: {error['message']}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {base_url}")
        print("   Make sure the API server is running")
        return None
    
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timeout")
        return None
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    """Main function"""
    
    # Example usage - modify these as needed
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        client_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        project_name = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        # Default example
        print("Usage: python upload_pdf.py <pdf_path> [client_id] [project_name]")
        print("\nExample:")
        print("  python upload_pdf.py path/to/bajaj_po.pdf 1 'Project A'")
        print("\nClients:")
        print("  1 = Bajaj (PO)")
        print("  2 = Dava India (Proforma Invoice)")
        print("\n" + "=" * 60)
        
        # Try to find a sample PDF
        print("\n🔍 Looking for PDF files in current directory...")
        pdfs = list(Path(".").glob("*.pdf"))
        
        if pdfs:
            print(f"\n Found {len(pdfs)} PDF(s):")
            for pdf in pdfs:
                print(f"  - {pdf}")
            
            # Use first PDF found
            pdf_path = str(pdfs[0])
            print(f"\n📤 Uploading: {pdf_path}")
            upload_pdf(pdf_path)
        else:
            print("\n❌ No PDF files found in current directory")
            print("\nTo upload a PDF, run:")
            print("  python upload_pdf.py <path_to_pdf_file>")
        return
    
    upload_pdf(pdf_path, client_id=client_id, project_name=project_name)


if __name__ == "__main__":
    main()
