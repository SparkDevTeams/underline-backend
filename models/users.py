# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
# pylint: disable=no-name-in-module; see https://github.com/samuelcolvin/pydantic/issues/1961
"""
Holds models for the users in the database.

Should easily extend into a two-user-type system where
the admin data is different from the regular user data.
"""
from enum import auto
from typing import Dict

import bcrypt
from pydantic import EmailStr, BaseModel

import models.commons as model_commons

# type alias for UserID
UserId = str


class UserTypeEnum(model_commons.AutoName):
    PUBLIC_USER = auto()
    ADMIN = auto()


class User(model_commons.ExtendedBaseModel):
    """
    Main top-level user model. Should hold only enough data to be useful,
    as any more can become painful to deal with due to privacy etc.
    """
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    def set_password(self, new_password: str) -> None:
        """
        Sets a hashed password for user using bcrypt
        """
        encoded_new_pass = new_password.encode('utf-8')

        hashed_pass = bcrypt.hashpw(encoded_new_pass, bcrypt.gensalt())
        self.password = str(hashed_pass)

    def check_password(self, password_to_check: str) -> bool:
        """
        Checks if value matches the user's password and returns a boolean
        """
        pass_to_check = password_to_check.encode('utf-8')
        user_pass = self.password.encode('utf-8')

        # XXX: awful code! get rid of asap!
        if isinstance(self.password, str):
            user_pass = self.password[2:-1].encode('utf-8')
        passwords_match = bcrypt.checkpw(pass_to_check, user_pass)
        return passwords_match


class UserRegistrationForm(User):
    """
    Client-facing user registration form.
    """


class UserRegistrationResponse(BaseModel):
    """
    Response for a successful user registration.
    """
    user_id: str


class UserIdentifier(BaseModel):
    """
    Used for whenever we need to identify a user by a piece of data.

    This gives us a lot more freedom in how we actually implement things like
    queries, as well as login/signup ops.
    """
    email: EmailStr

    def get_database_query(self) -> Dict[str, str]:
        """
        Returns a query dict that always has at least one valid identifier.
        """
        return {"email": self.email}


class UserInfoQueryResponse(User):
    """
    Response for a user data query, which should be all
    of the user's public-facing information.
    """


class UserLoginForm(BaseModel):
    """
    Contains username and password to validate against database
    """
    identifier: UserIdentifier
    password: str


class UserLoginResponse(BaseModel):
    """
    Response for a user login attempt
    fixme: should be a Token when class becomes available
    """
    jwt: str
