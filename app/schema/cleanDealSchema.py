from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.models.userModel import QuestionModel, StageModel


class CreateCleanDealSessionReq(BaseModel):
    user_id: str
    attempt: int
    score: int
    percentage: float
    time_taken: int
    stages: List[StageModel] = []


class CleanDealSessionRes(BaseModel):
    id: str
    user_id: str
    mode: str
    attempt: int
    score: int
    percentage: float
    time_taken: int
    played_at: datetime
    stages: List[StageModel]


class PaginatedCleanDealSessionRes(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    sessions: List[CleanDealSessionRes]
