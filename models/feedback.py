"""
Holds the (small) models for feedback object to be tied to an event.
"""

from pydantic import BaseModel


class Feedback(BaseModel):
    """
    Holds the very simple feedback model that will be
    indexed by ID in an event.
    """
    event_id: str
    comment: str


# pylint: disable=invalid-name
class registration_form(Feedback):
    """
    Client facing registration form for feedback.
    """


class registration_response(BaseModel):
    """
    Response for a successful feedback registration.
    """
    feedback_id: str
