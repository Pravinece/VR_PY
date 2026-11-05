from pydantic import BaseModel, Field
from typing import List
from app.models.userModel import GameEnum, generate_uuid

class StagesModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    stage_number: str
    stage_name: str
    stage_description: str
    stage_intro: List[str]
    game: GameEnum

    model_config = {"populate_by_name": True}

class createStageReq(BaseModel):
    stage_number: str
    stage_name: str
    stage_description: str
    stage_intro: List[str]
    game: GameEnum

class createStageRes(BaseModel):
    id: str = Field(alias="_id")
    stage_number: str
    stage_name: str
    stage_description: str
    stage_intro: List[str]
    game: GameEnum
    
    model_config = {"populate_by_name": True}
    
class listStageRes(BaseModel):
    id: str = Field(alias="_id")
    stage_number: str
    stage_name: str    
    stage_description: str
    stage_intro: List[str]
    game: GameEnum
    
    model_config = {"populate_by_name": True}