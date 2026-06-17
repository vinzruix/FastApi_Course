import shutil
import uuid
from fastapi import File, UploadFile, HTTPException
from starlette import status
import os



MEDIA_DIR = "media"
ALLOW_MIME = ["image/png", "image/jpeg"]
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB","10"))
CHUNKS = 1024*1024


def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR,exist_ok=True)


async def save_image(file: UploadFile = File(...)) -> dict:
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo se permite imagenes jpg y png")

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer, length=CHUNKS)

    size = os.path.getsize(file_path)

    if size > MAX_UPLOAD_MB * 1024 * 1024:
        os.remove(file_path)
        HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE,detail="Archivo demasiado grande")

    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"media/{filename}"
    }
