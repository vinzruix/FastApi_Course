import os
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from starlette import status

from app.services.file_storage import save_image

router = APIRouter(prefix="/upload", tags=["uploads"])

@router.post("/bytes")
async def upload_bytes(file: bytes = File(...)): # Carga en RAM (para archivos pequeños)
    return {
        "file_name":"archivo subido",
        "size_bytes":len(file)
    }


@router.post("/file")
async def upload_file(file : UploadFile = File(...)): # Carga en disco (para archivos grandes)
    return {
        "filename": file.filename,
        "size_file": file.content_type

    }

@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    return await save_image(file)

























