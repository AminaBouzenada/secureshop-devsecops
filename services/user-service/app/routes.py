from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import UserCreate, UserLogin, Token, UserResponse
from auth import create_access_token, verify_password, hash_password, verify_token
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

# In-memory user database (replace with real database in production)
users_db = {}
user_id_counter = 1

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user"""
    global user_id_counter
    
    # Check if username exists
    if any(u["username"] == user.username for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_data = {
        "id": user_id_counter,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hash_password(user.password),
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users_db[user_id_counter] = user_data
    user_id_counter += 1
    
    # Create token
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user and return JWT token"""
    # Find user
    user = None
    for u in users_db.values():
        if u["username"] == credentials.username:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user["username"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile"""
    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")
    
    # Find user
    user = None
    for u in users_db.values():
        if u["username"] == username:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )

@router.get("/users", response_model=list[UserResponse])
async def list_users():
    """List all users (for testing)"""
    return [
        UserResponse(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            full_name=u["full_name"],
            created_at=u["created_at"],
            is_active=u["is_active"]
        )
        for u in users_db.values()
    ]
