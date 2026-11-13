from pydantic import BaseModel, Field
from typing import List, Optional
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

class GameModeEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class SessionStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class UserModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    username: str
    emp_id: str
    password: str
    role: RoleEnum
    gender: GenderEnum
    lastCleanDealSession: Optional[str] = None
    lastSkatingSession: Optional[str] = None
    is_first_login: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}

class AssetModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    name: str
    gender: Optional[GenderEnum] = None  # only for dress, None means common (gun/skate/wheels)
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

class DistrictModel(BaseModel):
    district_number: int
    score: int = 0
    coins: int = 0
    health: int = 0
    time: int = 0
    points: int = 0
    start_time: datetime
    end_time: datetime
    gifts: List[str] = []       # list of asset_ids
    boosters: List[BoosterModel] = []
    test: List[TestModel] = []

class SkateSessionModel(BaseModel):
    id: str = Field(default_factory=generate_uuid, alias="_id")
    user_id: str
    mode: str                   # "easy" | "medium" | "hard"
    attempt: int = 1
    total_score: int = 0
    total_coins: int = 0
    total_points: int = 0
    total_time: int = 0
    status: str = "in_progress"
    played_at: datetime
    districts: List[DistrictModel] = []

    model_config = {"populate_by_name": True}



class QuestionModel(BaseModel):
    question: str
    answer: str
    points: int

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
    
