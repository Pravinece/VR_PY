import uuid
import os
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.core.exception import AppException
from app.core.config import settings
from app.core.db import mongodb
from app.models.userModel import FileModel
from app.schema.uploadSchema import FileRes
from app.schema.questionSchema import AudioKeyEnum
from app.core.security import require_roles

router = APIRouter()

IMAGES_DIR = os.path.join(settings.UPLOAD_DIR, "images")
AUDIO_DIR = os.path.join(settings.UPLOAD_DIR, "audio")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp3"}

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)


@router.post("/upload/image", response_model=FileRes)
async def upload_image(
    type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_roles("superadmin")),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise AppException(status_code=400, message="Only jpg, jpeg, png images are allowed")

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(IMAGES_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_doc = FileModel(
        url=f"/tiaa/static/images/{filename}",
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


@router.post("/upload/audio/{question_id}")
async def upload_question_audio(
    question_id: str,
    key: AudioKeyEnum = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_roles("superadmin")),
):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise AppException(status_code=400, message="Only mp3, wav, ogg audio files are allowed")

    collection = mongodb.db["questions"]
    question = await collection.find_one({"_id": question_id})
    if not question:
        raise AppException(status_code=404, message="Question not found")

    if question.get(key.value):
        raise AppException(status_code=400, message=f"{key.value} already exists. Use the replace API to update it.")

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(AUDIO_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    audio_url = f"/tiaa/static/audio/{filename}"
    await collection.update_one(
        {"_id": question_id},
        {"$set": {key.value: audio_url, "updated_at": datetime.now(timezone.utc)}}
    )

    return {"success": True, "message": f"{key.value} uploaded successfully", "url": audio_url}


@router.patch("/upload/audio/{question_id}")
async def replace_question_audio(
    question_id: str,
    key: AudioKeyEnum = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_roles("superadmin")),
):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise AppException(status_code=400, message="Only mp3, wav, ogg audio files are allowed")

    collection = mongodb.db["questions"]
    question = await collection.find_one({"_id": question_id})
    if not question:
        raise AppException(status_code=404, message="Question not found")

    # delete old file from disk
    old_url = question.get(key.value)
    if old_url:
        old_filename = old_url.split("/")[-1]
        old_file_path = os.path.join(AUDIO_DIR, old_filename)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(AUDIO_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    audio_url = f"{settings.BASE_URL}/static/audio/{filename}"
    await collection.update_one(
        {"_id": question_id},
        {"$set": {key.value: audio_url, "updated_at": datetime.now(timezone.utc)}}
    )

    return {"success": True, "message": f"{key.value} replaced successfully", "url": audio_url}
