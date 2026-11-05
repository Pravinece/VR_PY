from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models.userModel import generate_uuid

class CleanDealQuestionModel(BaseModel):
    question: str
    answer: str
    points: int

class FloorModel(BaseModel):
    stage_number: int
    stage_score: int
    questions: List[CleanDealQuestionModel] = []

class CleanDealSessionModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    attempt: int = 1
    score: int = 0
    percentage: float = 0.0
    time_taken: int = 0
    played_at: datetime
    stages: List[FloorModel] = []

    model_config = {"populate_by_name": True}


class QuestionReq(BaseModel):
    question: str
    answer: str
    points: int

class FloorReq(BaseModel):
    stage_number: int
    stage_score: int
    questions: List[QuestionReq] = []


class CreateCleanDealSessionReq(BaseModel):
    user_id: str
    attempt: int = 1
    time_taken: int = 0
    stage: []


class UpdateCleanDealSessionReq(BaseModel):
    stage: Optional[FloorReq] = None
    percentage: Optional[float] = None
    time_taken: Optional[int] = None


class FloorRes(BaseModel):
    stage_number: int
    stage_score: int
    questions: List[QuestionReq] = []


class CleanDealSessionRes(BaseModel):
    id: str
    user_id: str
    attempt: int
    percentage: float
    time_taken: int
    played_at: datetime
    stages: List[FloorRes] = []
    total_score: int = 0
