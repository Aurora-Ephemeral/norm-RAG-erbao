from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.api.dependencies import get_file_service
from app.service.FileService import FileService

router = APIRouter(prefix="/file", tags=["file"])

@router.post("/upload/{knowledge_base_id}")
async def upload_file(
    knowledge_base_id: int, 
    file: UploadFile = File(...),
    file_name: str = Form(...),
    part_type: Optional[str] = Form(default=None),
    standard_no: Optional[str] = Form(default=None),
    service: FileService = Depends(get_file_service)
):
    await service.upload_file(
        file=file,
        knowledge_base_id=knowledge_base_id,
        file_name=file_name,
        part_type=part_type,
        standard_no=standard_no
    )