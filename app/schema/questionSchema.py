from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.userModel import GameModeEnum, generate_uuid

class questionModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    context: List[str]
    question: str
    options: List[str]
    correctExplanation: str
    wrongExplanation: str
    answer: str
    stage_id: str
    game_mode: GameModeEnum
    is_archived: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"populate_by_name": True}
    
class createQuestionReq(BaseModel):
    context: List[str]
    question: str
    options: List[str]
    correctExplanation: str
    wrongExplanation: str
    answer: str
    stage_id: str
    is_archived: bool = Field(default=False)
    game_mode: GameModeEnum

class bulkCreateQuestionReq(BaseModel):
    questions: List[createQuestionReq]
    
class listQuestionRes(BaseModel):
    id: str = Field(alias="_id")
    context: List[str]
    question: str
    options: List[str]
    correctExplanation: str
    wrongExplanation: str
    answer: str
    stage_id: str
    game_mode: GameModeEnum
    is_archived: bool
    
    model_config = {"populate_by_name": True}
    
class updateQuestionReq(BaseModel):
    context: Optional[List[str]] = None
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correctExplanation: Optional[str] = None
    wrongExplanation: Optional[str] = None
    answer: Optional[str] = None
    game_mode: Optional[GameModeEnum] = None
    is_archived: Optional[bool] = None  # Used for archive / unarchive