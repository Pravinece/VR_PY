from pydantic import BaseModel
from datetime import datetime


class UnlockAssetReq(BaseModel):
    asset_id: str


class UnlockedAssetRes(BaseModel):
    id: str
    user_id: str
    asset_id: str
    unlocked_at: datetime
