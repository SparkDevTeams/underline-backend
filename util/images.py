"""
Handlers for image operations.
"""
from fastapi import File, UploadFile
import gridfs
from config.db import get_database, get_database_client_name

# instantiate the main collection to use for this util file for convenience

db = get_database()[get_database_client_name()]
images_collection = db["images"]

fs = gridfs.GridFS(db)


async def image_upload(file: UploadFile = File (...)):
    image = file.file
    image_id = fs.put(image)
    image_id_str = str(image_id)
    meta = {
       'image id' : image_id_str
    }
    images_collection.insert_one(meta)
    return image_id_str


async def get_image(key: str):
    return fs.get(key)
