"""
Handler for event operations.
"""
from geopy import distance
from models import exceptions
import models.events as event_models
from config.db import get_database, get_database_client_name


# create column for insertion in database_client
def events_collection():
    return get_database()[get_database_client_name()]["events"]


async def register_event(
    event_registration_form: event_models.EventRegistrationForm
) -> event_models.EventRegistrationResponse:
    """
    Takes an event registration object and inserts it into the database
    """
    event = await get_event_from_event_reg_form(event_registration_form)

    events_collection().insert_one(event.dict())

    # return user_id if success
    event_id = event.get_id()
    return event_models.EventRegistrationResponse(event_id=event_id)


async def get_event_from_event_reg_form(
        event_reg_form: event_models.EventRegistrationForm
) -> event_models.Event:
    """
    Returns a validated Event from a event registration form
    """
    return event_models.Event(**event_reg_form.dict())


async def get_event_by_id(
        event_id: event_models.EventId) -> event_models.Event:
    """
    Returns an Event object from the database by it's id.

    Throws 404 if nothing is found
    """
    event_document = events_collection().find_one({"_id": event_id})
    if not event_document:
        raise exceptions.EventNotFoundException

    return event_models.Event(**event_document)


async def events_by_location(origin, radius):
    def within_radius(event):
        event_location = event.get("location", {})

        event_lat = event_location.get("latitude", 0)
        event_lon = event_location.get("longitude", 0)

        destination = (event_lat, event_lon)

        distance_mi = distance.distance(origin, destination).miles

        return distance_mi <= radius

    events = events_collection().find()

    valid_events = list(filter(within_radius, events))

    return valid_events


# Returns all the events.
async def get_event_by_status(_event_id):
    raise Exception("Unimplemented")


async def get_all_events():
    events = list(events_collection().find())

    # change the "_id" field to a "event_id" field
    for event in events:
        event["event_id"] = event["_id"]
        del event["_id"]

    return {"events": events}
