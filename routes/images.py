"""
Endpoint routers for Images.
"""
import io
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, File, UploadFile, Depends

from docs import images as docs
from util import images as utils
from util import auth as auth_utils
from models import images as models

router = APIRouter()


@router.post('/images/upload',
             response_model=models.ImageUploadResponse,
             description=docs.image_upload_desc,
             summary=docs.image_upload_summ,
             tags=["Images"],
             status_code=201)
async def upload_file(
        file: UploadFile = File(...),
        user_id_from_token: str = Depends(
            auth_utils.get_user_id_from_header_and_check_existence)):
    del user_id_from_token  # unused var
    image_id = await utils.image_upload(file)
    return models.ImageUploadResponse(image_id=image_id)


@router.get('/images/get',
            description=docs.image_query_desc,
            summary=docs.image_query_summ,
            tags=["Images"],
            status_code=200)
async def image_query(image_id: models.ImageId):
    image_data_as_bytes = await utils.get_image_by_id(image_id)
    return StreamingResponse(io.BytesIO(image_data_as_bytes))
