# pylint: disable=unsubscriptable-object
#       - pylint bug with optional
"""
Holds the (small) models for feedback object to be tied to an event.
"""
from pydantic import BaseModel
import models.users as user_models
import models.commons as model_commons

FeedbackId = str


class Feedback(model_commons.ExtendedBaseModel):
    """
    Holds the very simple feedback model that will be
    indexed by ID in an event.
    """
    event_id: str
    comment: str
    creator_id: user_models.UserId


class FeedbackQueryResponse(BaseModel):
    """
    Model for all public facing data from a feedback document in the database
    """
    event_id: str
    comment: str
    creator_id: user_models.UserId


class FeedbackRegistrationRequest(BaseModel):
    """
    Client facing registration form for feedback.
    """
    event_id: str
    comment: str
    creator_id: user_models.UserId


class FeedbackRegistrationResponse(BaseModel):
    """
    Response for a successful feedback registration.
    """
    feedback_id: FeedbackId
