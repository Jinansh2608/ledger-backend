import requests
import json

base = 'http://localhost:8000'

# List projects
print("=== GET all projects ===")
r = requests.get(f'{base}/api/projects')
print(f"Status: {r.status_code}")
data = r.json()
projects = data.get('projects', [])
print(f"Total: {len(projects)}")
for p in projects[:3]:
    print(f"  - ID {p['id']}: {p['name']}")

# Try DELETE by ID
print("\n=== DELETE by ID (14) ===")
r = requests.delete(f'{base}/api/projects/14')
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

# Check if it still exists
print("\n=== Verify ===")
r = requests.get(f'{base}/api/projects')
projects = r.json().get('projects', [])
project_70 = next((p for p in projects if p['id'] == 14), None)
if project_70:
    print(f"Project 70 still exists: {project_70['name']}")
else:
    print("Project 70 was deleted!")
    print(f"Remaining projects: {len(projects)}")
