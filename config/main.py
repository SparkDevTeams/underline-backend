"""
Holds global config settings for the whole runtime.

Mostly made up of environment config variables.
Also instanciates the `FastAPI()` router instance.
"""
import os
from fastapi import FastAPI

app = FastAPI()

DB_URI = os.environ.get("MONGO_DB_URI")
if not DB_URI:
    raise Exception("Key Error: DB_URI not set!")

JWT_SECRET_KEY = "00cb508e977fd82f27bf05e321f596b63bf2d" \
        "9f2452829e787529a52e64e7439"
JWT_EXPIRY_TIME = 30
