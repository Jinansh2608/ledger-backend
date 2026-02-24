import requests

# Test with ID first (this should work)
print("=== DELETE by ID ===")
r = requests.delete('http://localhost:8000/api/projects/6')  # Project 01482 has ID 6
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

# Verify
print("\n=== Verify ===")
r = requests.get('http://localhost:8000/api/projects')
projects = r.json()['projects']
found = any(p['name'] == 'Project 01482' for p in projects)
print(f"Project 01482 still exists: {found}")
print(f"Total projects: {len(projects)}")
