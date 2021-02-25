# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
"""
Holds models for the users in the database.

Should easily extend into a two-user-type system where
the admin data is different from the regular user data.
"""
from typing import Dict, Any
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


class ValidateUserForm(BaseModel):
    """
    Contains username and password to validate against database
    """
    identifier: UserIdentifier
    password: str


class ValidateLoginResponse(BaseModel):
    """
    Response for a user login attempt
    """
    jwt: str
