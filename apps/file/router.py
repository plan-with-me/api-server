from fastapi import APIRouter, Depends, Request, status, HTTPException, UploadFile
from tortoise.transactions import atomic
import aiofiles

from core.dependencies import Auth
from apps.file.model import File
from apps.file.dto import FileResponse


BASE_NAS_LOC = "/nas"
BASE_CLIENT_LOC = "/static"

router = APIRouter(
    prefix="/files",
    tags=["File"],
    dependencies=[Depends(Auth())],
)


@router.post(
    path="",
    response_model=FileResponse,
    description="""
    파일 업로드 API입니다.
    """
)
@atomic()
async def upload_file(request: Request, file: UploadFile):
    ext = file.filename.split(".")[-1]
    file_model = await File.create(
        original_filename=file.filename,
        user_id=request.state.token_payload["id"],
    )
    async with aiofiles.open(f"/{BASE_NAS_LOC}/{file_model.id}.{ext}", mode="wb") as f:
        while content := await file.read(1024):
            await f.write(content)
        file_model.saved_location = f"{BASE_NAS_LOC}/{file_model.id}.{ext}"
        file_model.client_location = f"{BASE_CLIENT_LOC}/{file_model.id}.{ext}"
        await file_model.save()
    return file_model
