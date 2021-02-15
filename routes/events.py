from starlette.exceptions import HTTPException
from fastapi import APIRouter

from models import events as models
from docs import events as docs
from util import events as utils
import logging

router = APIRouter()


@router.post(
    "/events/register",
    response_model=models.registration_response,
    description=docs.registration_desc,
    summary=docs.registration_summ,
    tags=["Events"],
    status_code=201,
)
async def register_event(form: models.registration_form):
    # receive data from client -> util.register method -> return user_id from DB insertion
    # send the form data and DB instance to util.events.register_event
    event_id = await utils.register_event(form)

    # return response in reponse model
    return models.registration_response(event_id=event_id)


@router.get("/events/{event_id}",
            description=docs.get_event_desc,
            summary=docs.get_event_summ,
            tags=["Events"],
            response_model=models.Event,
            status_code=201)
async def get_event(event_id):
    event_data = await utils.get_event(event_id)

    if event_data is None:
        raise HTTPException(status_code=400, detail="Event not in database")

    return models.Event(**event_data)


# TODO: fix this once everything else is implemented and status is relevant
@router.get(
    "/events/status/{event_id}",
    description=docs.get_event_by_status_desc,
    summary=docs.get_event_by_status_summ,
    response_model=models.get_all_events_by_status_response,
    status_code=200,
    tags=["Events"],
)
async def get_event_by_status(event_id):
    event_status = await utils.get_event_by_status(event_id)
    #  return models.Event(**event_status)
    return event_status


@router.get(
    "/events/location/",
    response_model=models.events_by_location_response,
    description=docs.events_by_location_desc,
    summary=docs.events_by_location_summ,
    tags=["Events"],
    status_code=201,
)
async def events_by_location(lat: float, lon: float, radius: int = 10):
    if not (lat and lon):
        raise HTTPException(status_code=400, detail="Missing coordinate(s)")
    if lat < -90 or lat > 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude values must be between -90 and 90 inclusive")
    if lon < -90 or lon > 90:
        raise HTTPException(
            status_code=400,
            detail="Longitude values must be between -90 and 90 inclusive")
    origin = (lat, lon)
    valid_events = await utils.events_by_location(origin, radius)
    return models.events_by_location_response(events=valid_events)


@router.get("/events/find/all",
            description=docs.get_all_events_desc,
            summary=docs.get_all_events_summ,
            tags=["Events"],
            response_model=models.all_events_response,
            status_code=200)
async def get_all_events():
    events = await utils.get_all_events()
    return events
