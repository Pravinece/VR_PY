from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models.userModel import GameModeEnum, SessionStatusEnum, generate_uuid


class CleanDealQuestionModel(BaseModel):
    question: str
    answer: str
    points: int


class FloorModel(BaseModel):
    stage_number: int
    stage_score: int
    percentage: float = 0.0
    time_taken: int = 0         # seconds for this floor
    start_time: datetime
    end_time: datetime
    questions: List[CleanDealQuestionModel] = []


class CleanDealSessionModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    mode: GameModeEnum
    attempt: int = 1
    score: int = 0
    percentage: float = 0.0
    time_taken: int = 0
    status: SessionStatusEnum = SessionStatusEnum.IN_PROGRESS
    played_at: datetime
    stages: List[FloorModel] = []

    model_config = {"populate_by_name": True}


# ─── Request Models ───────────────────────────────────────

class QuestionReq(BaseModel):
    question: str
    answer: str
    points: int


class FloorReq(BaseModel):
    stage_number: int
    stage_score: int
    percentage: float = 0.0
    time_taken: int = 0
    start_time: datetime
    end_time: datetime
    questions: List[QuestionReq] = []


class CreateCleanDealSessionReq(BaseModel):
    user_id: str
    mode: GameModeEnum
    attempt: int = 1


class UpdateCleanDealSessionReq(BaseModel):
    stage: FloorReq


# ─── Response Models ──────────────────────────────────────

class FloorRes(BaseModel):
    stage_number: int
    stage_score: int
    percentage: float
    time_taken: int
    start_time: datetime
    end_time: datetime
    questions: List[QuestionReq] = []


class SessionUserRes(BaseModel):
    id: str
    username: str
    emp_id: str
    gender: str
    role: str


class CleanDealSessionRes(BaseModel):
    id: str
    user_data: Optional[SessionUserRes] = None
    mode: str
    attempt: int
    percentage: float
    time_taken: int
    status: str
    played_at: datetime
    stages: List[FloorRes] = []
    total_score: int = 0


class PaginatedCleanDealSessionRes(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    sessions: List[CleanDealSessionRes]
