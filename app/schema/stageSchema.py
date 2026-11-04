

from pydantic import BaseModel
from typing import List
from app.models.userModel import GameEnum


class createStageReq(BaseModel):
    stage_number: int
    stage_name: str
    stage_description: str
    stage_intro: List[str]
    game: GameEnum

class createStageRes(BaseModel):
    id: str
    stage_number: int
    stage_name: str
    stage_description: str
    stage_intro: List[str]
    game: GameEnum
    
class listStageRes(BaseModel):
    id: str
    stage_number: int
    stage_name: str    
    stage_description: str
    stage_intro: List[str]
    game: GameEnum