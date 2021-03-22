"""
Endpoint routers for images.
"""
from fastapi import APIRouter, File, UploadFile
from models import images as models
from docs import images as docs
from typing import List
import util.images as utils

router = APIRouter()


@router.post('/images/upload',
        response_model=models.ImageUploadResponse,
        description=docs.image_upload_desc,
        summary=docs.image_upload_summ,
        tags=["images"],
        status_code=201)
async def upload_file(
        files: List[UploadFile] = File(...)
        ):
        return True
