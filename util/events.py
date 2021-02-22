<<<<<<< HEAD
import uuid
from enum import Enum
from config.db import get_database, get_database_client_name
from starlette.exceptions import HTTPException
from geopy import distance
import logging


# create column for insertion in database_client
def events_collection():
    return get_database()[get_database_client_name()]["events"]


async def generate_id():
    return str(uuid.uuid4())


async def register_event(form):
    # cast input form (python class) -> dictionary (become JSON eventually)
    form_dict = form.dict()

    # generating event_id (UUID)
    event_id = await generate_id()

    # insert the event_id to the dictionary for insertion
    form_dict["_id"] = event_id

    # XXX BAD CODE ALERT!!!!
    # This will turn every instance of a enum into a string of itself
    # Bad time complexity and pretty stupid
    # Fix this in models!!!
    # TODO: this code will break the "query by status" endpoint when it is implemented
    # fix before testing that!!!
    for key, val in form_dict.items():
        if isinstance(val, Enum):
            form_dict[key] = val.name

    # insert id into collection
    events_collection().insert_one(form_dict)

    # return user_id if success
    return event_id


# Returns event dictionary
async def get_event(event_id):
    event = events_collection().find_one({"_id": event_id})

    return event


async def events_by_location(origin, radius):
    def within_radius(event):
        event_location = event.get("location", {})

        event_lat = event_location.get("latitude", 0)
        event_lon = event_location.get("longitude", 0)

        destination = (event_lat, event_lon)

        distance_mi = distance.distance(origin, destination).miles

        return distance_mi <= radius

    events = events_collection().find()
    all_events = [event for event in events]

    valid_events = list(filter(within_radius, all_events))

    return valid_events


# Returns all the events.
async def get_event_by_status(event_id):
    all_events = events_collection().find()
    all_events_list = [event for event in all_events]
    if not all_events_list:
        raise HTTPException(status_code=404,
                            detail="Event with given ID not found")
    return {"events": all_events_list}


async def get_all_events():
    events = list(events_collection().find())

    # change the "_id" field to a "event_id" field
    for event in events:
        event["event_id"] = event["_id"]
        del event["_id"]

    return {"events": events}
=======
"""
Handler for event operations.
"""
from typing import Dict, List, Any, Tuple
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


async def events_by_location(origin: Tuple[float, float],
                             radius: float) -> List[Dict[str, Any]]:
    """
    Given an origin point and a radius, finds all events
    within that radius.
    """
    def within_radius(event):
        """
        Given an event dict, checks if the event is within the
        given distance radius
        """
        event_location = event.get("location", {})
        event_lat = event_location.get("latitude", 0)
        event_lon = event_location.get("longitude", 0)

        destination = (event_lat, event_lon)
        try:
            distance_mi = distance.distance(origin, destination).miles
        except ValueError as coord_error:
            detail = f"Error with querying event by location: {coord_error}"
            raise exceptions.InvalidDataException(
                detail=detail) from coord_error
        return distance_mi <= radius

    events = events_collection().find()
    valid_events = list(filter(within_radius, events))
    return valid_events


async def get_event_by_status(_event_id) -> None:
    """
    Returns all events with a matching status tag.

    TODO: implement this with the tag system
    """
    raise Exception("Unimplemented")


async def get_all_events() -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns a dict with a list of all of the events
    in the database.
    """
    events = list(events_collection().find())

    # change the "_id" field to a "event_id" field
    for event in events:
        event["event_id"] = event.pop("_id")

    return {"events": events}
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
