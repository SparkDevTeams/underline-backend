# pylint: disable=unsubscriptable-object
#       - pylint bug with optional
# pylint: disable=no-name-in-module
#       - Need to whitelist pydantic locally
"""
Holds the (small) models for feedback object to be tied to an event.
"""
from pydantic import BaseModel
import models.commons as common_models
import models.users as user_models

FeedbackId = str


class Feedback(common_models.ExtendedBaseModel):
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
