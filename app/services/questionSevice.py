import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.core.exception import AppException
from app.schema.questionSchema import createQuestionReq, bulkCreateQuestionReq, updateQuestionReq, questionModel

logger = logging.getLogger(__name__)

class questionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["questions"]
        self.stages_collection = db["stages"]
        self.db = db

    async def _verify_stage_exists(self, stage_id: str):
        # Optional: verify if stage exists before inserting questions
        stage = await self.stages_collection.find_one({"_id": stage_id})
        if not stage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Stage with id '{stage_id}' not found"
            )

    async def create_question(self, payload: createQuestionReq):
        await self._verify_stage_exists(payload.stage_id)
        
        question_data = questionModel(**payload.model_dump())
        doc = question_data.model_dump(by_alias=True)
        
        await self.collection.insert_one(doc)
        
        # Map back _id to id for response model mapping
        doc["id"] = doc["_id"]
        return doc

    async def create_questions_bulk(self, payload: bulkCreateQuestionReq):
        if not payload.questions:
            return []
            
        # Verify stage using the first item (or verify all if they span multiple stages)
        stage_id = payload.questions[0].stage_id
        await self._verify_stage_exists(stage_id)

        documents = []
        for q_req in payload.questions:
            question_data = questionModel(**q_req.model_dump())
            doc = question_data.model_dump(by_alias=True)
            doc["id"] = doc["_id"]  # keep tracking id
            documents.append(doc)

        await self.collection.insert_many(documents)
        return documents

    async def get_questions(self, stage_id: str, is_archived: bool | None = None):
        try:
            query = {"stage_id": stage_id}
            
            if is_archived is not None:
                query["is_archived"] = is_archived

            questions_cursor = self.collection.find(query)
            questions = await questions_cursor.to_list(length=100)
            
            for doc in questions:
                doc["id"] = str(doc["_id"])
                
            return questions
        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_questions")
            raise AppException(status_code=500, message="Failed to retrieve questions")
        
    async def update_question(self, question_id: str, payload: updateQuestionReq) -> dict | None:
        try:
            # Extract only the fields that were explicitly sent in the request
            update_data = payload.model_dump(exclude_unset=True)
            
            if not update_data:
                # If nothing was provided to update, just return the current document if it exists
                doc = await self.collection.find_one({"_id": question_id})
                if doc:
                    doc["id"] = str(doc["_id"])
                    return doc
                return None

            # Always update the timestamp when a modification occurs
            update_data["updated_at"] = datetime.now(timezone.utc)

            # Perform the update
            result = await self.collection.update_one(
                {"_id": question_id},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return None

            # Fetch and return the updated document
            updated_doc = await self.collection.find_one({"_id": question_id})
            if updated_doc:
                updated_doc["id"] = str(updated_doc["_id"])
                return updated_doc
                
            return None
            
        except Exception:
            logger.exception("Unexpected error in update_question")
            raise AppException(status_code=500, message="Failed to update question")