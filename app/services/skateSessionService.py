import logging
import math
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import SkateSessionModel
from app.schema.skateSessionSchema import CreateSkateSessionReq, SkateSessionRes, PaginatedSkateSessionRes
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
                user_id=session.user_id,
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

    async def get_session_by_id(self, session_id: str) -> SkateSessionRes:
        try:
            doc = await self.collection.find_one({"_id": session_id})
            if not doc:
                raise AppException(status_code=404, message="Session not found")
            return SkateSessionRes(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
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
            cursor = self.collection.find({"user_id": user_id}).sort("played_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)

            sessions = [
                SkateSessionRes(
                    id=str(doc["_id"]),
                    user_id=doc["user_id"],
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
                total=total,
                page=page,
                limit=limit,
                total_pages=math.ceil(total / limit) if total > 0 else 0,
                sessions=sessions,
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_sessions_by_user")
            raise AppException(status_code=500, message="Failed to fetch skate sessions")


