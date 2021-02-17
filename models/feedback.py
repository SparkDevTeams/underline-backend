"""
Holds the (small) models for feedback object to be tied to an event.
"""
from uuid import uuid4
from typing import Optional
from pydantic import BaseModel

FeedbackId = str


class Feedback(BaseModel):
    """
    Holds the very simple feedback model that will be
    indexed by ID in an event.
    """
    _id: Optional[FeedbackId] = str(uuid4())
    event_id: str
    comment: str

    def get_id(self) -> FeedbackId:
        """
        Returns the object's protected id.
        """
        return self._id


class FeedbackQueryResponse(Feedback):
    """
    Model for all public facing data from a feedback document in the database
    """


class FeedbackRegistrationRequest(Feedback):
    """
    Client facing registration form for feedback.
    """


class FeedbackRegistrationResponse(BaseModel):
    """
    Response for a successful feedback registration.
    """
    feedback_id: str
