from pymongo import MongoClient
from config.db import get_database, get_database_client_name
from fastapi import File, UploadFile
from typing import List
import gridfs

# instantiate the main collection to use for this util file for convenience

db = get_database()[get_database_client_name()]
images_collection = db["images"]

fs = gridfs.GridFS(db)


async def image_upload(files: List[UploadFile] = File (...)):
    for file in files:
        image = fs.put(files)


async def get_image(key: str):
    return fs.get(key)