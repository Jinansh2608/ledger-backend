import requests
import json

print("Testing GET projects...")
r = requests.get('http://localhost:8000/api/projects')
print(f"Status: {r.status_code}")
data = r.json()
print(f"Projects: {len(data.get('projects', []))} found\n")

# Try to delete Project 70 (id=14)
print("Testing DELETE Project 70...")
r = requests.delete('http://localhost:8000/api/projects?name=Project 70')
print(f"Status: {r.status_code}")
print(f"Response: {r.text}\n")

# Verify deletion
print("Verifying deletion...")
r = requests.get('http://localhost:8000/api/projects')
data = r.json()
projects = data.get('projects', [])
found = any(p['name'] == 'Project 70' for p in projects)
print(f"Project 70 still exists: {found}")
print(f"Total projects now: {len(projects)}")
