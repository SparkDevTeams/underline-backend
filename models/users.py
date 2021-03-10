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
from typing import Dict, Any, Optional

import bcrypt
from pydantic import EmailStr, BaseModel, Field, validator

import models.commons as model_commons

# type alias for UserID
UserId = str


class User(BaseModel):
    """
    Main top-level user model. Should hold only enough data to be useful,
    as any more can become painful to deal with due to privacy etc.
    """
    # alias needed for validator access
    id: UserId = Field("", alias="_id")  # pylint: disable=invalid-name
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

    @validator("id", pre=True, always=True)
    def set_id(cls, value) -> str:
        """
        Workaround on dynamic default setting for UUID.
        From: https://github.com/samuelcolvin/pydantic/issues/866
        """
        return value or model_commons.generate_uuid4_str()

    def get_id(self) -> UserId:
        """
        Returns the instance's database id
        """
        return self.id

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Override the base `dict` method in order to get the mongo ID fix
        """
        parent_dict = super().dict(*args, **kwargs)
        parent_dict["_id"] = self.get_id()
        return parent_dict


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





"""
Option 1 
class UserUpdateForm(User):
    user_id: UserIdentifier
"""


"""
Option 2
Note: what is difference between first_name = none and first name: Optional[str]. Just type enforcement in latter?
class UserUpdateForm(BaseModel):
    user_id: UserIdentifier
    # idk if this should be here. How is this dif than Optional[UserIdentifier]?
    new_id: UserId = Field("", alias="_new_id")  # pylint: disable=invalid-name
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
"""

"""
Option 3: Is there a way to make the model inherit from User, but make all fields optional without needing to
explicitly re-declare each one? This would make every field updatable, but prevent the need to refactor both 
fields whenever we change our user model
"""


class UserUpdateResponse(BaseModel):
    """
    Response for a user update attempt
    todo: check if returning user_id as str is redundant or not
    """
    user_id: str
