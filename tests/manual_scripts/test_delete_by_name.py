import requests

base = 'http://localhost:8000'

# List projects  
r = requests.get(f'{base}/api/projects')
projects = r.json().get('projects', [])
print(f"Total projects: {len(projects)}")
for p in projects[:5]:
    print(f"  - {p['id']}: {p['name']}")

# Delete by name
print("\n=== DELETE by name (Project 69) ===")
r = requests.delete(f'{base}/api/projects?name=Project 69')
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

# Verify
print("\n=== Verify ===")
r = requests.get(f'{base}/api/projects')
projects = r.json().get('projects', [])
print(f"Remaining projects: {len(projects)}")
project_69 = next((p for p in projects if p['name'] == 'Project 69'), None)
if project_69:
    print(f"ERROR: Project 69 still exists!")
else:
    print(f"SUCCESS: Project 69 was deleted!")
