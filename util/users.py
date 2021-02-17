"""
Holds handling functions for user operations.

Uses a floating instance of the database client that is instanciated in
the `config.db` module like all other `util` modules.
"""
import uuid
from starlette.exceptions import HTTPException
from config.db import get_database
import logging
from config.db import get_database_client_name

# instanciate the main collection to use for this util file for convenience
users_collection = get_database()[get_database_client_name()]["users"]


async def generate_id():
    return str(uuid.uuid4())


async def register_user(form):
    # cast input form (python class) -> dictionary (become JSON eventually)
    form_dict = form.dict()

    # generating user_id (UUID)
    user_id = await generate_id()

    # insert the user_id to the dictionary for insertion
    form_dict["_id"] = user_id

    # insert id into column
    users_collection.insert_one(form_dict)

    # return user_id if success
    return user_id


async def get_user_info(email):

    #make query from identifier input
    query = {"email": email}

    #query to database
    response = users_collection.find_one(query)

    if not response:
        raise HTTPException(status_code=404, detail="User does not exist")

    return response


async def delete_user(email):

    # create column for insertion in database_client

    response = users_collection.delete_one({"email": email})
    if response.deleted_count == 0:
        raise HTTPException(status_code=404,
                            detail="User not found and could not be deleted")


# Returns user dictionary
async def get_user(user_id):
    user = users_collection.find_one({"_id": user_id})
    return user
