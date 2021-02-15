"""
Holds models for the users in the database.

Should easily extend into a two-user-type system where
the admin data is different from the regular user data.
"""
from pydantic import EmailStr, BaseModel


class Users(BaseModel):
    """
    Main top-level user model. Should hold only enough data to be useful,
    as any more can become painful to deal with due to privacy etc.
    """
    first_name: str
    last_name: str
    email: EmailStr


# pylint: disable=invalid-name
class registration_form(Users):
    """
    Client-facing user registration form.
    """


class registration_response(BaseModel):
    """
    Response for a successful user registration.
    """
    user_id: str


class get_user_info_response(Users):
    """
    Response for a user data query, which should be all
    of the user's public-facing information.
    """
