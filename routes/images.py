"""
Endpoint routers for Images.
"""
from typing import List
from fastapi import APIRouter, File, UploadFile
from models import images as models
from docs import images as docs
import util.images as utils

router = APIRouter()

@router.post('/images/upload',
             response_model=models.ImageUploadResponse,
             description=docs.image_upload_desc,
             summary=docs.image_upload_summ,
             tags=["Images"],
             status_code=201)
async def upload_file(files: List[UploadFile] = File(...)):
    image = await utils.image_upload(files)
    return models.UserAuthenticationResponse(image_id=image)
