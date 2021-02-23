"""
Holds handling functions for user operations.

Uses a floating instance of the database client that is instanciated in
the `config.db` module like all other `util` modules.
"""
from config.db import get_database, get_database_client_name
from models import exceptions
import models.users as user_models


# instanciate the main collection to use for this util file for convenience
def users_collection():
    return get_database()[get_database_client_name()]["users"]


async def register_user(
        form: user_models.UserRegistrationForm) -> user_models.UserId:
    """
    Register a user registration form to the database and return it's user ID.
    """
    # cast input form (python class) -> dictionary (become JSON eventually)
    form_dict = form.dict()

    # insert id into column
    users_collection().insert_one(form_dict)

    # return user_id if success
    return form_dict["_id"]


async def get_user_info_by_identifier(
        identifier: user_models.UserIdentifier) -> user_models.User:
    """
    Returns a User object by it's given identifier.
    """
    query = identifier.get_database_query()

    #query to database
    user_document = users_collection().find_one(query)

    if not user_document:
        raise exceptions.UserNotFoundException

    # cast the database response into a User object
    return user_models.User(**user_document)


async def delete_user(identifier: user_models.UserIdentifier) -> None:
    """
    Deletes a user by it's identifier
    """
    query = identifier.get_database_query()
    response = users_collection().delete_one(query)
    if response.deleted_count == 0:
        detail = "User not found and could not be deleted"
        raise exceptions.UserNotFoundException(detail=detail)
