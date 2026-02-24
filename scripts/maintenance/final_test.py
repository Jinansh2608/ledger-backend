import requests
import json

# Test DELETE by name - updated to use both name options 
print("=== List projects ===")
r = requests.get('http://localhost:8000/api/projects')
projects = r.json()['projects']
print(f"Total: {len(projects)}")
print(f"First 5: {[p['name'] for p in projects[:5]]}")

# Find Project 01482 which was mentioned in the original error
print("\n=== DELETE by name (Project 01482) ===")
r = requests.delete('http://localhost:8000/api/projects?name=Project 01482')
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

# Verify
print("\n=== Verify ===")
r = requests.get('http://localhost:8000/api/projects')
projects = r.json()['projects']
remaining = [p['name'] for p in projects]
if 'Project 01482' in remaining:
    print("FAILED: Project 01482 still exists")
else:
    print(f"SUCCESS: Project 01482 was deleted!")
    print(f"Remaining: {len(projects)} projects")
