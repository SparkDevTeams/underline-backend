import uuid
from starlette.exceptions import HTTPException
from config.db import get_database, get_database_client_name
import logging


# instanciate the main collection to use for this util file for convenience
def feedback_collection():
    return get_database()[get_database_client_name()]["feedback"]


def events_collection():
    return get_database()[get_database_client_name()]["events"]


async def generate_id():
    return str(uuid.uuid4())


# Given an event id and feedback id, attempt to delete the feedback from the event's comment_ids array as well as from the feedback collection
async def delete_feedback(event_id, feedback_id):
    found_event = events_collection().find_one({"_id": event_id})

    if not found_event:
        raise HTTPException(status_code=404, detail="Event ID is invalid")

    if feedback_id in found_event["comment_ids"]:
        found_event["comment_ids"].remove(feedback_id)
    else:
        raise HTTPException(
            status_code=404,
            detail="Feedback ID not found in the provided event")

    events_collection().update_one({"_id": event_id}, {"$set": found_event})

    # Remove feedback from the feedback collection
    found_feedback = feedback_collection().find_one({"_id": feedback_id})

    if not found_feedback:
        raise HTTPException(status_code=404, detail="Feedback ID is invalid")

    feedback_collection().delete_one({"_id": feedback_id})


# Given an event id, create a feedback id and add the feedback to the event
# Event id is a body parameter
async def add_feedback(form):
    form_dict = form.dict()
    feedback_id = await generate_id()
    form_dict["_id"] = feedback_id

    event_id = form_dict["event_id"]

    # attempt to find event and add feedback
    found_event = events_collection().find_one({"_id": event_id})
    if not found_event:
        raise HTTPException(status_code=404, detail="Event ID is invalid")

    found_event["comment_ids"].append(feedback_id)
    events_collection().update_one({"_id": event_id}, {"$set": found_event})

    feedback_collection().insert_one(form_dict)

    return feedback_id


# Returns feedback dictionary
async def get_feedback(feedback_id):
    feedback = feedback_collection().find_one({"_id": feedback_id})

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback ID is invalid")

    return feedback
