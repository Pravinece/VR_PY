import logging
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.schema.userSchema import CreateUserReq, CreateUserRes, APIResponse, LoginRes, LoginReq
from app.services.userService import UserService
from app.core.security import get_current_user, require_roles

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()


# Only superadmin can create users
@router.post("/users", response_model=APIResponse[CreateUserRes])
async def create_user(
    payload: CreateUserReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin"))
):
    service = UserService(db)
    user = await service.create_user(payload)
    return APIResponse(success=True, message="User created successfully", data=user)


# Public — no auth needed
@router.post("/login", response_model=APIResponse[LoginRes])
async def login(payload: LoginReq, db: AsyncIOMotorDatabase = Depends(get_db)):
    service = UserService(db)
    logged_user = await service.login_user(payload.emp_id, payload.password)
    return APIResponse(success=True, message="User login successfully", data=logged_user)


# Swagger Authorize button uses this endpoint (OAuth2 password flow)
@router.post("/token")
async def token(form: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_db)):
    service = UserService(db)
    # username field is used as emp_id
    result = await service.login_user(form.username, form.password)
    return {"access_token": result.token, "token_type": "bearer"}

@router.post("/seed")
async def createSuperadmin(db: AsyncIOMotorDatabase = Depends(get_db)):
    service = UserService(db)
    superadmin = await service.create_user(CreateUserReq(
        username="SuperAdmin",
        emp_id="SA001",
        role="superadmin",
        gender="male",
    ))
    return {
        "message": "Superadmin created",
        "data": superadmin}
