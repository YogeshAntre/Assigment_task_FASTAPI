import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime
from test_app.models.user import User
from test_app.models.role import RoleEnum
from pydantic import ValidationError



@pytest.fixture
def sample_role():
    """Fixture providing a sample role"""
    return RoleEnum.ADMIN

@pytest.fixture
def sample_user(sample_role):
    """Fixture providing a sample user with a role"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed123"  # Use hashed_password instead of password
    )
    user.roles = [sample_role]  # Set roles after creation
    return user

def test_user_creation(sample_user):
    """Test basic user creation"""
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"
    assert sample_user.hashed_password == "hashed123"
    assert len(sample_user.roles) == 1
    assert sample_user.roles[0] == RoleEnum.ADMIN



def test_user_role_assignment(sample_user, sample_role):
    """Test role assignment functionality"""
    assert sample_role in sample_user.roles
    # If you have a method to check roles:
    if hasattr(sample_user, 'has_role'):
        assert sample_user.has_role(sample_role.name)


def test_user_email_validation():
    """Test email validation through Pydantic schema"""
    from test_app.schemas.user import UserCreate  # Import your Pydantic schema
    
    # Valid email
    user_data = {
        "username": "valid",
        "email": "valid@example.com",
        "password": "Valid123!"
    }
    user = UserCreate(**user_data)
    assert user.email == "valid@example.com"
    
    # Invalid email
    with pytest.raises(ValidationError):
        UserCreate(
            username="invalid",
            email="not-an-email",
            password="Valid123!"
        )