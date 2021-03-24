"""
Holds models for image operations
"""
from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    image_id: str


class ImageQueryResponse(BaseModel):
    image_data: bytes
