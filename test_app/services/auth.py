# from datetime import datetime, timedelta
# import jwt
# from test_app.config import settings
# from test_app.models.user import User
# from test_app.models.role import RoleEnum
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

# class AuthService:
#     @staticmethod
#     def create_access_token(data: dict, expires_delta: timedelta = None):
#         to_encode = data.copy()
#         if expires_delta:
#             expire = datetime.utcnow() + expires_delta
#         else:
#             expire = datetime.utcnow() + timedelta(minutes=15)
        
#         to_encode.update({"exp": expire})
#         return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
#     @staticmethod
#     async def authenticate_user(
#         session: AsyncSession, 
#         username: str, 
#         password: str
#     ) -> User | None:
#         stmt = select(User).where(User.username == username)
#         result = await session.execute(stmt)
#         user = result.scalar_one_or_none()
        
#         if not user or not user.verify_password(password):
#             return None
#         return user
    
#     @staticmethod
#     def check_role_permission(user_role: RoleEnum, required_role: RoleEnum) -> bool:
#         role_hierarchy = {
#             RoleEnum.ADMIN: 3,
#             RoleEnum.MANAGER: 2,
#             RoleEnum.USER: 1
#         }
#         return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
from datetime import datetime, timedelta
from typing import Optional
import jwt
from jose import JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from test_app.config import settings
from test_app.models.user import User
from test_app.models.role import RoleEnum

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def create_access_token(
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates a JWT access token with expiration.
        
        Args:
            data: Dictionary containing token claims
            expires_delta: Optional timedelta for token expiration
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    async def authenticate_user(
        session: AsyncSession, 
        username: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticates a user by username and password.
        
        Args:
            session: Async database session
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User object if authenticated, None otherwise
        """
        # Eager load the role relationship to avoid async issues
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.role))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generates a password hash."""
        return pwd_context.hash(password)

    @staticmethod
    def check_role_permission(user_role: RoleEnum, required_role: RoleEnum) -> bool:
        """
        Checks if user role has sufficient permissions.
        
        Args:
            user_role: The user's role
            required_role: The minimum required role
            
        Returns:
            True if user has sufficient permissions, False otherwise
        """
        role_hierarchy = {
            RoleEnum.ADMIN: 3,
            RoleEnum.MANAGER: 2,
            RoleEnum.USER: 1
        }
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

    @staticmethod
    async def get_current_user(
        token: str, 
        session: AsyncSession
    ) -> User:
        """
        Validates JWT token and returns the current user.
        
        Args:
            token: JWT token string
            session: Async database session
            
        Returns:
            Authenticated user
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
            
        user = await AuthService.authenticate_user(session, username, "")
        if user is None:
            raise credentials_exception
        return user