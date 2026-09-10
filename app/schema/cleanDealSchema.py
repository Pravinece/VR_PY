from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QuestionReq(BaseModel):
    question: str
    answer: str
    points: int


class StageReq(BaseModel):
    stage_number: int
    stage_score: int
    questions: List[QuestionReq] = []


class CreateCleanDealSessionReq(BaseModel):
    user_id: str
    attempt: int = 1
    time_taken: int = 0
    stage: StageReq


class UpdateCleanDealSessionReq(BaseModel):
    stage: Optional[StageReq] = None
    percentage: Optional[float] = None
    time_taken: Optional[int] = None


class StageRes(BaseModel):
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
    stages: List[StageRes] = []
    total_score: int = 0
