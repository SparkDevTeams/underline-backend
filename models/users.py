"""
Holds models for the users in the database.

Should easily extend into a two-user-type system where
the admin data is different from the regular user data.
"""
from typing import Dict
from pydantic import EmailStr, BaseModel

# type alias for UserID
UserId = str


class User(BaseModel):
    """
    Main top-level user model. Should hold only enough data to be useful,
    as any more can become painful to deal with due to privacy etc.
    """
    first_name: str
    last_name: str
    email: EmailStr


class UserRegistrationRequest(User):
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
