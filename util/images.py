"""
Handlers for image operations.
"""
import io
from PIL import Image
import gridfs
from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
from models import exceptions
from config.db import get_database, get_database_client_name

# instantiate the main collection to use for this util file for convenience
db = get_database()[get_database_client_name()]
images_collection = db["images"]

fs = gridfs.GridFS(db)


async def image_upload(upload_file: UploadFile) -> str:
    """
    Validates and uploads the file data within the upload file
    into GridFS, returning the UUID.
    """
    await validate_incoming_file_data(upload_file)
    file_data = upload_file.file

    image_id = str(fs.put(file_data))
    meta = {'image id': image_id}
    images_collection.insert_one(meta)
    return image_id


async def validate_incoming_file_data(file: UploadFile) -> None:
    """
    Does some simple data validation on the incoming file data,
    trying to assert that it is a valid image.

    Raises the appropriate error if invalid, or returning
    None if valid.
    """
    await check_file_data_is_valid_image(file)


async def check_file_data_is_valid_image(file: UploadFile) -> None:
    """
    Uses PIL to verify the integrity of the image data.
    Raises exceptions if invalid, else returns none.
    """
    image_byte_data = io.BytesIO(await file.read())
    try:
        image_to_verify = Image.open(image_byte_data)
        image_to_verify.verify()
    except Exception as image_verification_error:
        detail = f"Invalid or unreadable image data: {image_verification_error}"
        raise exceptions.InvalidDataException(
            detail=detail) from image_verification_error


async def get_image(key: str):
    return fs.get(key)
