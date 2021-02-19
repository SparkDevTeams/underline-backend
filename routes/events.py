"""
FastAPI endpoint handlers for code related to events.

As with all files in `routes/`, the endpoints here should do as little actual
data handling as possible, handing it off to the handler in `util/` as soon
as possible.
"""
from starlette.exceptions import HTTPException
from fastapi import APIRouter

from models import events as models
from docs import events as docs
from util import events as utils

router = APIRouter()


@router.post(
    "/events/register",
    response_model=models.EventRegistrationResponse,
    description=docs.registration_desc,
    summary=docs.registration_summ,
    tags=["Events"],
    status_code=201,
)
async def register_event(form: models.EventRegistrationForm):
    """
    Main endpoint handler for registering an event.

    The overall workflow for the function is:
        1. receive data from the client
        2. send the data from to the `util.register_event` method
        3. return the `event_id` from the inserted document to the client
    """
    # send the form data and DB instance to util.events.register_event
    event_registration_response = await utils.register_event(form)

    # return response in reponse model
    return event_registration_response


@router.get("/events/get/{event_id}",
            response_model=models.EventQueryResponse,
            description=docs.get_event_desc,
            summary=docs.get_event_summ,
            tags=["Events"],
            status_code=201)
async def get_event(event_id):
    """
    Simplest query endpoint that queries the database for a single event with
    a matching `event_id`.
    """
    event_data = await utils.get_event_by_id(event_id)
    return models.EventQueryResponse(**event_data)


@router.get(
    "/events/status/{event_id}",
    response_model=models.EventQueryByStatusResponse,
    description=docs.get_event_by_status_desc,
    summary=docs.get_event_by_status_summ,
    status_code=200,
    tags=["Events"],
)
async def get_event_by_status(event_id):
    """
    Endpoint that returns all of the events by a status.

    FIXME: Currently not implemented! Mostly because status isn't implemented.
    """
    event_status = await utils.get_event_by_status(event_id)
    return event_status


@router.get(
    "/events/location",
    response_model=models.EventQueryByLocationResponse,
    description=docs.events_by_location_desc,
    summary=docs.events_by_location_summ,
    tags=["Events"],
    status_code=200,
)
async def events_by_location(lat: float, lon: float, radius: float = 10.0):
    """
    Endpoint for querying the events database by location.

    Should return all of the events that are within the given search radius.
    """
    origin = (lat, lon)
    valid_events = await utils.events_by_location(origin, radius)
    return models.EventQueryByLocationResponse(events=valid_events)


@router.get("/events/find/all",
            response_model=models.AllEventsQueryResponse,
            description=docs.get_all_events_desc,
            summary=docs.get_all_events_summ,
            tags=["Events"],
            status_code=200)
async def get_all_events():
    """
    Endpoint for returning ALL events in the database without any filter.
    """
    events = await utils.get_all_events()
    return events
