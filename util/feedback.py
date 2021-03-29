"""
Handlers for feedback operations.
"""
from config.db import get_database, get_database_client_name
from models import exceptions
import models.users as user_models
import models.events as event_models
import models.feedback as feedback_models


# instanciate the main collection to use for this util file for convenience
def feedback_collection():
    return get_database()[get_database_client_name()]["feedback"]


def events_collection():
    return get_database()[get_database_client_name()]["events"]


async def delete_feedback(event_id: event_models.EventId,
                          feedback_id: feedback_models.FeedbackId,
                          user_id_from_token: user_models.UserId) -> None:
    """
    Given an event id and feedback id, attempt to delete the feedback from
    the event's comment_ids array as well as from the feedback collection
    """
    found_event = events_collection().find_one({"_id": event_id})

    if not found_event:
        raise exceptions.EventNotFoundException
    if feedback_id not in found_event["comment_ids"]:
        raise exceptions.FeedbackNotFoundException

    feedback_query = {"_id": feedback_id}
    found_comment_document = feedback_collection().find_one(feedback_query)

    if not found_comment_document:
        raise exceptions.FeedbackNotFoundException
    if found_comment_document["creator_id"] != user_id_from_token:
        detail = "User ID does not match creator ID for the comment"
        raise exceptions.UnauthorizedIdentifierData(detail=detail)

    # remove the feedback ID from the event then update the DB document to match
    found_event["comment_ids"].remove(feedback_id)
    events_collection().update_one({"_id": event_id}, {"$set": found_event})

    # remove feedback from the feedback collection
    feedback_collection().delete_one(feedback_query)


async def register_feedback(
    registration_form: feedback_models.FeedbackRegistrationRequest
) -> feedback_models.FeedbackId:
    """
    Given an event id, create a feedback id and add the feedback to the event
    """
    # attempt to find given event
    event_id = registration_form.event_id
    found_event = events_collection().find_one({"_id": event_id})
    if not found_event:
        raise exceptions.EventNotFoundException

    # insert the feedback into the feedback collection
    valid_feedback = await get_feedback_from_reg_form(registration_form)
    feedback_collection().insert_one(valid_feedback.dict())

    # add feedback id to event and update it in the database
    feedback_id = valid_feedback.get_id()
    found_event["comment_ids"].append(feedback_id)
    events_collection().update_one({"_id": event_id}, {"$set": found_event})

    return feedback_id


async def get_feedback_from_reg_form(
    reg_form: feedback_models.FeedbackRegistrationRequest
) -> feedback_models.Feedback:
    """
    Validates and creates a valid feedback object from an incoming registration
    form and returns it.
    """
    valid_feedback = feedback_models.Feedback(**reg_form.dict())
    return valid_feedback


async def get_feedback(
        feedback_id: feedback_models.FeedbackId) -> feedback_models.Feedback:
    """
    Returns the feedback document as a Feedback object given it's id.
    """
    feedback = feedback_collection().find_one({"_id": feedback_id})

    if not feedback:
        raise exceptions.FeedbackNotFoundException

    return feedback_models.Feedback(**feedback)
