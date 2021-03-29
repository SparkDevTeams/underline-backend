"""
Handlers for image operations.
"""
import io
from uuid import uuid4

import gridfs
import pymongo
from PIL import Image
from fastapi import UploadFile

from models import exceptions
import models.images as image_models
from config.db import get_database, get_database_client_name, get_grid_fs_client


def images_collection() -> pymongo.collection.Collection:
    """
    Function-based replacement for accessing the database collection for images

    Returns the image collection on the current database.
    """
    return get_database()[get_database_client_name()]["images"]


def grid_fs_client() -> gridfs.GridFS:
    """
    Facade over the main database call to get the global
    `GridFS` client instance.
    """
    return get_grid_fs_client()


async def get_image_by_id(image_id: image_models.ImageId) -> bytes:
    """
    Retrieves the given image from the database and returns it as binary data
    if it exists, else raises 404.
    """
    file = grid_fs_client().find_one(image_id)

    if not file:
        raise exceptions.ImageNotFoundException

    return file.read()


async def image_upload(upload_file: UploadFile) -> image_models.ImageId:
    """
    Validates and uploads the file data within the upload file
    into GridFS, returning the UUID.
    """
    await validate_incoming_file_data(upload_file)
    file_data = upload_file.file

    image_id = str(uuid4())
    grid_fs_client().put(file_data, _id=image_id)

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

    # reset cursor position post-read
    await file.seek(0)

    try:
        image_to_verify = Image.open(image_byte_data)
        image_to_verify.verify()
    except Exception as image_verification_error:
        detail = f"Invalid or unreadable image data: {image_verification_error}"
        raise exceptions.InvalidDataException(
            detail=detail) from image_verification_error
