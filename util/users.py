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
    Returns a User object by it's given identifier. UserNotFoundException returns 404 if no user is found.
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


async def attempt_user_login(
        login_form: user_models.UserLoginForm) -> user_models.UserLoginResponse:
    """
    Validates user login attempt based off identifier and password.
    Will raise 404 UserNotFoundException if user does not exist, or
    422 InvalidPasswordException if the user does exist but password is invalid.
    """
    user = await get_user_info_by_identifier(login_form.identifier)
    password_matches = await check_user_password_matches(login_form, user)
    if password_matches:
        login_response = user_models.UserLoginResponse()
        login_response.jwt = await get_auth_token_from_user_data(user)
        return login_response
    else:
        raise exceptions.InvalidPasswordException


"""
-route/users.py should return a UserLoginResponse.  DONE    
-Make the exception and THEN wait to implement correct one. DONE
-routes/users.py needs to throw an appropriate response. Check Felipes notes, throw 404. DONE

-write tests. TO-DO


Questions
PR notes

-I totally forgot to ask you about async in our last meeting. I'd like to have a realtime discussion with you about that, but until then... Do I just make all my functions async? That seems to be what is going on in the file I'm working on. Anyways, I'll submit them one way or another. Keep an eye out for that though, since I'm really just slapping it on there without knowing what it does. Let's discuss more on Wednesday though, I've put in plenty of time but don't understand the advantage still.

-user_data vs user vs user_info for variable name of a User object. Obviously I should normalize these, but which one? If it's up to me, I'd go with user. But I thought I'd check, since you gave example code that used user_data and (I think) user_info... Is a User object even the correct thing to pass in all of these situations? Again, that's what I'd do, but I'm a noob. Specifically looking in util/users/attempt_user_login, util/users/check_user_password_matches, and util/users/get_auth_token_from_user_data

-Clean up all my comments before PR, do github comments instead
"""


# todo: change this to actually compare with hashed password in user_info once we have the field in our user class
async def check_user_password_matches(login_form: user_models.UserLoginForm,
                                user_info: user_models.User) -> bool:
    return login_form.password == 'password123'


# todo: change this to return a Token once we have made the class
async def get_auth_token_from_user_data(
        user: user_models.User) -> str:
    login_response = 'a jwt!'
    return login_response
