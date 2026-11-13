import logging
import math
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schema.cleanDealSchema import (
    CleanDealQuestionModel, CleanDealSessionModel, CreateCleanDealSessionReq,
    FloorModel, UpdateCleanDealSessionReq, CleanDealSessionRes,
    PaginatedCleanDealSessionRes, SessionUserRes
)
from app.core.exception import AppException

logger = logging.getLogger(__name__)


class CleanDealService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["cleandeal_sessions"]
        self.users = db["users"]

    def _to_res(self, doc: dict, user: dict = None) -> CleanDealSessionRes:
        total_score = sum(s.get("stage_score", 0) for s in doc.get("stages", []))
        return CleanDealSessionRes(
            id=doc["_id"],
            user_data=SessionUserRes(
                id=str(user["_id"]),
                username=user["username"],
                emp_id=user["emp_id"],
                gender=user["gender"],
                role=user["role"],
            ) if user else None,
            mode=doc["mode"],
            attempt=doc["attempt"],
            percentage=doc["percentage"],
            time_taken=doc["time_taken"],
            status=doc["status"],
            played_at=doc["played_at"],
            stages=doc.get("stages", []),
            total_score=total_score,
        )
        
    async def get_sessions(self, page: int, limit: int, mode: str, search: str = None) -> PaginatedCleanDealSessionRes:
        try:
            skip = (page - 1) * limit
            session_query = {"mode": mode}

            if search:
                matched_users = await self.users.find(
                    {"$or": [
                        {"emp_id": {"$regex": search, "$options": "i"}},
                        {"username": {"$regex": search, "$options": "i"}},
                    ]},
                    {"_id": 1}
                ).to_list(length=None)
                session_query["user_id"] = {"$in": [u["_id"] for u in matched_users]}

            total = await self.collection.count_documents(session_query)
            docs = await self.collection.find(session_query).sort("played_at", -1).skip(skip).limit(limit).to_list(length=limit)

            user_ids = list({doc["user_id"] for doc in docs})
            users = await self.users.find({"_id": {"$in": user_ids}}).to_list(length=len(user_ids))
            user_map = {u["_id"]: u for u in users}

            return PaginatedCleanDealSessionRes(
                total=total, page=page, limit=limit,
                total_pages=math.ceil(total / limit) if total > 0 else 0,
                sessions=[self._to_res(doc, user_map.get(doc["user_id"])) for doc in docs],
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_sessions")
            raise AppException(status_code=500, message="Failed to fetch clean deal sessions")

    async def get_session_by_id(self, session_id) -> CleanDealSessionRes:
        try:
            doc = await self.collection.find_one({"_id": session_id})
            if not doc:
                raise AppException(status_code=404, message="Session not found")
            user = await self.users.find_one({"_id": doc["user_id"]})
            if not user:
                raise AppException(status_code=404, message="session user not found")
            return self._to_res(doc, user)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_session_by_id")
            raise AppException(status_code=500, message="Failed to fetch session")

    async def create_session(self, payload: CreateCleanDealSessionReq) -> CleanDealSessionRes:
        try:
            user = await self.users.find_one({"_id": payload.user_id})
            if not user:
                raise AppException(status_code=404, message="User not found")

            last_session_id = user.get("lastCleanDealSession")
            if last_session_id:
                last_session = await self.collection.find_one({"_id": last_session_id})
                if last_session and last_session.get("status") == "in_progress":
                    raise AppException(
                        status_code=400,
                        message="Previous session is still in progress. Complete it before starting a new one."
                    )

            session = CleanDealSessionModel(
                user_id=payload.user_id,
                mode=payload.mode,
                attempt=payload.attempt,
                played_at=datetime.now(timezone.utc),
            )
            await self.collection.insert_one(session.model_dump(by_alias=True))

            # store last session id in user
            await self.users.update_one(
                {"_id": payload.user_id},
                {"$set": {"lastCleanDealSession": session.id}}
            )

            doc = await self.collection.find_one({"_id": session.id})
            return self._to_res(doc)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in create_session")
            raise AppException(status_code=500, message="Failed to create clean deal session")

    async def update_session(self, session_id: str, payload: UpdateCleanDealSessionReq) -> CleanDealSessionRes:
        try:
            session = await self.collection.find_one({"_id": session_id})
            if not session:
                raise AppException(status_code=404, message="Session not found")

            floor = FloorModel(
                stage_number=payload.stage.stage_number,
                stage_score=payload.stage.stage_score,
                percentage=payload.stage.percentage,
                time_taken=payload.stage.time_taken,
                start_time=payload.stage.start_time,
                end_time=payload.stage.end_time,
                questions=[CleanDealQuestionModel(**q.model_dump()) for q in payload.stage.questions],
            )
            await self.collection.update_one(
                {"_id": session_id},
                {"$push": {"stages": floor.model_dump()}}
            )

            # recalculate total score, percentage, time_taken from all stages
            doc = await self.collection.find_one({"_id": session_id})
            stages = doc.get("stages", [])
            total_score = sum(s.get("stage_score", 0) for s in stages)
            avg_percentage = sum(s.get("percentage", 0.0) for s in stages) / len(stages) if stages else 0.0
            total_time = sum(s.get("time_taken", 0) for s in stages)

            await self.collection.update_one(
                {"_id": session_id},
                {"$set": {
                    "score": total_score,
                    "percentage": avg_percentage,
                    "time_taken": total_time,
                }}
            )

            doc = await self.collection.find_one({"_id": session_id})
            return self._to_res(doc)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in update_session")
            raise AppException(status_code=500, message="Failed to update clean deal session")
