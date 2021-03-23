"""
Handlers for image operations.
"""
import PIL
import gridfs
from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
from models import exceptions
from config.db import get_database, get_database_client_name

# instantiate the main collection to use for this util file for convenience
db = get_database()[get_database_client_name()]
images_collection = db["images"]

fs = gridfs.GridFS(db)


async def image_upload(upload_file: UploadFile):
    """
    Validates and uploads the file data within the upload file
    into GridFS, returning the UUID.
    """
    await validate_incoming_file_data(upload_file)
    file_data = upload_file.file

    image_id = fs.put(image)
    image_id_str = str(image_id)
    meta = {'image id': image_id_str}
    images_collection.insert_one(meta)
    return image_id_str


async def validate_incoming_file_data(file: UploadFile) -> None:
    """
    Does some simple data validation on the incoming file data,
    trying to assert that it is a valid image.

    Raises the appropriate error if invalid, or returning
    None if valid.
    """
    await check_filename_is_valid(file.filename)
    await check_file_data_is_valid_image(file.file)


async def check_filename_is_valid(filename: str) -> None:
    """
    Checks if the filename is of valid extension, raising
    an exception if not.
    """
    allowed_file_extensions = ("png", "jpeg", "jpg")
    filename_valid = filename.endswith(allowed_file_extensions)
    breakpoint()

    if not filename_valid:
        detail = "Filename invalid. Must be .jpg, .jpeg, or .png"
        raise exceptions.InvalidDataException(detail=detail)


async def check_file_data_is_valid_image(file: SpooledTemporaryFile) -> None:
    """
    Uses PIL to verify the integrity of the image data.
    Raises exceptions if invalid, else returns none.
    """
    image_byte_data = await file.read()
    try:
        image_to_verify = pil.Image.open(image_byte_data)
        image_to_verify.verify()
    except Exception as image_verification_error:
        detail = "Invalid or unreadable image data"
        raise exceptions.InvalidDataException(
            detail=detail) from image_verification_error


async def get_image(key: str):
    return fs.get(key)
