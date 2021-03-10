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
        user_reg_form: user_models.UserRegistrationForm) -> user_models.UserId:
    """
    Register a user registration form to the database and return it's user ID.
    """
    pre_hash_user_password = user_reg_form.password
    user_reg_form.set_password(pre_hash_user_password)
    # cast input form (python class) -> dictionary (become JSON eventually)
    form_dict = user_reg_form.dict()

    # insert id into column
    users_collection().insert_one(form_dict)

    # return user_id if success
    return form_dict["_id"]


async def get_user_info_by_identifier(
        identifier: user_models.UserIdentifier) -> user_models.User:
    """
    Returns a User object by it's given identifier.
    UserNotFoundException returns 404 if no user is found.
    """
    query = identifier.get_database_query()

    # query to database
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


async def login_user(
        login_form: user_models.UserLoginForm
) -> user_models.UserLoginResponse:
    """
    Validates user login attempt based off
    identifier and password. Will raise
    404 UserNotFoundException if user does
    not exist, or 422 InvalidPasswordException
    if the user does exist but password is invalid.
    """
    user = await get_user_info_by_identifier(login_form.identifier)
    password_matches = await check_user_password_matches(login_form, user)
    if password_matches:
        auth_token = await get_auth_token_from_user_data(user)
        login_response = user_models.UserLoginResponse(jwt=auth_token)
        return login_response
    raise exceptions.InvalidPasswordException


async def check_user_password_matches(login_form: user_models.UserLoginForm,
                                      user: user_models.User) -> bool:
    return user.check_password(login_form.password)


# fixme: change this to return a Token once we have made the class
async def get_auth_token_from_user_data(_user: user_models.User) -> str:
    login_response = 'a jwt!'
    return login_response


async def update_user(user: user_models.U) -> str:
