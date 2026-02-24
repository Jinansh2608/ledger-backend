"""
Authentication and authorization utilities
Ready for JWT-based authentication implementation
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

import bcrypt

# Password hashing configuration (using raw bcrypt instead of passlib to avoid compatibility bugs)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

class AuthenticationError(Exception):
    """Authentication error"""
    pass

def hash_password(password: str) -> str:
    """Hash a password using bcrypt
    
    Note: bcrypt has a 72-byte limit on passwords. Longer passwords are truncated.
    """
    # Truncate password to 72 bytes (bcrypt limit)
    # Encode to UTF-8 first to get byte length
    password_bytes = password.encode('utf-8')[:72]
    password = password_bytes.decode('utf-8', errors='ignore')
    
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash
    
    Note: Passwords are truncated to 72 bytes to match bcrypt limits.
    """
    try:
        # Truncate password to 72 bytes (bcrypt limit) - same as hashing
        password_bytes = plain_password.encode('utf-8')[:72]
        plain_password = password_bytes.decode('utf-8', errors='ignore')
        
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_access_token(token: str) -> dict:
    """Verify and decode a JWT access token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token attempted: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_bearer_token(credentials = Depends(security)):
    """Extract bearer token from credentials"""
    return credentials.credentials

async def get_current_user(token: str = Depends(get_bearer_token)) -> dict:
    """
    Dependency for getting current authenticated user
    Usage: @router.get("/protected")
           def protected_endpoint(user = Depends(get_current_user)):
    """
    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {"user_id": user_id, **payload}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class User:
    """User model for authentication"""
    def __init__(self, user_id: str, username: str, email: str, roles: list = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.roles = roles or ["user"]
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.has_role("admin")

def require_role(required_role: str):
    """
    Dependency for role-based access control
    Usage: @router.get("/admin")
           def admin_endpoint(user = Depends(require_role("admin"))):
    """
    async def check_role(user: dict = Depends(get_current_user)) -> dict:
        user_roles = user.get("roles", [])
        
        if required_role not in user_roles:
            logger.warning(f"Unauthorized access attempt by user {user.get('user_id')} to role {required_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role"
            )
        
        return user
    
    return check_role

"""
EXAMPLE USAGE:

1. Login Endpoint:
   
   from fastapi import APIRouter
   from pydantic import BaseModel
   
   router = APIRouter()
   
   class LoginRequest(BaseModel):
       username: str
       password: str
   
   class LoginResponse(BaseModel):
       access_token: str
       token_type: str
   
   @router.post("/login", response_model=LoginResponse)
   async def login(request: LoginRequest):
       # Verify username and password
       user = verify_user_credentials(request.username, request.password)
       if not user:
           raise HTTPException(status_code=401, detail="Invalid credentials")
       
       # Create token
       access_token = create_access_token(
           data={"sub": user.user_id, "username": user.username, "roles": user.roles}
       )
       
       return {"access_token": access_token, "token_type": "bearer"}

2. Protected Endpoint:
   
   @router.get("/me")
   async def get_current_user_info(user = Depends(get_current_user)):
       return {"user_id": user.get("user_id"), "username": user.get("username")}

3. Role-Based Protected Endpoint:
   
   @router.delete("/users/{user_id}")
   async def delete_user(user_id: int, admin = Depends(require_role("admin"))):
       # Only admins can delete users
       return {"message": f"User {user_id} deleted"}

4. Client Usage:
   
   import requests
   
   # Login
   response = requests.post("http://localhost:8000/api/login", json={
       "username": "user",
       "password": "password"
   })
   token = response.json()["access_token"]
   
   # Use token
   headers = {"Authorization": f"Bearer {token}"}
   response = requests.get("http://localhost:8000/api/me", headers=headers)
"""
