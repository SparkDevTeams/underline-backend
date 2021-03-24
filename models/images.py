"""
Holds models for image operations
"""
from pydantic import BaseModel

ImageId = str


class ImageUploadResponse(BaseModel):
    image_id: ImageId
