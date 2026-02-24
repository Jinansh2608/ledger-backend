# Authentication API Documentation

## Overview

The Authentication API provides simple username/password-based authentication with JWT tokens. It includes user signup, login, and protected endpoints functionality.

## Table of Contents

1. [Setup](#setup)
2. [API Endpoints](#api-endpoints)
3. [Usage Examples](#usage-examples)
4. [Error Handling](#error-handling)
5. [Token Management](#token-management)
6. [Protected Endpoints](#protected-endpoints)

## Setup

### Step 1: Initialize the Database

Run the setup script to create the user table:

```bash
python setup_auth.py
```

Or manually run the migration:

```bash
python -c "from migrations.'001_create_user_table' import create_user_table; create_user_table()"
```

This creates the `user` table in the database with the following schema:

```sql
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Step 2: Start the Application

```bash
python run.py
```

## API Endpoints

### 1. Signup - Create New User

**Endpoint:** `POST /api/auth/signup`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJqb2huX2RvZSIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImV4cCI6MTcwNDEwNDAwMH0.xxx...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**Validation Rules:**
- Username: minimum 3 characters, must be unique
- Email: must be valid and unique
- Password: minimum 6 characters

**Error Responses:**

**400 Bad Request:**
```json
{
  "detail": "Username already exists"
}
```

### 2. Login - Authenticate User

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJqb2huX2RvZSIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImV4cCI6MTcwNDEwNDAwMH0.xxx...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Invalid username or password"
}
```

### 3. Get Current User - Retrieve User Info

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Response (200 OK):**
```json
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Invalid token"
}
```

## Usage Examples

### Using cURL

#### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securePassword123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securePassword123"
  }'
```

#### Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_access_token>"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/auth"

# Signup
signup_response = requests.post(
    f"{BASE_URL}/signup",
    json={
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securePassword123"
    }
)
token = signup_response.json()["access_token"]

# Login
login_response = requests.post(
    f"{BASE_URL}/login",
    json={
        "username": "john_doe",
        "password": "securePassword123"
    }
)
token = login_response.json()["access_token"]

# Get Current User
headers = {"Authorization": f"Bearer {token}"}
user_response = requests.get(
    f"{BASE_URL}/me",
    headers=headers
)
print(user_response.json())
```

### Using JavaScript/Fetch API

```javascript
const BASE_URL = "http://localhost:8000/api/auth";

// Signup
const signupResponse = await fetch(`${BASE_URL}/signup`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    username: "john_doe",
    email: "john@example.com",
    password: "securePassword123"
  })
});
const { access_token } = await signupResponse.json();

// Login
const loginResponse = await fetch(`${BASE_URL}/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    username: "john_doe",
    password: "securePassword123"
  })
});
const { access_token } = await loginResponse.json();

// Get Current User
const userResponse = await fetch(`${BASE_URL}/me`, {
  headers: {
    "Authorization": `Bearer ${access_token}`
  }
});
const user = await userResponse.json();
console.log(user);
```

## Error Handling

The API returns standard HTTP status codes:

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 200 | Success | Login successful |
| 201 | Created | User account created |
| 400 | Bad Request | Invalid input, missing fields |
| 401 | Unauthorized | Invalid credentials, missing token |
| 500 | Server Error | Database error |

### Common Error Messages

**Signup Errors:**
- `"Username must be at least 3 characters long"`
- `"Password must be at least 6 characters long"`
- `"Invalid email address"`
- `"Username already exists"`
- `"Email already registered"`

**Login Errors:**
- `"Invalid username or password"`

**Token Errors:**
- `"Invalid token"`
- `"Missing authorization token"`

## Token Management

### JWT Token Structure

The JWT token contains the following claims:

```json
{
  "sub": "1",              // User ID
  "username": "john_doe",  // Username
  "email": "john@example.com",  // Email
  "exp": 1704104000,       // Expiration timestamp
  "iat": 1704102800        // Issued at timestamp
}
```

### Token Expiration

By default, tokens expire after 30 minutes. This can be configured via the `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable:

```bash
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Refreshing Tokens

To get a new token, simply login again:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securePassword123"}'
```

## Protected Endpoints

### Using the Auth Dependency

To protect your own endpoints with authentication, use the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(user = Depends(get_current_user)):
    return {"message": f"Hello {user['username']}"}
```

### Header Format

All protected endpoints require the `Authorization` header in the format:

```
Authorization: Bearer <jwt_token>
```

Example:
```bash
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Security Considerations

1. **Password Hashing**: Passwords are hashed using bcrypt with automatic salt generation
2. **JWT Tokens**: Tokens are signed with a secret key (configure `SECRET_KEY` environment variable)
3. **HTTPS**: Always use HTTPS in production
4. **Token Storage**: Store tokens securely (e.g., HttpOnly cookies, secure storage)
5. **CORS**: Configure CORS settings for your frontend domain
6. **Rate Limiting**: Consider implementing rate limiting on auth endpoints in production
7. **Audit Logging**: Login attempts are logged (see logs directory)

### Environment Variables

```bash
# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Nexgen_erp
DB_USER=postgres
DB_PASSWORD=your_password
DB_SCHEMA=Finances

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Troubleshooting

### "User table not found" Error

**Solution:** Run the setup script to create the user table:
```bash
python setup_auth.py
```

### "Database connection failed" Error

**Solution:** Verify database credentials in environment variables:
```bash
echo $DB_HOST $DB_PORT $DB_NAME $DB_USER
```

### "Invalid token" Error

**Solution:** 
1. Ensure token is not expired (tokens expire after 30 minutes by default)
2. Verify the `Authorization` header format: `Authorization: Bearer <token>`
3. Check if `SECRET_KEY` environment variable matches between signup and verification

### "CORS error" when calling from frontend

**Solution:** Check `CORS_ORIGINS` environment variable includes your frontend URL:
```bash
export CORS_ORIGINS=http://localhost:3000
```

## Next Steps

1. ✓ User signup/login API created
2. Next: Integrate with frontend (see [FRONTEND_AUTH_INTEGRATION.md](FRONTEND_AUTH_INTEGRATION.md))
3. Next: Add refresh tokens (see [ADVANCED_AUTH.md](ADVANCED_AUTH.md))
4. Next: Add role-based access control (see RBAC integration guide)

## Support

For issues or questions, check the [API_ROUTES_REFERENCE.md](API_ROUTES_REFERENCE.md) or create an issue in the project repository.
