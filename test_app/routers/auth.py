from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from test_app.database import get_db
from test_app.services.auth import AuthService
from test_app.schemas.user import UserCreate, UserResponse
from test_app.models.user import User
from test_app.models.role import Role, RoleEnum
from sqlalchemy import select
from test_app.services.user import role_required
router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate, 
    session: AsyncSession = Depends(get_db)
):

    existing_user = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered"
        )


    existing_email = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )


    hashed_password = AuthService.get_password_hash(user_data.password)
    

    role = await session.execute(
        select(Role).where(Role.name == user_data.role.value)
    )
    role = role.scalar_one_or_none()
    
    if not role:
        role = Role(name=user_data.role.value)
        session.add(role)
        await session.flush()

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role_id=role.id
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role.name
    )


@router.post("/login")
async def login(
    username: str, 
    password: str, 
    session: AsyncSession = Depends(get_db)
):
    user = await AuthService.authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    print(user)
    # Create access token
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "role": user.role.name}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/admin")
def admin_route(user_role: RoleEnum = Depends(role_required(RoleEnum.ADMIN))):
    return {"message": "Welcome, Admin"}



