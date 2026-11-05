import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.db import mongodb
from app.core.security import require_roles
from app.schema.questionSchema import (
    createQuestionReq, 
    bulkCreateQuestionReq, 
    listQuestionRes, 
    questionModel,
    updateQuestionReq
)
from app.schema.userSchema import APIResponse
from app.services.questionSevice import questionService

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_db() -> AsyncIOMotorDatabase:
    return await mongodb.get_database()

@router.post("/questions", response_model=APIResponse[listQuestionRes])
async def create_question(
    payload: createQuestionReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin"))
):
    service = questionService(db)
    question = await service.create_question(payload)
    return APIResponse(success=True, message="Question created successfully", data=question)

@router.post("/questions/bulk", response_model=APIResponse[List[listQuestionRes]])
async def create_questions_bulk(
    payload: bulkCreateQuestionReq,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(require_roles("superadmin"))
):
    service = questionService(db)
    questions = await service.create_questions_bulk(payload)
    return APIResponse(success=True, message=f"{len(questions)} questions created successfully", data=questions)

@router.get("/questions", response_model=APIResponse[List[listQuestionRes]])
async def get_questions(
    stage_id: str,
    is_archived: bool | None = None,
    current_user: dict = Depends(require_roles("superadmin", "user")),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = questionService(db)
    questions = await service.get_questions(stage_id=stage_id, is_archived=is_archived)
    return APIResponse(success=True, message="Questions retrieved successfully", data=questions)

@router.patch("/questions/{question_id}", response_model=APIResponse[listQuestionRes])
async def update_question(
    question_id: str,
    payload: updateQuestionReq,
    current_user: dict = Depends(require_roles("superadmin")),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    service = questionService(db)
    updated_question = await service.update_question(question_id, payload)
    
    if not updated_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
        
    return APIResponse(success=True, message="Question updated successfully", data=updated_question)