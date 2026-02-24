import json
from pathlib import Path

files = [
    'PO_Management_API.postman_collection.json',
    'DavaIndia_PI_API_Tests.postman_collection.json'
]
root = Path(__file__).resolve().parents[1]
for fn in files:
    p = root / fn
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        print('OK', fn, '->', data.get('info', {}).get('name'))
    except Exception as e:
        print('ERROR', fn, e)
