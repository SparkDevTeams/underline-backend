"""
Holds handling functions for user operations.

Uses a floating instance of the database client that is instanciated in
the `config.db` module like all other `util` modules.
"""
from typing import Dict, Any, List

import pymongo.errors as pymongo_exceptions

from models import exceptions
import models.users as user_models
import models.commons as common_models
from models.auth import Token

from config.db import get_database, get_database_client_name
import util.events as event_utils


# instantiate the main collection to use for this util file for convenience
def users_collection():
    return get_database()[get_database_client_name()]["users"]


async def register_user(
        user_reg_form: user_models.UserRegistrationForm
) -> user_models.UserAuthenticationResponse:
    """
    Register a user registration form to the database and return it's user ID.
    """
    user_object = await get_valid_user_from_reg_form(user_reg_form)

    # insert id into column
    try:
        users_collection().insert_one(user_object.dict())
    except pymongo_exceptions.DuplicateKeyError as dupe_error:
        detail = "Invalid user insertion: duplicate email"
        raise exceptions.DuplicateDataException(detail=detail) from dupe_error

    # return user_id if success
    user_id = user_object.get_id()
    return user_id


async def get_valid_user_from_reg_form(
        user_reg_form: user_models.UserRegistrationForm) -> user_models.User:
    """
    Casts an incoming user registration form into a `User` object,
    effectively validating the user, and setting the password.
    """
    user_type = user_reg_form.get_user_type()
    user_object = user_models.User(**user_reg_form.dict(), user_type=user_type)

    pre_hash_user_password = user_reg_form.password
    user_object.set_password(pre_hash_user_password)

    return user_object


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


async def check_if_user_exists_by_id(user_id: common_models.UserId) -> None:
    """
    Checks if the user exists solely by ID and raises an
    exception if it does, else returns None silently.
    """
    user_identifier = user_models.UserIdentifier(user_id=user_id)
    await get_user_info_by_identifier(user_identifier)


async def delete_user(identifier: user_models.UserIdentifier) -> None:
    """
    Deletes a user by it's identifier.

    Raises an error if the user does not exist or if the credentials
    don't match the identifier
    """

    query = identifier.get_database_query()
    response = users_collection().delete_one(query)
    if response.deleted_count == 0:
        detail = "User not found and could not be deleted"
        raise exceptions.UserNotFoundException(detail=detail)


async def login_user(
        login_form: user_models.UserLoginForm
) -> user_models.UserAuthenticationResponse:
    """
    Validates user login attempt based off
    identifier and password.

    Will raise 404 UserNotFoundException if user does
    not exist, or 422 InvalidPasswordException
    if the user does exist but password is invalid.
    """
    user = await get_user_info_by_identifier(login_form.identifier)

    password_matches = await check_user_password_matches(login_form, user)
    if not password_matches:
        raise exceptions.InvalidPasswordException

    auth_token = await get_auth_token_from_user_data(user)
    login_response = user_models.UserAuthenticationResponse(jwt=auth_token)
    return login_response


async def check_user_password_matches(login_form: user_models.UserLoginForm,
                                      user: user_models.User) -> bool:
    """
    Compares the password of the user loging form and the user object,
    returning the boolean outcome.
    """
    return user.check_password(login_form.password)


async def update_user(
        user_update_form: user_models.UserUpdateForm
) -> user_models.UserUpdateResponse:
    """
    Updates user entries in database if UserUpdateForm fields are valid.
    """
    user = await get_user_info_by_identifier(user_update_form.identifier)

    await update_user_data_database(user, user_update_form)

    return user_models.UserUpdateResponse(user_id=user.get_id())


async def update_user_data_database(
        user: user_models.User,
        user_update_form: user_models.UserUpdateForm) -> None:
    """
    Updates user data within database,
    based off fields specified in UserUpdateForm
    """

    if user_update_form.dict().get("password"):
        await set_update_form_pass_to_hashed(user, user_update_form)

    values_to_update = await get_dict_of_values_to_update(user_update_form)
    update_dict = await format_update_dict(values_to_update)

    identifier_dict = user_update_form.identifier.get_database_query()
    users_collection().update_one(identifier_dict, update_dict)


async def set_update_form_pass_to_hashed(
        user: user_models.User,
        user_update_form: user_models.UserUpdateForm) -> None:
    """
    Takes a given user and Update form and hashes
    the update form password accordingly
    fixme: This is ugly code.
    """
    unhashed_pass = user_update_form.dict().get("password")
    user.set_password(unhashed_pass)
    user_update_form.password = user.dict().get("password")


async def format_update_dict(
        values_to_update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats a dict of data so it can be passed into a PyMongo update function
    """
    return {"$set": values_to_update}


async def get_dict_of_values_to_update(
        update_form: user_models.UserUpdateForm) -> Dict[str, Any]:
    """
    Given a `UserUpdateForm`, returns a dict with all of the values
    to be updated with a `dict.update()` call to the original user data dict.
    """
    form_dict_items = update_form.dict().items()

    # could be simplified to be just `v` but this makes our intent crystal clear
    valid_value = lambda v: v is not None

    forbidden_keys_set = {"identifier"}
    valid_key = lambda k: k not in forbidden_keys_set

    values_to_update_dict = {
        key: value
        for key, value in form_dict_items
        if valid_key(key) and valid_value(value)
    }

    return values_to_update_dict


async def get_auth_token_from_user_data(user: user_models.User) -> str:
    """
    Given a User object, returns an encoded JWT string with the
    user's identifier data (UserID) in it's payload.
    """
    user_id = user.get_id()
    encoded_jwt_str = await get_auth_token_from_user_id(user_id)
    return encoded_jwt_str


async def get_auth_token_from_user_id(user_id: common_models.UserId) -> str:
    """
    Returns an encoded token string with the given user_id in it's payload.
    """
    payload_dict = {'user_id': user_id}
    encoded_jwt_str = Token.get_enc_token_str_from_dict(payload_dict)
    return encoded_jwt_str


async def get_events_from_user_identifier(
        identifier: user_models.UserIdentifier) -> List[common_models.EventId]:
    """
    Gets list of all v
    """
    identifier_dict = identifier.get_database_query()
    user_dict = users_collection().find_one(identifier_dict)
    return user_dict["events_visible"]


async def user_add_event(add_event_form: user_models.UserAddEventForm,
                         user_id: user_models.UserId
                         ) -> user_models.UserAddEventResponse:
    """
    Adds an event to a validated User's events_visible field
    """

    # at this point token is already validated
    event_id = add_event_form.event_id
    var = "hi"

    # this exists just to validate that event is in database
    await event_utils.get_event_by_id(event_id)

    user_identifier = user_models.UserIdentifier(user_id=user_id)
    identifier_dict = user_identifier.get_database_query()
    if event_id not in await get_events_from_user_identifier(
            user_identifier):
        users_collection().update_one(
            identifier_dict,
            {
                "$push":
                    {"events_visible": event_id
                     }
            }
        )
    else:
        raise exceptions.DuplicateDataException(
            "Event already in user's events_visible field")

    return user_models.UserAddEventResponse(event_id=event_id)
