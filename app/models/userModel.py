from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from uuid import uuid4
from enum import Enum

def generate_uuid() -> str:
    return str(uuid4())

class RoleEnum(str, Enum):
    SUPERADMIN = "superadmin"
    USER = "user"

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    
class GameEnum(str, Enum):
    cleanDeal = "cleanDeal"
    skating = "skating"

class AssetTypeEnum(str, Enum):
    DRESS = "dress"
    GUN = "gun"
    SKATE = "skate"
    WHEELS = "wheels"
class UserModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    username: str
    emp_id: str
    password: str
    role: RoleEnum       
    gender: GenderEnum   
    is_first_login: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}

class AssetModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    name: str
    gender: GenderEnum
    type: AssetTypeEnum
    image: str
    is_default: bool = False
    created_at: datetime

    model_config = {"populate_by_name": True}


class AvatarModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    gender: GenderEnum
    equipped_assets: List[str] = []
    model_config = {"populate_by_name": True}


class UnlockedAssetModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    asset_id: str
    unlocked_at: datetime
    model_config = {"populate_by_name": True}


class FileModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    url: str
    type: str
    created_by: str
    created_at: datetime
    model_config = {"populate_by_name": True}


class BoosterModel(BaseModel):
    name: str
    count: int

class TestModel(BaseModel):
    question: str
    answer: str
    points: int

class SkateSessionModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str                # ref: users._id
    mode: str                   # "easy" | "medium" | "hard"
    score: int
    coins: int
    health: int
    time: int                   # seconds
    played_at: datetime
    gifts: List[str] = []       # list of asset_ids
    boosters: List[BoosterModel] = []
    test: List[TestModel] = []



class QuestionModel(BaseModel):
    question: str
    answer: str
    points: int

class StageModel(BaseModel):
    stage_number: int
    stage_score: int
    questions: List[QuestionModel] = []

class CleanDealSessionModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    attempt: int = 1
    score: int = 0
    percentage: float = 0.0
    time_taken: int = 0
    played_at: datetime
    stages: List[StageModel] = []

    model_config = {"populate_by_name": True}


class UserBestScoreModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str                # ref: users._id
    game_type: str              # "skating" | "cleandeal"
    mode: str                   # "easy" | "medium" | "hard"
    best_score: int
    time_taken: int             # seconds
    session_id: str             # ref: skate_sessions._id or cleandeal_sessions._id
    achieved_at: datetime

    model_config = {"populate_by_name": True}
    
class StagesModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    stage_number: int
    stage_name: str
    stage_description: str
    stage_intro: List[str]
    game: GameEnum

    model_config = {"populate_by_name": True}
