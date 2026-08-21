import logging
import math
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import CleanDealSessionModel
from app.schema.cleanDealSchema import CreateCleanDealSessionReq, CleanDealSessionRes, PaginatedCleanDealSessionRes
from app.services.bestScoreService import BestScoreService
from app.core.exception import AppException

logger = logging.getLogger(__name__)

GAME_TYPE = "cleandeal"
MODE = "easy"


class CleanDealService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["cleandeal_sessions"]
        self.users = db["users"]
        self.best_score_service = BestScoreService(db)

    async def create_session(self, payload: CreateCleanDealSessionReq) -> CleanDealSessionRes:
        try:
            user = await self.users.find_one({"_id": payload.user_id})
            if not user:
                raise AppException(status_code=404, message="User not found")

            session = CleanDealSessionModel(
                user_id=payload.user_id,
                attempt=payload.attempt,
                score=payload.score,
                percentage=payload.percentage,
                time_taken=payload.time_taken,
                played_at=datetime.now(timezone.utc),
                stages=payload.stages,
            )

            async with await self.collection.database.client.start_session() as mongo_session:
                async with mongo_session.start_transaction():
                    await self.collection.insert_one(session.model_dump(by_alias=True), session=mongo_session)
                    await self.best_score_service.upsert_best_score(
                        payload.user_id, GAME_TYPE, MODE, payload.score, payload.time_taken, session.id, session=mongo_session
                    )

            return CleanDealSessionRes(
                id=session.id,
                user_id=session.user_id,
                mode=MODE,
                attempt=session.attempt,
                score=session.score,
                percentage=session.percentage,
                time_taken=session.time_taken,
                played_at=session.played_at,
                stages=session.stages,
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in create_session")
            raise AppException(status_code=500, message="Failed to create clean deal session")

    async def get_session_by_id(self, session_id: str) -> CleanDealSessionRes:
        try:
            doc = await self.collection.find_one({"_id": session_id})
            if not doc:
                raise AppException(status_code=404, message="Session not found")
            return self._to_res(doc)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_session_by_id")
            raise AppException(status_code=500, message="Failed to fetch clean deal session")

    async def get_sessions_by_user(self, user_id: str, page: int, limit: int) -> PaginatedCleanDealSessionRes:
        try:
            user = await self.users.find_one({"_id": user_id})
            if not user:
                raise AppException(status_code=404, message="User not found")

            skip = (page - 1) * limit
            total = await self.collection.count_documents({"user_id": user_id})
            docs = await self.collection.find({"user_id": user_id}).sort("played_at", -1).skip(skip).limit(limit).to_list(length=limit)

            return PaginatedCleanDealSessionRes(
                total=total,
                page=page,
                limit=limit,
                total_pages=math.ceil(total / limit) if total > 0 else 0,
                sessions=[self._to_res(doc) for doc in docs],
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_sessions_by_user")
            raise AppException(status_code=500, message="Failed to fetch clean deal sessions")

    def _to_res(self, doc: dict) -> CleanDealSessionRes:
        return CleanDealSessionRes(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            mode=MODE,
            attempt=doc["attempt"],
            score=doc["score"],
            percentage=doc["percentage"],
            time_taken=doc["time_taken"],
            played_at=doc["played_at"],
            stages=doc.get("stages", []),
        )
