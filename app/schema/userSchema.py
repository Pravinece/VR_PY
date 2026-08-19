from pydantic import BaseModel
from datetime import datetime
from typing import Generic, TypeVar, Optional
from app.models.userModel import RoleEnum, GenderEnum

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

class LoginReq(BaseModel):
    emp_id: str
    password: str


class LoginRes(BaseModel):
    token: str
    logged_user: CreateUserRes