"""
Authentication API endpoints - Login and Signup
Simple username/password authentication with JWT tokens
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from datetime import datetime
from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token, verify_access_token
from app.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

def get_bearer_token(credentials = Depends(security)):
    """Extract and return the bearer token"""
    return credentials.credentials

def get_user_by_username(username: str):
    """Get user from database by username"""
    try:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id, username, email, password_hash, created_at FROM "user" WHERE username = %s',
                    (username,)
                )
                result = cur.fetchone()
                return result
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise

def get_user_by_email(email: str):
    """Get user from database by email"""
    try:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id, username, email, password_hash, created_at FROM "user" WHERE email = %s',
                    (email,)
                )
                result = cur.fetchone()
                return result
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        raise

def create_user(username: str, email: str, password: str):
    """Create a new user in the database"""
    try:
        password_hash = hash_password(password)
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    '''INSERT INTO "user" (username, email, password_hash, created_at) 
                       VALUES (%s, %s, %s, %s) 
                       RETURNING id, username, email, created_at''',
                    (username, email, password_hash, datetime.utcnow())
                )
                result = cur.fetchone()
                conn.commit()
                return result
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        raise

async def get_current_user(token: str = Depends(get_bearer_token)):
    """Dependency for getting current authenticated user"""
    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {"user_id": int(user_id), "username": payload.get("username"), "email": payload.get("email")}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest):
    """
    Create a new user account and return JWT token
    
    Args:
        request: Signup request with username, email, and password
    
    Returns:
        TokenResponse with access token and user information
    """
    # Validate input
    if len(request.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    if not request.email or "@" not in request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address"
        )
    
    # Check if user already exists
    if get_user_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = create_user(request.username, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user['id']),
            "username": user['username'],
            "email": user['email']
        }
    )
    
    logger.info(f"New user registered: {user['username']}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            user_id=user['id'],
            username=user['username'],
            email=user['email'],
            created_at=user['created_at']
        )
    )

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Authenticate user with username and password, return JWT token
    
    Args:
        request: Login request with username and password
    
    Returns:
        TokenResponse with access token and user information
    """
    # Get user from database
    user = get_user_by_username(request.username)
    
    if not user:
        logger.warning(f"Login attempt with non-existent username: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(request.password, user['password_hash']):
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user['id']),
            "username": user['username'],
            "email": user['email']
        }
    )
    
    logger.info(f"User logged in: {user['username']}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            user_id=user['id'],
            username=user['username'],
            email=user['email'],
            created_at=user['created_at']
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info
    
    Requires: Authorization header with Bearer token
    
    Returns:
        UserResponse with user information
    """
    try:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id, username, email, created_at FROM "user" WHERE id = %s',
                    (user['user_id'],)
                )
                result = cur.fetchone()
                
                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                
                return UserResponse(
                    user_id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    created_at=result['created_at']
                )
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user information"
        )
