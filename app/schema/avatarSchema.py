from pydantic import BaseModel
from typing import List


class AvatarRes(BaseModel):
    id: str
    user_id: str
    gender: str
    equipped_assets: List[str]
