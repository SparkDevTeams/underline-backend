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
