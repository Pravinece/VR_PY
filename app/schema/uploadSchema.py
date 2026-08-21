from pydantic import BaseModel
from datetime import datetime


class FileRes(BaseModel):
    id: str
    url: str
    type: str
    created_by: str
    created_at: datetime
