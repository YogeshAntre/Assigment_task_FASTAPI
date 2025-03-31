

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from test_app.database import Base
from enum import Enum
# class RoleEnum(enum.Enum):
#     ADMIN = "admin"
#     MANAGER = "manager"
#     USER = "user"




class RoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    
    # Relationship to User
    users = relationship("User", back_populates="role")