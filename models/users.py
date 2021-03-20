# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
# pylint: disable=no-name-in-module; see https://github.com/samuelcolvin/pydantic/issues/1961
# pylint: disable=unsubscriptable-object
#       - pylint bug with optional
"""
Holds models for admin-only operations and users.
"""

from enum import auto
from typing import Dict, Optional

import bcrypt
from pydantic import EmailStr, BaseModel, root_validator, validator

import models.commons as model_commons

# type alias for UserID
UserId = str


# async or no? Asserts correct way to do this?
def validate_name(name: str) -> str:
    if not 2 <= len(name) <= 36:
        raise ValueError("Invalid name length. 2 chars min, 36 chars max")
    if not name.isalpha():
        raise ValueError("First and last name should "
                         "consist only of alphabetical characters")

    return name


def validate_password(password: str) -> str:
    if not 6 <= len(password) <= 15:
        print(password)
        print(len(password))
        raise ValueError("Invalid password length. 6 chars min, 15 chars max")

    return password


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
    user_type: UserTypeEnum



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


class UserRegistrationForm(BaseModel):
    """
    Client-facing user registration form.

    Only carries the necessary client-facing data, hiding the `User` internals.
    """
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    # validators
    _validate_first_name = validator(
        "first_name", allow_reuse=True)(validate_name)
    _validate_last_name = validator(
        "last_name", allow_reuse=True)(validate_name)
    _validate_password = validator(
        "password", allow_reuse=True)(validate_password)
    def get_user_type(self) -> UserTypeEnum:
        """
        Returns the type enum for a regular user.
        """
        return UserTypeEnum.PUBLIC_USER


class AdminUserRegistrationForm(UserRegistrationForm):
    """
    Admin-only user registration form.

    Inherits from the base `UserRegistrationForm`, but overrides the
    method that returns user type, allowing for decently strong polymorphic
    calls in utils.
    """
    def get_user_type(self) -> UserTypeEnum:
        """
        Returns the type enum for an admin user.
        """
        return UserTypeEnum.ADMIN


class UserIdentifier(BaseModel):
    """
    Used for whenever we need to identify a user by a piece of data.

    This gives us a lot more freedom in how we actually implement things like
    queries, as well as login/signup ops.
    """
    email: Optional[EmailStr] = None
    user_id: Optional[UserId] = None

    @root_validator()
    def check_at_least_one_identifier(cls, values):
        """
        Since the identifiers are typed as Optionals, we need to make sure
        that at _least_ one form of identification is passed in.
        """
        has_non_null_entries = any(values.values())

        if has_non_null_entries:
            return values

        message = "At least one type of identifier must be specified."
        raise ValueError(message)

    def get_database_query(self) -> Dict[str, str]:
        """
        Generates a valid database query dict from the instance's information.
        """
        self_key_val_pairs = self.dict().items()

        # only use non-null values for identifier
        query_dict = {key: val for key, val in self_key_val_pairs if val}

        # mongo uses `_id` for it's uuid field
        if "user_id" in query_dict:
            query_dict["_id"] = query_dict.pop("user_id")

        return query_dict


class UserInfoQueryResponse(BaseModel):
    """
    Response for a user data query, which should be all
    of the user's public-facing information.
    """
    first_name: str
    last_name: str
    email: EmailStr


class UserLoginForm(BaseModel):
    """
    Contains username and password to validate against database
    """
    identifier: UserIdentifier
    password: str


class UserAuthenticationResponse(BaseModel):
    """
    Response for authentication of user
    """
    jwt: str


class UserUpdateForm(BaseModel):
    """
    Contains optional user fields to update
    """
    identifier: UserIdentifier
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

    # validators
    _validate_first_name = validator(
        "first_name", allow_reuse=True)(validate_name)
    _validate_last_name = validator(
        "last_name", allow_reuse=True)(validate_name)
    _validate_password = validator(
        "password", allow_reuse=True)(validate_password)


class UserUpdateResponse(BaseModel):
    """
    Response for a user update attempt
    """
    user_id: UserId


class AdminUserInfoQueryResponse(BaseModel):
    """
    Holds info to be returned for a admin user data query
    """
    email: EmailStr
