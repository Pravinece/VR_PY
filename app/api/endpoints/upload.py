import uuid
import os
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.core.exception import AppException
from app.core.config import settings
from app.core.security import get_current_user
from app.core.db import mongodb
from app.models.userModel import FileModel
from app.schema.uploadSchema import FileRes
from app.core.security import require_roles

router = APIRouter()

UPLOAD_DIR = "uploads/images"
ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png"}
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/image", response_model=FileRes)
async def upload_image(
    type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_roles("superadmin")),
):
    if file.content_type not in ALLOWED_TYPES:
        raise AppException(status_code=400, message="Only jpg, jpeg, png images are allowed")

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_doc = FileModel(
        url=f"{settings.BASE_URL}/static/images/{filename}",
        type=type,
        created_by=current_user["id"],
        created_at=datetime.now(timezone.utc),
    )
    collection = mongodb.db["files"]
    await collection.insert_one(file_doc.model_dump(by_alias=True))

    return FileRes(
        id=file_doc.id,
        url=file_doc.url,
        type=file_doc.type,
        created_by=file_doc.created_by,
        created_at=file_doc.created_at,
    )
