import logging
import math
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import SkateSessionModel
from app.schema.skateSessionSchema import CreateSkateSessionReq, SkateSessionRes, SkateSessionWithUserRes, PaginatedSkateSessionRes, SessionUserRes, GiftAssetRes
from app.services.bestScoreService import BestScoreService
from app.core.exception import AppException

logger = logging.getLogger(__name__)


class SkateSessionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["skate_sessions"]
        self.users = db["users"]
        self.best_score_service = BestScoreService(db)

    async def create_session(self, payload: CreateSkateSessionReq) -> SkateSessionRes:
        try:
            user = await self.users.find_one({"_id": payload.user_id})
            if not user:
                raise AppException(status_code=404, message="User not found")

            session = SkateSessionModel(
                user_id=payload.user_id,
                mode=payload.mode,
                score=payload.score,
                coins=payload.coins,
                health=payload.health,
                time=payload.time,
                played_at=datetime.now(timezone.utc),
                gifts=payload.gifts,
                boosters=payload.boosters,
                test=payload.test,
            )

            async with await self.collection.database.client.start_session() as mongo_session:
                async with mongo_session.start_transaction():
                    await self.collection.insert_one(session.model_dump(by_alias=True), session=mongo_session)
                    await self.best_score_service.upsert_best_score(
                        payload.user_id, "skating", payload.mode, payload.score, payload.time, session.id, session=mongo_session
                    )

            return SkateSessionRes(
                id=session.id,
                user=SessionUserRes(
                    id=str(user["_id"]),
                    username=user["username"],
                    emp_id=user["emp_id"],
                    gender=user["gender"],
                    role=user["role"],
                ),
                mode=session.mode,
                score=session.score,
                coins=session.coins,
                health=session.health,
                time=session.time,
                played_at=session.played_at,
                gifts=session.gifts,
                boosters=session.boosters,
                test=session.test,
            )
            
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in create_session")
            raise AppException(status_code=500, message="Failed to create skate session")

    async def get_session_by_id(self, session_id: str) -> SkateSessionWithUserRes:
        try:
            doc = await self.collection.find_one({"_id": session_id})
            if not doc:
                raise AppException(status_code=404, message="Session not found")
            user = await self.users.find_one({"_id": doc["user_id"]})
            if not user:
                raise AppException(status_code=404, message="User not found")

            gift_ids = doc.get("gifts", [])
            assets_collection = self.collection.database["assets"]
            asset_docs = await assets_collection.find({"_id": {"$in": gift_ids}}).to_list(length=None)
            asset_map = {a["_id"]: a for a in asset_docs}
            gifts = [
                GiftAssetRes(
                    id=str(aid),
                    name=asset_map[aid]["name"],
                    type=asset_map[aid]["type"],
                    gender=asset_map[aid]["gender"],
                    image=asset_map[aid]["image"],
                )
                for aid in gift_ids if aid in asset_map
            ]

            return SkateSessionWithUserRes(
                id=str(doc["_id"]),
                user=SessionUserRes(
                    id=str(user["_id"]),
                    username=user["username"],
                    emp_id=user["emp_id"],
                    gender=user["gender"],
                    role=user["role"],
                ),
                mode=doc["mode"],
                score=doc["score"],
                coins=doc["coins"],
                health=doc["health"],
                time=doc["time"],
                played_at=doc["played_at"],
                gifts=gifts,
                boosters=doc.get("boosters", []),
                test=doc.get("test", []),
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_session_by_id")
            raise AppException(status_code=500, message="Failed to fetch skate session")

    async def get_sessions_by_user(self, user_id: str, page: int, limit: int) -> PaginatedSkateSessionRes:
        try:
            user = await self.users.find_one({"_id": user_id})
            if not user:
                raise AppException(status_code=404, message="User not found")

            skip = (page - 1) * limit
            total = await self.collection.count_documents({"user_id": user_id})
            docs = await self.collection.find({"user_id": user_id}).sort("played_at", -1).skip(skip).limit(limit).to_list(length=limit)

            user_res = SessionUserRes(id=str(user["_id"]), username=user["username"], emp_id=user["emp_id"], gender=user["gender"], role=user["role"])
            sessions = [
                SkateSessionRes(
                    id=str(doc["_id"]),
                    user=user_res,
                    mode=doc["mode"],
                    score=doc["score"],
                    coins=doc["coins"],
                    health=doc["health"],
                    time=doc["time"],
                    played_at=doc["played_at"],
                    gifts=doc.get("gifts", []),
                    boosters=doc.get("boosters", []),
                    test=doc.get("test", []),
                )
                for doc in docs
            ]

            return PaginatedSkateSessionRes(
                total=total, page=page, limit=limit,
                total_pages=math.ceil(total / limit) if total > 0 else 0,
                sessions=sessions,
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_sessions_by_user")
            raise AppException(status_code=500, message="Failed to fetch skate sessions")

    async def get_sessions(self, page: int, limit: int) -> PaginatedSkateSessionRes:
        try:
            skip = (page - 1) * limit
            total = await self.collection.count_documents({})
            docs = await self.collection.find().sort("played_at", -1).skip(skip).limit(limit).to_list(length=limit)

            user_ids = list({doc["user_id"] for doc in docs})
            user_docs = await self.users.find({"_id": {"$in": user_ids}}).to_list(length=None)
            user_map = {u["_id"]: u for u in user_docs}

            sessions = [
                SkateSessionRes(
                    id=str(doc["_id"]),
                    user=SessionUserRes(
                        id=doc["user_id"],
                        username=user_map[doc["user_id"]]["username"] if doc["user_id"] in user_map else "Unknown",
                        emp_id=user_map[doc["user_id"]]["emp_id"] if doc["user_id"] in user_map else "",
                        gender=user_map[doc["user_id"]]["gender"] if doc["user_id"] in user_map else "",
                        role=user_map[doc["user_id"]]["role"] if doc["user_id"] in user_map else "",
                    ),
                    mode=doc["mode"],
                    score=doc["score"],
                    coins=doc["coins"],
                    health=doc["health"],
                    time=doc["time"],
                    played_at=doc["played_at"],
                    gifts=doc.get("gifts", []),
                    boosters=doc.get("boosters", []),
                    test=doc.get("test", []),
                )
                for doc in docs
            ]

            return PaginatedSkateSessionRes(
                total=total, page=page, limit=limit,
                total_pages=math.ceil(total / limit) if total > 0 else 0,
                sessions=sessions,
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_sessions")
            raise AppException(status_code=500, message="Failed to fetch skate sessions")


