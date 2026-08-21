from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class BestScoreUser(BaseModel):
    id: str
    username: str
    emp_id: str


class BestScoreEntry(BaseModel):
    id: str
    user: BestScoreUser
    game_type: str
    mode: str
    best_score: int
    time_taken: int
    session_id: str
    achieved_at: datetime


class CurrentUserBestScore(BaseModel):
    rank: Optional[int] = None
    best_score: Optional[int] = None
    time_taken: Optional[int] = None
    session_id: Optional[str] = None
    achieved_at: Optional[datetime] = None


class BestScoreLeaderboardRes(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    current_user: CurrentUserBestScore
    results: List[BestScoreEntry]
