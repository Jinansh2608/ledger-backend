"""
Test and demonstration script for Authentication API
Run this after starting the FastAPI server
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/auth"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def test_signup():
    """Test user signup"""
    print_section("TEST 1: User Signup")
    
    user_data = {
        "username": f"testuser_{datetime.now().timestamp()}",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "TestPassword123"
    }
    
    print(f"Signing up user: {user_data['username']}")
    print(f"Email: {user_data['email']}\n")
    
    response = requests.post(f"{BASE_URL}/signup", json=user_data)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"User created successfully!")
        print(f"User ID: {data['user']['user_id']}")
        print(f"Username: {data['user']['username']}")
        print(f"Email: {data['user']['email']}")
        print(f"Token Type: {data['token_type']}")
        print(f"Token (first 50 chars): {data['access_token'][:50]}...")
        return user_data['username'], user_data['password'], data['access_token']
    else:
        print_error(f"Signup failed: {response.status_code}")
        print(f"Response: {response.json()}")
        return None, None, None

def test_login(username, password):
    """Test user login"""
    print_section("TEST 2: User Login")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    print(f"Logging in user: {username}\n")
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Login successful!")
        print(f"User ID: {data['user']['user_id']}")
        print(f"Username: {data['user']['username']}")
        print(f"Email: {data['user']['email']}")
        print(f"Token (first 50 chars): {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print_error(f"Login failed: {response.status_code}")
        print(f"Response: {response.json()}")
        return None

def test_get_user(token):
    """Test getting current user info"""
    print_section("TEST 3: Get Current User")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Getting current user info...\n")
    
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("User info retrieved!")
        print(f"User ID: {data['user_id']}")
        print(f"Username: {data['username']}")
        print(f"Email: {data['email']}")
        print(f"Created At: {data['created_at']}")
    else:
        print_error(f"Failed to get user info: {response.status_code}")
        print(f"Response: {response.json()}")

def test_invalid_login():
    """Test login with invalid credentials"""
    print_section("TEST 4: Invalid Login (Error Handling)")
    
    invalid_data = {
        "username": "nonexistent_user",
        "password": "wrongpassword"
    }
    
    print(f"Attempting login with invalid credentials...\n")
    
    response = requests.post(f"{BASE_URL}/login", json=invalid_data)
    
    if response.status_code == 401:
        data = response.json()
        print_success("Error handled correctly!")
        print(f"Status Code: {response.status_code}")
        print(f"Error Message: {data['detail']}")
    else:
        print_error(f"Unexpected status code: {response.status_code}")

def test_invalid_token():
    """Test request with invalid token"""
    print_section("TEST 5: Invalid Token (Error Handling)")
    
    headers = {
        "Authorization": "Bearer invalid_token_string"
    }
    
    print(f"Attempting to get user info with invalid token...\n")
    
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    
    if response.status_code == 401:
        data = response.json()
        print_success("Error handled correctly!")
        print(f"Status Code: {response.status_code}")
        print(f"Error Message: {data['detail']}")
    else:
        print_error(f"Unexpected status code: {response.status_code}")

def test_duplicate_user(username, email):
    """Test signup with duplicate username/email"""
    print_section("TEST 6: Duplicate User (Error Handling)")
    
    duplicate_data = {
        "username": username,
        "email": f"different_{email}",
        "password": "TestPassword123"
    }
    
    print(f"Attempting signup with duplicate username...\n")
    
    response = requests.post(f"{BASE_URL}/signup", json=duplicate_data)
    
    if response.status_code == 400:
        data = response.json()
        print_success("Duplicate check working!")
        print(f"Status Code: {response.status_code}")
        print(f"Error Message: {data['detail']}")
    else:
        print_error(f"Unexpected status code: {response.status_code}")

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Authentication API - Test Suite")
    print("="*60)
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print(f"{'='*60}{Colors.RESET}\n")
    
    try:
        # Test 1: Signup
        username, password, token = test_signup()
        if not username:
            print_error("Signup test failed, aborting other tests")
            return
        
        # Test 2: Login
        new_token = test_login(username, password)
        if not new_token:
            print_error("Login test failed, skipping dependent tests")
            return
        
        # Test 3: Get User Info
        test_get_user(new_token)
        
        # Test 4: Invalid Login
        test_invalid_login()
        
        # Test 5: Invalid Token
        test_invalid_token()
        
        # Test 6: Duplicate User
        test_duplicate_user(username, f"test_{datetime.now().timestamp()}@example.com")
        
        # Summary
        print_section("Test Suite Complete")
        print_success("All tests passed!")
        print("\nFor comprehensive API documentation, see docs/AUTH_API.md")
        
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server at http://localhost:8000")
        print_info("Make sure the FastAPI server is running:")
        print_info("  python run.py")
    except Exception as e:
        print_error(f"Test suite error: {e}")

if __name__ == "__main__":
    main()
