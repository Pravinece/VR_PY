import logging
import math
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import SkateSessionModel, DistrictModel
from app.schema.skateSessionSchema import (
    CreateSkateSessionReq, UpdateSkateSessionReq,
    SkateSessionRes, SkateSessionWithUserRes,
    PaginatedSkateSessionRes, SessionUserRes
)
from app.core.exception import AppException

logger = logging.getLogger(__name__)


class SkateSessionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["skate_sessions"]
        self.users = db["users"]

    def _to_res(self, doc: dict, user: dict = None) -> SkateSessionRes:
        return SkateSessionRes(
            id=doc["_id"],
            user_data=SessionUserRes(
                id=str(user["_id"]),
                username=user["username"],
                emp_id=user["emp_id"],
                gender=user["gender"],
                role=user["role"],
            ) if user else None,
            mode=doc["mode"],
            attempt=doc.get("attempt", 1),
            total_score=doc.get("total_score", 0),
            total_coins=doc.get("total_coins", 0),
            total_points=doc.get("total_points", 0),
            total_time=doc.get("total_time", 0),
            status=doc.get("status", "in_progress"),
            played_at=doc["played_at"],
            districts=doc.get("districts", []),
        )

    async def create_session(self, payload: CreateSkateSessionReq) -> SkateSessionRes:
        try:
            user = await self.users.find_one({"_id": payload.user_id})
            if not user:
                raise AppException(status_code=404, message="User not found")

            last_session_id = user.get("lastSkatingSession")
            if last_session_id:
                last_session = await self.collection.find_one({"_id": last_session_id})
                if last_session and last_session.get("status") == "in_progress":
                    raise AppException(
                        status_code=400,
                        message="Previous session is still in progress. Complete it before starting a new one."
                    )

            session = SkateSessionModel(
                user_id=payload.user_id,
                mode=payload.mode,
                attempt=payload.attempt,
                played_at=datetime.now(timezone.utc),
            )
            await self.collection.insert_one(session.model_dump(by_alias=True))

            await self.users.update_one(
                {"_id": payload.user_id},
                {"$set": {"lastSkatingSession": session.id}}
            )

            doc = await self.collection.find_one({"_id": session.id})
            return self._to_res(doc)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in create_session")
            raise AppException(status_code=500, message="Failed to create skate session")

    async def update_session(self, session_id: str, payload: UpdateSkateSessionReq) -> SkateSessionRes:
        try:
            session = await self.collection.find_one({"_id": session_id})
            if not session:
                raise AppException(status_code=404, message="Session not found")

            if session.get("status") == "completed":
                raise AppException(status_code=400, message="Session already completed")

            district = DistrictModel(
                district_number=payload.district.district_number,
                score=payload.district.score,
                coins=payload.district.coins,
                health=payload.district.health,
                time=payload.district.time,
                points=payload.district.points,
                start_time=payload.district.start_time,
                end_time=payload.district.end_time,
                gifts=payload.district.gifts,
                boosters=[b.model_dump() for b in payload.district.boosters],
                test=[t.model_dump() for t in payload.district.test],
            )

            await self.collection.update_one(
                {"_id": session_id},
                {"$push": {"districts": district.model_dump()}}
            )

            # recalculate totals from all districts
            doc = await self.collection.find_one({"_id": session_id})
            districts = doc.get("districts", [])
            total_score = sum(d.get("score", 0) for d in districts)
            total_coins = sum(d.get("coins", 0) for d in districts)
            total_points = sum(d.get("points", 0) for d in districts)
            total_time = sum(d.get("time", 0) for d in districts)

            await self.collection.update_one(
                {"_id": session_id},
                {"$set": {
                    "total_score": total_score,
                    "total_coins": total_coins,
                    "total_points": total_points,
                    "total_time": total_time,
                }}
            )

            doc = await self.collection.find_one({"_id": session_id})
            return self._to_res(doc)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in update_session")
            raise AppException(status_code=500, message="Failed to update skate session")

    async def get_session_by_id(self, session_id: str) -> SkateSessionWithUserRes:
        try:
            doc = await self.collection.find_one({"_id": session_id})
            if not doc:
                raise AppException(status_code=404, message="Session not found")
            user = await self.users.find_one({"_id": doc["user_id"]})
            if not user:
                raise AppException(status_code=404, message="User not found")

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
                attempt=doc.get("attempt", 1),
                total_score=doc.get("total_score", 0),
                total_coins=doc.get("total_coins", 0),
                total_points=doc.get("total_points", 0),
                total_time=doc.get("total_time", 0),
                status=doc["status"],
                played_at=doc["played_at"],
                districts=doc.get("districts", []),
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

            user = await self.users.find_one({"_id": user_id})
            return PaginatedSkateSessionRes(
                total=total, page=page, limit=limit,
                total_pages=math.ceil(total / limit) if total > 0 else 0,
                sessions=[self._to_res(doc, user) for doc in docs],
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_sessions_by_user")
            raise AppException(status_code=500, message="Failed to fetch skate sessions")

    async def get_sessions(self, page: int, limit: int, mode: str, search: str = None) -> PaginatedSkateSessionRes:
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

            return PaginatedSkateSessionRes(
                total=total, page=page, limit=limit,
                total_pages=math.ceil(total / limit) if total > 0 else 0,
                sessions=[self._to_res(doc, user_map.get(doc["user_id"])) for doc in docs],
            )
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_sessions")
            raise AppException(status_code=500, message="Failed to fetch skate sessions")
