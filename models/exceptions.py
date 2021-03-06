# pylint: disable=unsubscriptable-object
#       - pylint bug with optional
"""
Holds all of the common exceptions that get re-raised as HTTPExceptions.

Should all come with a pre-set message that can be overriden.
"""

from typing import Optional
from starlette.exceptions import HTTPException


class EventNotFoundException(HTTPException):
    """
    Default exception for a 404 on events.
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Event not found with given ID"
        super().__init__(status_code=404, detail=detail)


class UserNotFoundException(HTTPException):
    """
    Default exception for a 404 on users.
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "User not found with given identifier"
        super().__init__(status_code=404, detail=detail)


class ImageNotFoundException(HTTPException):
    """
    Default exception for a 404 on images.
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Image not found with given image ID"
        super().__init__(status_code=404, detail=detail)


class DuplicateDataException(HTTPException):
    """
    Default exception for duplicate data
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Cannot complete request: duplicate data detected"
        super().__init__(status_code=409, detail=detail)


class FeedbackNotFoundException(HTTPException):
    """
    Default exception for a 404 on a feedback per event.
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Feedback ID not found in the provided event"
        super().__init__(status_code=404, detail=detail)


class InvalidDataException(HTTPException):
    """
    Default for invalid entry data that raises a 422
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Invalid data provided"
        super().__init__(status_code=422, detail=detail)


class InvalidPasswordException(HTTPException):
    """
    Thrown when an invalid password is given.
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = 'User registered, but invalid password provided'
        super().__init__(status_code=422, detail=detail)


class InvalidAuthHeaderException(HTTPException):
    """
    Default for empty header which expects a JWT string
    that raises a 401
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Invalid authorization token in header"
        super().__init__(status_code=401, detail=detail)


class UnauthorizedIdentifierData(HTTPException):
    """
    Raised when the user data passed in does not match the
    data in the authorization token header.
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Invalid identifier data: does not match auth header token"
        super().__init__(status_code=401, detail=detail)


class ForbiddenUserAction(HTTPException):
    """
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "User does not have permission to perform this operation"
        super().__init__(status_code=403, detail=detail)

class DatabaseError(HTTPException):
    """
    Raised when the user data passed in does not match the
    data in the authorization token header.
    """
    def __init__(self, detail: Optional[str] = None):
        if not detail:
            detail = "Database error"
        super().__init__(status_code=500, detail=detail)
