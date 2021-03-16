"""
Holds handling functions for user operations.

Uses a floating instance of the database client that is instanciated in
the `config.db` module like all other `util` modules.
"""
from config.db import get_database, get_database_client_name
from models import exceptions
import models.users as user_models
from models.auth import Token


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
    users_collection().insert_one(user_object.dict())

    # return user_id if success
    user_id = user_object.get_id()
    return user_id


async def get_valid_user_from_reg_form(
        user_reg_form: user_models.UserRegistrationForm) -> user_models.User:
    """
    Casts an incoming user registration form into a `User` object,
    effectively validating the user, and setting the password.
    """
    user_type = user_models.UserTypeEnum.PUBLIC_USER
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
) -> user_models.UserAuthenticationResponse:
    """
    Validates user login attempt based off
    identifier and password. Will raise
    404 UserNotFoundException if user does
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


async def get_auth_token_from_user_data(user: user_models.User) -> str:
    """
    Given a User object, returns an encoded JWT string with the
    user's identifier data (UserID) in it's payload.
    """
    user_id = user.get_id()
    encoded_jwt_str = await get_auth_token_from_user_id(user_id)
    return encoded_jwt_str


async def get_auth_token_from_user_id(user_id: user_models.UserId) -> str:
    """
    Returns an encoded token string with the given user_id in it's payload.
    """
    payload_dict = {'user_id': user_id}
    encoded_jwt_str = Token.get_enc_token_str_from_dict(payload_dict)
    return encoded_jwt_str
