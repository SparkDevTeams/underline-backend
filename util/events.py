"""
Handler for event operations.
"""
from typing import Dict, List, Any, Tuple
from geopy import distance

from models import exceptions
import util.users as user_utils
import models.users as user_models
import models.events as event_models
from config.db import get_database, get_database_client_name


# create column for insertion in database_client
def events_collection():
    return get_database()[get_database_client_name()]["events"]


#create column for admin queue in database_client
def events_queue():
    return get_database()[get_database_client_name()]["events_queue"]


async def register_event(
    event_registration_form: event_models.EventRegistrationForm
) -> event_models.EventRegistrationResponse:
    """
    Takes an event registration object and inserts it into the database.
    If unapproved, adds it to the Admin queue.
    """
    creator_user_id = event_registration_form.creator_id
    await user_utils.check_if_user_exists_by_id(creator_user_id)

    # form validation followed by database insertion
    event = await get_event_from_event_reg_form(event_registration_form)

    await add_event_to_queue(event)

    events_collection().insert_one(event.dict())
    # return user_id if success

    # add registered event id to user's list of created event

    event_id = event.get_id()
    await user_utils.add_id_to_created_events_list(creator_user_id, event_id)

    return event_models.EventRegistrationResponse(event_id=event_id)


async def check_user_id_matches_reg_form(
        reg_form: event_models.EventRegistrationForm,
        user_id: user_models.UserId) -> None:
    """
    Checks that the event registration form has the same
    `creator_id` value as the `user_id` passed in.

    Raises exception if not, else returns silently.
    """
    creator_id = reg_form.creator_id
    if not creator_id == user_id:
        detail = "Token passed in does not match creator ID for the event form"
        raise exceptions.InvalidAuthHeaderException(detail=detail)


async def get_event_from_event_reg_form(
        event_reg_form: event_models.EventRegistrationForm
) -> event_models.Event:
    """
    Returns a validated Event from a event registration form
    """
    event_reg_form_dict = event_reg_form.dict()
    valid_event = event_models.Event(**event_reg_form_dict)
    return valid_event


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


async def get_events_queue() -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns a dict with a list of all of the events
    in the queue.
    """
    events = list(events_queue().find())

    # change the "_id" field to a "event_id" field
    for event in events:
        event["event_id"] = event.pop("_id")

    return {"events": events}


async def add_event_to_queue(event: event_models.Event):
    """
    Adds events to queue
    """
    if event.approval == 'unapproved':
        events_queue().insert_one(event.dict())


async def remove_event_from_queue(event_id: event_models.EventId):
    """
    Remove event from queue
    """
    events_queue().find_one_and_delete({"_id": event_id})


async def change_event_approval(event_id: event_models.EventId,
                                approved: bool):
    """
    Changes an event's approval status enum in-place, and also
    removes it from the approve/deny queue.
    """
    if approved:
        decision_enum = event_models.EventApprovalEnum.approved.name
    else:
        decision_enum = event_models.EventApprovalEnum.denied.name

    # FIXME: very ugly!
    events_collection().find_one_and_update(
        filter={"_id": event_id}, update={"$set": {
            'approval': decision_enum
        }})

    await utils_events.remove_event_from_queue(event_id)


async def get_event_by_id_in_queue(
        event_id: event_models.EventId) -> event_models.Event:
    """
    Returns an Event object from the queue by it's id.

    Throws 404 if nothing is found
    """
    event_document = events_queue().find_one({"_id": event_id})
    if not event_document:
        raise exceptions.EventNotFoundException

    return event_models.Event(**event_document)


async def search_events(
        form: event_models.EventSearchForm) -> List[Dict[str, Any]]:
    """
    Returns events from the database based on a key word
    and a date range
    """
    events = events_collection().find()
    result_events = []

    event_matches_query = lambda event: form.keyword in {
        event["title"], event["description"]
    }
    for event in events:
        if event_matches_query(event):
            result_events.append(event)

    return {"events": result_events}


async def batch_event_query(
    query_form: event_models.BatchEventQueryModel
) -> event_models.BatchEventQueryResponse:
    """
    Returns a list of events filtered by datetimes and
    event tags.
    """
    filter_dict = await get_db_filter_dict_for_query(query_form)

    list_of_events_found = await get_events_from_filtered_query(
        filter_dict, query_form)

    response = event_models.BatchEventQueryResponse(
        events=list_of_events_found)
    return response


async def get_db_filter_dict_for_query(
        query_form: event_models.BatchEventQueryModel) -> Dict[str, Any]:
    """
    Given a query form, generates a database filter dict for an event query
    """
    datetime_filter_dict = await get_date_filter_dict_for_query(query_form)
    event_tags_filter_dict = await get_tag_filter_dict_for_query(query_form)

    filter_dict = await get_base_batch_filter_dict()
    filter_dict.update(datetime_filter_dict)
    filter_dict.update(event_tags_filter_dict)

    return filter_dict


async def get_events_from_filtered_query(
        filter_dict: Dict[str,
                          Any], query_form: event_models.BatchEventQueryModel
) -> List[event_models.Event]:
    """
    Executes a batch database query given the filter, and returns the list of
    events found by pages.
    """
    events_found = []
    query_limit = query_form.limit * (query_form.index + 1)
    event_query_response = events_collection().find(filter_dict).limit(
        query_limit)

    for _ in range(query_form.index * query_form.limit):
        next(event_query_response, None)

    for event_document in event_query_response:
        event = event_models.Event(**event_document)
        events_found.append(event)

    return events_found


async def get_date_filter_dict_for_query(
        query_form: event_models.BatchEventQueryModel) -> Dict[str, Any]:
    """
    Returns a filter dict for querying between datetimes
    for a given query form
    """
    has_date_range = bool(query_form.query_date_range)

    if has_date_range:
        start_date = query_form.query_date_range.start_date
        end_date = query_form.query_date_range.end_date

        datetime_start_filter = {"date_time_start": {"$lte": start_date}}
        datetime_end_filter = {"date_time_end": {"$gt": end_date}}
    else:
        datetime_start_filter = {
            "date_time_start": {
                "$lte": query_form.query_date
            }
        }
        datetime_end_filter = {"date_time_end": {"$gt": query_form.query_date}}

    filter_dict = {}
    filter_dict.update(datetime_start_filter)
    filter_dict.update(datetime_end_filter)

    return filter_dict


async def get_tag_filter_dict_for_query(
        query_form: event_models.BatchEventQueryModel) -> Dict[str, Any]:
    """
    Given a query form, returns the filter dict to be used for the
    database query to filter the events by tag.
    """
    if not query_form.event_tag_filter:
        return {}

    filter_dict = {
        "tags": {
            "$elemMatch": {
                "$in": query_form.event_tag_filter
            }
        }
    }
    return filter_dict


async def get_base_batch_filter_dict() -> Dict[str, Any]:
    """
    Returns the base filter for the batch query.

    This includes events that are:
    - public and approved events
    - upcoming, or active
    """
    valid_status_list = await get_list_of_valid_query_status()

    filter_dict = {"public": True, "status": {"$in": valid_status_list}}

    return filter_dict


async def get_list_of_valid_query_status() -> List[str]:
    """
    Returns the list of valid status enum strings for the
    batch event query
    """
    status_enum = event_models.EventStatusEnum
    enum_to_str = lambda enum_val: enum_val.name
    valid_status_list = [
        enum_to_str(enum_val)
        for enum_val in [status_enum.active, status_enum.ongoing]
    ]

    return valid_status_list
