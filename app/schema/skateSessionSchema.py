from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.userModel import BoosterModel, TestModel


class PaginatedSkateSessionRes(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    sessions: List["SkateSessionRes"]


class CreateSkateSessionReq(BaseModel):
    user_id: str
    mode: str                       # "easy" | "medium" | "hard"
    score: int
    coins: int
    health: int
    time: int                       # seconds
    gifts: List[str] = []           # list of asset_ids
    boosters: List[BoosterModel] = []
    test: List[TestModel] = []


class SkateSessionRes(BaseModel):
    id: str
    user_id: str
    mode: str
    score: int
    coins: int
    health: int
    time: int
    gifts: List[str]
    boosters: List[BoosterModel]
    test: List[TestModel]
