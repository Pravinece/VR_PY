import logging
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db import mongodb
from app.schema.userSchema import CreateUserReq, CreateUserRes, APIResponse, LoginRes, LoginReq, ModifyPassRes, RegeneratePasswordReq, UserWithAvatarRes, UpdateUserReq
from app.schema.avatarSchema import AvatarWithAssetsRes, EquipAssetReq
from app.services.userService import UserService
from app.services.avatarService import AvatarService
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


@router.get("/users/{user_id}", response_model=APIResponse[UserWithAvatarRes])
async def get_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = UserService(db)
    user = await service.get_user_with_avatar(user_id)
    return APIResponse(success=True, message="User fetched successfully", data=user)


# Public — no auth needed
@router.post("/login", response_model=APIResponse[LoginRes])
async def login(payload: LoginReq, db: AsyncIOMotorDatabase = Depends(get_db)):
    service = UserService(db)
    logged_user = await service.login_user(payload.emp_id, payload.password)
    return APIResponse(success=True, message="User login successfully", data=logged_user)

@router.patch("/regenerate-password", response_model=APIResponse[ModifyPassRes])
async def regenarate_password(
    payload: RegeneratePasswordReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("user", "superadmin"))
):
    service = UserService(db)
    updated_user = await service.regenerate_password(current_user['id'], payload.old_password, payload.new_password)
    return APIResponse(success=True, message="Password changed successfully", data=updated_user)

@router.patch("/reset-password", response_model=APIResponse[ModifyPassRes])
async def reset_password(user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin"))
    ):
    service = UserService(db)
    updated_user = await service.reset_password(user_id)
    return APIResponse(success=True, message="Password reset successfully", data=updated_user)
    

@router.patch("/users/{user_id}", response_model=APIResponse[CreateUserRes])
async def update_user(
    user_id: str,
    payload: UpdateUserReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin")),
):
    service = UserService(db)
    user = await service.update_user(user_id, payload)
    return APIResponse(success=True, message="User updated successfully", data=user)


@router.patch("/users/{user_id}/equip", response_model=APIResponse[AvatarWithAssetsRes])
async def equip_asset(
    user_id: str,
    payload: EquipAssetReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("user", "superadmin")),
):
    service = AvatarService(db)
    avatar = await service.equip_asset(user_id, payload.asset_id)
    return APIResponse(success=True, message="Asset equipped successfully", data=avatar)


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
