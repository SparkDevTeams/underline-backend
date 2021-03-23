"""
Endpoint routers for Images.
"""
from fastapi import APIRouter, File, UploadFile

from docs import images as docs
from util import images as utils
from models import images as models

router = APIRouter()


@router.post('/images/upload',
             response_model=models.ImageUploadResponse,
             description=docs.image_upload_desc,
             summary=docs.image_upload_summ,
             tags=["Images"],
             status_code=201)
async def upload_file(file: UploadFile = File(...)):
    image = await utils.image_upload(file)
    return models.ImageUploadResponse(image_id=image)
