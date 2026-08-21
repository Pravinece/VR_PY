from pydantic import BaseModel
from typing import List


class AvatarRes(BaseModel):
    id: str
    user_id: str
    gender: str
    equipped_assets: List[str]


class EquippedAssetDetail(BaseModel):
    id: str
    name: str
    gender: str
    type: str
    image: str
    is_default: bool


class AvatarWithAssetsRes(BaseModel):
    id: str
    gender: str
    equipped_assets: List[EquippedAssetDetail]


class EquipAssetReq(BaseModel):
    asset_id: str
