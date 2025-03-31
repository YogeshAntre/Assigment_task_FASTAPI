from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from test_app.database import get_db
from test_app.models.user import User
from test_app.models.role import RoleEnum
from test_app.services.auth import AuthService
from test_app.schemas.user import UserCreate, UserResponse
from test_app.services.user import hash_password
from test_app.models.role import Role
from test_app.services.user import role_required
from typing import List

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).filter(User.email == user.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    role = await session.execute(
        select(Role).where(Role.name == user.role.value)
    )
    role = role.scalar_one_or_none()
    
    if not role:
        role = Role(name=user.role.value)
        session.add(role)
        await session.flush()
    hashed_password = AuthService.get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
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


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(role_required(RoleEnum.MANAGER))])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    print('result',result)
    return result.scalars().all()




@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(role_required(RoleEnum.MANAGER))])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # return user
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.name
    )


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(role_required(RoleEnum.MANAGER))])
async def update_user(user_id: int, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    print('result',result)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = user_data.username
    user.email = user_data.email
    #user.hashed_password = hash_password(user_data.password)
    user.hashed_password = AuthService.get_password_hash(user_data.password)
    await db.commit()
    await db.refresh(user)
    await db.refresh(user)
    

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.name
    )




@router.delete("/{user_id}", dependencies=[Depends(role_required(RoleEnum.ADMIN))])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}

