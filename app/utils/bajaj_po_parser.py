import pdfplumber
import re
from datetime import datetime


# =========================================================
# ERRORS
# =========================================================

class BajajPOParserError(Exception):
    pass


# =========================================================
# SAFE HELPERS
# =========================================================

def clean(text):
    if not text:
        return ""
    return " ".join(str(text).replace("\xa0", " ").strip().split())


def to_float(val):
    try:
        return float(re.sub(r"[^\d\.]", "", str(val)))
    except:
        return None


def safe_date(text):
    try:
        return datetime.strptime(text, "%d %b %Y").date().isoformat()
    except:
        return None


# =========================================================
# DESCRIPTION CLEANER
# =========================================================

JUNK_PREFIXES = (
    "STATUS", "TAX", "OTHER INFORMATION", "REQ. LINE",
    "PR NO", "STORAGE LOCATION", "CLASSIFICATION",
    "INCOTERM", "ORDER SUBMITTED", "PDF GENERATED",
    "THIS PURCHASE ORDER"
)

def trim_description(block_lines):

    meaningful = []

    for line in block_lines:

        if not line:
            continue

        upper = line.upper()

        if upper.startswith(JUNK_PREFIXES):
            continue

        if "INR" in upper and re.search(r"\d{1,3}(?:,\d{3})*\.\d{2}", line):
            continue

        if upper.startswith("MAHARASHTRA MUMBAI"):
            continue

        if re.fullmatch(r"\d{8,}", line.strip()):
            continue

        meaningful.append(line)

    text = " ".join(meaningful)

    text = re.sub(r"VENDOR\s*:.*?PLUS”", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Unconfirmed.*?Location on Detail", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()

    return text if text else "UNKNOWN ITEM"


# =========================================================
# CORE PARSER
# =========================================================

def parse_bajaj_pdf_po(pdf_path):

    result = {
        "status": "SUCCESS",
        "po_details": {
            "po_number": None,
            "po_date": None,
            "store_id": None,
            "site_address": None,
            "po_value": None
        },
        "line_items": [],
        "line_item_count": 0,
        "warnings": []
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            lines = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                for l in text.splitlines():
                    lines.append(clean(l))
    except Exception as e:
        raise BajajPOParserError(f"PDF read failed: {str(e)}")

    if not lines:
        raise BajajPOParserError("PDF contains no readable text")

    currency_re = re.compile(r"(\d{1,3}(?:,\d{3})*\.\d{2})")

    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    for line in lines[:200]:

        if not result["po_details"]["po_number"]:
            m = re.search(r"Purchase Order[:\s]*([0-9]{6,12})", line, re.I)
            if m:
                result["po_details"]["po_number"] = m.group(1)

        if not result["po_details"]["po_date"]:
            m = re.search(r"\b(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\b", line)
            if m:
                result["po_details"]["po_date"] = safe_date(m.group(1))

        if result["po_details"]["po_value"] is None:
            m = re.search(r"Amount[:\s]*([\d,]+\.\d{2})", line)
            if m:
                result["po_details"]["po_value"] = to_float(m.group(1))

    # -----------------------------------------------------
    # LINE ITEMS (HEADER-ANCHOR METHOD)
    # -----------------------------------------------------

    header_indices = [
        i for i, l in enumerate(lines)
        if "Line # Part # / Description" in l
    ]

    if not header_indices:
        raise BajajPOParserError("Could not locate line item headers")

    header_indices.sort()

    row_index = 1
    seen = set()

    for idx in range(len(header_indices)):

        start = header_indices[idx] + 1
        end = header_indices[idx + 1] if idx + 1 < len(header_indices) else len(lines)

        block = lines[start:end]

        joined = " ".join(block)
        amounts = currency_re.findall(joined)

        if len(amounts) < 1:
            continue

        amount = to_float(amounts[1] if len(amounts) >= 2 else amounts[0])

        if amount is None:
            continue

        qty = 1
        for l in block:
            m = re.search(r"\b(\d+(?:\.\d+)?)\s*\(\s*[A-Za-z0-9]+\s*\)", l)
            if m:
                qty = float(m.group(1))
                break

        description = trim_description(block)

        key = (description.lower(), qty, amount)

        if key in seen:
            continue

        seen.add(key)

        result["line_items"].append({
            "description": description,
            "quantity": qty,
            "amount": round(amount, 2),
            "row_index": row_index
        })

        row_index += 1

    if not result["line_items"]:
        raise BajajPOParserError("No valid line items extracted")

    result["line_item_count"] = len(result["line_items"])

    if result["po_details"]["po_value"] is None:
        total = sum(i["amount"] for i in result["line_items"])
        result["po_details"]["po_value"] = round(total, 2)

    return result


# =========================================================
# FASTAPI SAFE WRAPPER
# =========================================================

def parse_bajaj_po(pdf_path, request_path="/api/po/upload"):

    try:
        return parse_bajaj_pdf_po(pdf_path)

    except BajajPOParserError as e:
        return {
            "status": "ERROR",
            "error_code": "PARSER_ERROR",
            "message": f"Parsing failed: Parser error for Bajaj: {str(e)}",
            "path": request_path
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "error_code": "HTTP_ERROR",
            "message": f"Parsing failed: Parser error for Bajaj: Unexpected error: {str(e)}",
            "path": request_path
        }