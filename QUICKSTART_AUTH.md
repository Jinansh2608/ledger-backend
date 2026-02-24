# Authentication API Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Initialize Database

```bash
python setup_auth.py
```

✓ This creates the `user` table with username, email, and password_hash columns

### 2. Start the Server

```bash
python run.py
```

✓ The API will be available at `http://localhost:8000`

### 3. Try the API

#### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

#### Get Current User (with token)
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_token_here>"
```

---

## 📚 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/auth/signup` | Register new user |
| `POST` | `/api/auth/login` | Login with credentials |
| `GET` | `/api/auth/me` | Get current user info |

---

## 🧪 Run Comprehensive Tests

```bash
python test_auth_api.py
```

This runs 6 tests covering:
- ✓ User signup
- ✓ User login  
- ✓ Get user info
- ✓ Invalid login handling
- ✓ Invalid token handling
- ✓ Duplicate user prevention

---

## 📖 Full Documentation

For detailed documentation, examples, and troubleshooting, see [docs/AUTH_API.md](docs/AUTH_API.md)

---

## 🔒 Using Auth in Your Endpoints

Protect your own endpoints with authentication:

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter()

@router.get("/api/protected")
async def protected_endpoint(user = Depends(get_current_user)):
    return {
        "message": f"Hello {user['username']}!",
        "user_id": user['user_id']
    }
```

Call it with token:
```bash
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer <your_token>"
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Token expiration (minutes)
export ACCESS_TOKEN_EXPIRE_MINUTES=30

# JWT signing key (CHANGE IN PRODUCTION!)
export SECRET_KEY=your-secret-key

# Database
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=Nexgen_erp
export DB_USER=postgres
export DB_PASSWORD=toor
export DB_SCHEMA=Finances
```

---

## 📝 Features

✅ **Secure Password Hashing** - Uses bcrypt with automatic salting
✅ **JWT Tokens** - Stateless authentication
✅ **Email Validation** - Ensures valid email addresses
✅ **Duplicate Prevention** - Username and email must be unique
✅ **Input Validation** - Enforces minimum lengths
✅ **Error Handling** - Clear error messages
✅ **Audit Logging** - All auth attempts are logged
✅ **CORS Support** - Works with frontend applications

---

## 🚦 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid credentials) |
| 500 | Server Error |

---

## 💡 Common Tasks

### Store Token in Frontend

```javascript
// After signup/login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);
```

### Use Token in Requests

```javascript
// When calling protected endpoints
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Clear Token on Logout

```javascript
localStorage.removeItem('token');
```

---

## 🐛 Troubleshooting

**Q: "User table not found" error?**
- A: Run `python setup_auth.py` first

**Q: "Invalid token" error?** 
- A: Token may be expired. Login again to get a new token.

**Q: CORS errors from frontend?**
- A: Check `CORS_ORIGINS` environment variable includes your frontend URL

**Q: "Connection refused" when starting server?**
- A: Make sure PostgreSQL is running and database credentials are correct

---

## 📞 Need Help?

- See [docs/AUTH_API.md](docs/AUTH_API.md) for full documentation
- Run `python test_auth_api.py` to verify everything works
- Check `logs/` directory for application logs
- Review [README_PRODUCTION.md](README_PRODUCTION.md) for production deployment

---

## ✨ Next Steps

1. ✅ Basic auth API created and tested
2. 📱 Next: Integrate with your frontend
3. 🔄 Optional: Add refresh tokens (advanced)
4. 👥 Optional: Add role-based access control
5. 🛡️ Optional: Add two-factor authentication

Happy authenticating! 🚀
