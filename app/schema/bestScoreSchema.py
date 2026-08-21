from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class BestScoreEntry(BaseModel):
    id: str
    user_id: str
    game_type: str
    mode: str
    best_score: int
    session_id: str
    achieved_at: datetime


class CurrentUserBestScore(BaseModel):
    rank: Optional[int] = None
    best_score: Optional[int] = None
    session_id: Optional[str] = None
    achieved_at: Optional[datetime] = None


class BestScoreLeaderboardRes(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    current_user: CurrentUserBestScore
    results: List[BestScoreEntry]
