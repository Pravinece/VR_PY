from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.userModel import GenderEnum, AssetTypeEnum


class CreateAssetReq(BaseModel):
    name: str
    gender: GenderEnum
    type: AssetTypeEnum
    image: str
    is_default: bool = False


class UpdateAssetReq(BaseModel):
    name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    type: Optional[AssetTypeEnum] = None
    image: Optional[str] = None
    is_default: Optional[bool] = None


class AssetRes(BaseModel):
    id: str
    name: str
    gender: str
    type: str
    image: str
    is_default: bool
    created_at: datetime
    
class AssetListRes(BaseModel):
    assets: list[AssetRes]
