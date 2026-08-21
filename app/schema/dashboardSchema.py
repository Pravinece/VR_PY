from pydantic import BaseModel
from typing import List


class MonthlyGameStat(BaseModel):
    month: str
    skating: int
    cleandeal: int


class GameStatsRes(BaseModel):
    year: int
    months: List[MonthlyGameStat]
