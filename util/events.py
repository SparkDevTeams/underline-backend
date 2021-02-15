import uuid
from enum import Enum
from config.db import get_database, get_database_client_name
from starlette.exceptions import HTTPException
from geopy import distance
import logging


async def generate_id():
    return str(uuid.uuid4())


async def register_event(form, database_client):
    # cast input form (python class) -> dictionary (become JSON eventually)
    form_dict = form.dict()

    # generating event_id (UUID)
    event_id = await generate_id()

    # insert the event_id to the dictionary for insertion
    form_dict["_id"] = event_id

    # create column for insertion in database_client
    column = database_client[get_database_client_name()]["events"]

    # XXX BAD CODE ALERT!!!!
    # This will turn every instance of a enum into a string of itself
    # Bad time complexity and pretty stupid
    # Fix this in models!!!
    # TODO: this code will break the "query by status" endpoint when it is implemented
    # fix before testing that!!!
    for key, val in form_dict.items():
        if isinstance(val, Enum):
            form_dict[key] = val.name

    # insert id into column
    column.insert_one(form_dict)

    # return user_id if success
    return event_id


# Returns event dictionary
async def get_event(event_id, database_client):
    column = database_client[get_database_client_name()]["events"]
    event = column.find_one({"_id": event_id})

    return event


async def events_by_location(origin, radius, database_client):
    def within_radius(event):
        event_location = event.get("location", {})

        event_lat = event_location.get("latitude", 0)
        event_lon = event_location.get("longitude", 0)

        destination = (event_lat, event_lon)

        distance_mi = distance.distance(origin, destination).miles

        return distance_mi <= radius

    column = database_client[get_database_client_name()]["events"]

    events = column.find()
    all_events = [event for event in events]

    valid_events = list(filter(within_radius, all_events))

    return valid_events


# Returns all the events.
async def get_event_by_status(event_id, database_client):
    column = database_client[get_database_client_name()]["events"]
    all_events = column.find()
    all_events_list = [event for event in all_events]
    if not all_events_list:
        raise HTTPException(status_code=404,
                            detail="Event with given ID not found")
    return {"events": all_events_list}


async def get_all_events(database_client):
    collection = database_client[get_database_client_name()]["events"]
    events = list(collection.find())

    # change the "_id" field to a "event_id" field
    for event in events:
        event["event_id"] = event["_id"]
        del event["_id"]

    return {"events": events}
