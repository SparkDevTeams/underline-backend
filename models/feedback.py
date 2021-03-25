# pylint: disable=unsubscriptable-object
#       - pylint bug with optional
# pylint: disable=no-name-in-module
#       - Need to whitelist pydantic locally
"""
Holds the (small) models for feedback object to be tied to an event.
"""
from pydantic import BaseModel
import models.commons as common_models

FeedbackId = str


class Feedback(common_models.ExtendedBaseModel):
    """
    Holds the very simple feedback model that will be
    indexed by ID in an event.
    """
    event_id: str
    comment: str


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
