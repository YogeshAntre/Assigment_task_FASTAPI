from test_app.models.role import RoleEnum
from fastapi import FastAPI, Depends, HTTPException
import bcrypt
from test_app.services.auth import AuthService
# class RoleChecker:
#     @staticmethod
#     def check_role_permission(user_role: RoleEnum) -> bool:
#         required_role: RoleEnum
#         role_hierarchy = {
#             RoleEnum.ADMIN: 3,
#             RoleEnum.MANAGER: 2,
#             RoleEnum.USER: 1
#         }
#         return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

def role_required(required_role: RoleEnum):
    def checker(user_role: RoleEnum):
        if not AuthService.check_role_permission(user_role, required_role):
            raise HTTPException(status_code=403, detail="Access Denied")
        return user_role
    return checker


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

