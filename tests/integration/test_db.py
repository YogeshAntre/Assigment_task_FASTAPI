import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from test_app.database import Base
import pytest
from main import app
from fastapi.testclient import TestClient
import pytest_asyncio
from httpx import AsyncClient
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac


DATABASE_URL = "postgresql+asyncpg://postgres:yogesh@localhost:5432/UserTable"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class TestAuth:
    @pytest.mark.asyncio
    async def test_register_user_success(self, client):
        """Test successful user registration"""
        response = await client.post(
            "/auth/register",
            json={
                "username": "testuser101",
                "email": "test101@example.com",
                "password": "Test21237896!",
                "role": "user"
            }
        )
        print('yogesh',response.json())
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["username"] == "testuser101"
        assert data["email"] == "test101@example.com"
        assert "password" not in data
        assert data["role"] == "user"


 

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        # Test login with query parameters
        login_response = await client.post(
            "/auth/login",
            params={  # Changed from data to params
                "username": "testuser10123",
                "password": "Test21237896!"
            }
        )
        
        print('Login response:', login_response.json())
        assert login_response.status_code == status.HTTP_200_OK
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_invalid_password(self, client):
        """Test registration with an invalid password"""
        response = await client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "short",  # too short
                "role": "user"
            }
        )
        print('----',response.json())
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = response.json()["detail"]
        assert any("password" in error["msg"].lower() for error in detail)

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = await client.post(
            "/auth/login",
            params={
                "username": "admin_user",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect username or password" in response.json()["detail"].lower()


