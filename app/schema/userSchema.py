from pydantic import BaseModel
from datetime import datetime
from typing import Generic, TypeVar, Optional, List
from app.models.userModel import RoleEnum, GenderEnum
from app.schema.avatarSchema import AvatarWithAssetsRes

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None


class CreateUserReq(BaseModel):
    username: str
    emp_id: str
    role: RoleEnum
    gender: GenderEnum


class CreateUserRes(BaseModel):
    id: str
    username: str
    emp_id: str
    role: str
    gender: str
    is_first_login: bool
    created_at: datetime
    updated_at: datetime

class UpdateUserReq(BaseModel):
    username: Optional[str] = None
    emp_id: Optional[str] = None
    gender: Optional[GenderEnum] = None


class LoginReq(BaseModel):
    emp_id: str
    password: str


class RegeneratePasswordReq(BaseModel):
    old_password: str
    new_password: str

class ModifyPassRes(BaseModel):
    new_password: str
class UserWithAvatarRes(BaseModel):
    id: str
    username: str
    emp_id: str
    role: str
    gender: str
    is_first_login: bool
    created_at: datetime
    updated_at: datetime
    avatars: List[AvatarWithAssetsRes]


class LoginRes(BaseModel):
    token: str
    logged_user: CreateUserRes