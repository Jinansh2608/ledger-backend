import requests
response = requests.post(
    "http://localhost:8000/api/po/upload",
    params={"client_id": 1},
    files={"file": ("test.pdf", b"%PDF", "application/pdf")}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
