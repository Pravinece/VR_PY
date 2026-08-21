import logging
import bcrypt
import json

from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schema.userSchema import CreateUserReq, CreateUserRes, LoginRes, ModifyPassRes, UserWithAvatarRes
from app.schema.avatarSchema import AvatarWithAssetsRes, EquippedAssetDetail
from app.models.userModel import UserModel
from app.core.exception import AppException
from app.core.security import JWTHandler
from app.services.avatarService import AvatarService

logger = logging.getLogger(__name__)

hashed = bcrypt.hashpw("Welcome@123".encode(), bcrypt.gensalt()).decode()

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]
        self.db = db

    async def create_user(self, payload: CreateUserReq) -> CreateUserRes:
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                try:
                    existing = await self.collection.find_one({"emp_id": payload.emp_id}, session=session)
                    if existing:
                        raise AppException(status_code=409, message="Employee ID already exists")

                    now = datetime.now(timezone.utc)
                    user_model = UserModel(
                        username=payload.username,
                        emp_id=payload.emp_id,
                        role=payload.role,
                        gender=payload.gender,
                        password=hashed,
                        is_first_login=True,
                        created_at=now,
                        updated_at=now,
                    )
                    await self.collection.insert_one(user_model.model_dump(by_alias=True), session=session)

                    avatar_service = AvatarService(self.db)
                    await avatar_service.create_avatars_for_user(user_model.id, session=session)

                    return CreateUserRes(
                        id=user_model.id,
                        username=user_model.username,
                        emp_id=user_model.emp_id,
                        role=user_model.role,
                        gender=user_model.gender,
                        is_first_login=user_model.is_first_login,
                        created_at=user_model.created_at,
                        updated_at=user_model.updated_at,
                    )
                except AppException:
                    raise
                except Exception:
                    logger.exception("Unexpected error in create_user")
                    raise AppException(status_code=500, message="Failed to create user")

    async def get_user_by_id(self, user_id: str) -> dict:
        user = await self.collection.find_one({"_id": user_id})
        if not user:
            raise AppException(status_code=404, message="User not found")
        return user

    async def get_user_res_by_id(self, user_id: str) -> CreateUserRes:
        user = await self.get_user_by_id(user_id)
        return CreateUserRes(
            id=str(user["_id"]),
            username=user["username"],
            emp_id=user["emp_id"],
            role=user["role"],
            gender=user["gender"],
            is_first_login=user["is_first_login"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )

    async def get_user_with_avatar(self, user_id: str) -> UserWithAvatarRes:
        try:
            user = await self.get_user_by_id(user_id)
            avatars_cursor = self.db["avatars"].find({"user_id": user_id})
            avatar_docs = await avatars_cursor.to_list(length=None)

            avatar_res_list = []
            for avatar in avatar_docs:
                asset_ids = avatar.get("equipped_assets", [])
                asset_docs = await self.db["assets"].find({"_id": {"$in": asset_ids}}).to_list(length=None)
                asset_map = {a["_id"]: a for a in asset_docs}
                equipped = [
                    EquippedAssetDetail(
                        id=str(aid),
                        name=asset_map[aid]["name"],
                        gender=asset_map[aid]["gender"],
                        type=asset_map[aid]["type"],
                        image=asset_map[aid]["image"],
                        is_default=asset_map[aid]["is_default"],
                    )
                    for aid in asset_ids if aid in asset_map
                ]
                avatar_res_list.append(AvatarWithAssetsRes(
                    id=str(avatar["_id"]),
                    gender=avatar["gender"],
                    equipped_assets=equipped,
                ))

            return UserWithAvatarRes(
                id=str(user["_id"]),
                username=user["username"],
                emp_id=user["emp_id"],
                role=user["role"],
                gender=user["gender"],
                is_first_login=user["is_first_login"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                avatars=avatar_res_list,
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_user_with_avatar")
            raise AppException(status_code=500, message="Failed to fetch user")

    async def login_user(self, emp_id: str, password: str) -> LoginRes:
        try:
            user = await self.collection.find_one({"emp_id": emp_id})
            if not user:
                raise AppException(status_code=401, message="Invalid credentials")
            
            # Check password
            decrypted = bcrypt.checkpw(password.encode(), user["password"].encode())
            if not decrypted:
                raise AppException(status_code=401, message="Invalid credentials")

            token = JWTHandler.create_access_token(subject=json.dumps({
                "empId": user["emp_id"],
                "id": str(user["_id"]),
                "role": user["role"]
            }))
            logged_user = CreateUserRes(
                id=str(user["_id"]),
                username=user["username"],
                emp_id=user["emp_id"],
                role=user["role"],
                gender=user["gender"],
                is_first_login=user["is_first_login"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
            )
            return LoginRes(token=token, logged_user=logged_user)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in login_user")
            raise AppException(status_code=500, message="Login failed")

    async def regenerate_password(self, user_id: str, old_password: str, new_password: str) -> ModifyPassRes:
        try:
            user = await self.collection.find_one({"_id": user_id})
            if not user:
                raise AppException(status_code=404, message="User not found")

            decrypted = bcrypt.checkpw(old_password.encode(), user["password"].encode())
            if not decrypted:
                raise AppException(status_code=400, message="Old password is incorrect")

            hashed_new = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": {"password": hashed_new, "is_first_login": False}}
            )

            if result.modified_count == 0:
                raise AppException(status_code=500, message="Failed to update password")

            return ModifyPassRes(new_password=new_password)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in regenerate_password")
            raise AppException(status_code=500, message="Failed to change password")
        
    async def reset_password(self, user_id: str) -> ModifyPassRes:
        try:
            user = await self.collection.find_one({"_id": user_id})
            
            if not user:
                raise AppException(status_code=404, message="User not found")
            
            hashed_new = bcrypt.hashpw("Welcome@123".encode(), bcrypt.gensalt()).decode()
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": {"password": hashed_new, "is_first_login": True}}
            )

            if result.modified_count == 0:
                raise AppException(status_code=500, message="Failed to reset password")

            return ModifyPassRes(new_password="Welcome@123")
        
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in reset_password")
            raise AppException(status_code=500, message="Failed to reset password")
