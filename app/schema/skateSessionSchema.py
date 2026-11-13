from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.userModel import BoosterModel, TestModel, GameModeEnum


# ─── District Models ──────────────────────────────────────

class DistrictReq(BaseModel):
    district_number: int
    score: int = 0
    coins: int = 0
    health: int = 0
    time: int = 0
    points: int = 0
    start_time: datetime
    end_time: datetime
    gifts: List[str] = []
    boosters: List[BoosterModel] = []
    test: List[TestModel] = []


class DistrictRes(BaseModel):
    district_number: int
    score: int
    coins: int
    health: int
    time: int
    points: int
    start_time: datetime
    end_time: datetime
    gifts: List[str] = []
    boosters: List[BoosterModel] = []
    test: List[TestModel] = []


# ─── Session Request Models ───────────────────────────────

class CreateSkateSessionReq(BaseModel):
    user_id: str
    mode: GameModeEnum
    attempt: int = 1


class UpdateSkateSessionReq(BaseModel):
    district: DistrictReq


# ─── User in Response ─────────────────────────────────────

class SessionUserRes(BaseModel):
    id: str
    username: str
    emp_id: str
    gender: str
    role: str


# ─── Session Response Models ──────────────────────────────

class SkateSessionRes(BaseModel):
    id: str
    user_data: Optional[SessionUserRes] = None
    mode: str
    attempt: int
    total_score: int
    total_coins: int
    total_points: int
    total_time: int
    status: str
    played_at: datetime
    districts: List[DistrictRes] = []


class SkateSessionWithUserRes(BaseModel):
    id: str
    user: SessionUserRes
    mode: str
    attempt: int
    total_score: int
    total_coins: int
    total_points: int
    total_time: int
    status: str
    played_at: datetime
    districts: List[DistrictRes] = []


class PaginatedSkateSessionRes(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    sessions: List[SkateSessionRes]
