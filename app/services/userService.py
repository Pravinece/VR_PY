import logging
import bcrypt

from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schema.userSchema import CreateUserReq, CreateUserRes, LoginRes
from app.models.userModel import UserModel
from app.core.exception import AppException
from app.core.security import JWTHandler

logger = logging.getLogger(__name__)

hashed = bcrypt.hashpw("Welcome@123".encode(), bcrypt.gensalt()).decode()

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def create_user(self, payload: CreateUserReq) -> CreateUserRes:
        try:
            existing = await self.collection.find_one({"emp_id": payload.emp_id})
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

            await self.collection.insert_one(user_model.model_dump(by_alias=True))

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

    async def login_user(self, emp_id: str, password: str) -> LoginRes:
        try:
            user = await self.collection.find_one({"emp_id": emp_id})
            if not user:
                raise AppException(status_code=401, message="Invalid credentials")
            
            # Check password
            decrypted = bcrypt.checkpw(password.encode(), user["password"].encode())
            if not decrypted:
                raise AppException(status_code=401, message="Invalid credentials")

            token = JWTHandler.create_access_token(subject=str({
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
