import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import CleanDealSessionModel, StageModel, QuestionModel
from app.schema.cleanDealSchema import CreateCleanDealSessionReq, UpdateCleanDealSessionReq, CleanDealSessionRes
from app.core.exception import AppException
from app.services.userService import UserService

logger = logging.getLogger(__name__)


class CleanDealService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["cleandeal_sessions"]
        self.user_service = UserService(db)

    def _to_res(self, doc: dict) -> CleanDealSessionRes:
        total_score = sum(s.get("stage_score", 0) for s in doc.get("stages", []))
        return CleanDealSessionRes(
            id=doc["_id"],
            user_id=doc["user_id"],
            attempt=doc["attempt"],
            percentage=doc["percentage"],
            time_taken=doc["time_taken"],
            played_at=doc["played_at"],
            stages=doc.get("stages", []),
            total_score=total_score,
        )

    async def create_session(self, payload: CreateCleanDealSessionReq) -> CleanDealSessionRes:
        try:
            await self.user_service.get_user_by_id(payload.user_id)

            stage = StageModel(
                stage_number=payload.stage.stage_number,
                stage_score=payload.stage.stage_score,
                questions=[QuestionModel(**q.model_dump()) for q in payload.stage.questions],
            )
            session = CleanDealSessionModel(
                user_id=payload.user_id,
                attempt=payload.attempt,
                score=stage.stage_score,
                time_taken=payload.time_taken,
                played_at=datetime.now(timezone.utc),
                stages=[stage],
            )
            await self.collection.insert_one(session.model_dump(by_alias=True))

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

            updates = {}

            if payload.stage:
                stage = StageModel(
                    stage_number=payload.stage.stage_number,
                    stage_score=payload.stage.stage_score,
                    questions=[QuestionModel(**q.model_dump()) for q in payload.stage.questions],
                )
                await self.collection.update_one(
                    {"_id": session_id},
                    {"$push": {"stages": stage.model_dump()}},
                )

            if payload.percentage is not None:
                updates["percentage"] = payload.percentage
            if payload.time_taken is not None:
                updates["time_taken"] = payload.time_taken

            if updates:
                await self.collection.update_one({"_id": session_id}, {"$set": updates})

            doc = await self.collection.find_one({"_id": session_id})
            total_score = sum(s.get("stage_score", 0) for s in doc.get("stages", []))
            await self.collection.update_one({"_id": session_id}, {"$set": {"score": total_score}})

            return self._to_res(doc)
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in update_session")
            raise AppException(status_code=500, message="Failed to update clean deal session")
