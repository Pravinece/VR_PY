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
    mode: str
    score: int
    coins: int
    health: int
    time: int
    gifts: List[str] = []
    boosters: List[BoosterModel] = []
    test: List[TestModel] = []



class SessionUserRes(BaseModel):
    id: str
    username: str
    emp_id: str
    gender: str
    role: str


class SkateSessionRes(BaseModel):
    id: str
    user: SessionUserRes
    mode: str
    score: int
    coins: int
    health: int
    time: int
    played_at: datetime
    gifts: List[str]
    boosters: List[BoosterModel]
    test: List[TestModel]


class GiftAssetRes(BaseModel):
    id: str
    name: str
    type: str
    gender: str
    image: str


class SkateSessionWithUserRes(BaseModel):
    id: str
    user: SessionUserRes
    mode: str
    score: int
    coins: int
    health: int
    time: int
    played_at: datetime
    gifts: List[GiftAssetRes]
    boosters: List[BoosterModel]
    test: List[TestModel]
