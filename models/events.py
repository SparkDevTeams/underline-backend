# pylint: disable=unsubscriptable-object
#       - this is actually a pylint bug that hasn't been resolved.
# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
# pylint: disable=no-name-in-module
#       - Need to whitelist pydantic locally
"""
Holds the database models for user operations.

Pydantic offers fast, safe, and extendable validation
Think of it as strong typing without the verbosity.

These models should be the only places where raw input/output data is changed.
"""
import random
from enum import auto
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, validator
import models.images as image_models
import models.commons as common_models

EventId = common_models.EventId


class EventTagEnum(common_models.AutoName):
    """
    Enum that holds the different possible types or labels of events.
    """
    sport_event = auto()
    food_event = auto()
    art_event = auto()
    music_event = auto()
    meeting_event = auto()
    class_event = auto()
    paid_event = auto()


class EventApprovalEnum(common_models.AutoName):
    """
    Holds the different life statuses that events can cycle through.
    """
    approved = auto()
    denied = auto()
    unapproved = auto()
    private = auto()


class EventStatusEnum(common_models.AutoName):
    """
    Holds the different life statuses that events can cycle through.
    """
    active = auto()
    cancelled = auto()
    ongoing = auto()
    expired = auto()


class Location(BaseModel):
    """
    Simple tuple-like to group (lat, long) into a logical pairing.
    """
    title: str
    latitude: float
    longitude: float


class Event(common_models.ExtendedBaseModel):
    """
    Main Event model that should have a 1:1 correlation with the database
    rendition of an event.

    Any changes here can have lots of side effects, as many forms inherit this
    model, thereby sharing fields. Refactor or extend thoughtfully.
    """
    title: str
    description: str
    date_time_start: datetime
    date_time_end: datetime
    tags: List[EventTagEnum]
    location: Location
    max_capacity: int
    public: bool
    comment_ids: List[str] = []
    attending: List[common_models.UserId] = []
    status: EventStatusEnum = EventStatusEnum.active
    links: List[str]
    image_ids: List[image_models.ImageId] = []
    creator_id: common_models.UserId
    approval: EventApprovalEnum = EventApprovalEnum.unapproved


class EventRegistrationForm(BaseModel):
    """
    Form that represents an event registration.

    Has only the necessary client-facing data needed to create
    an event in the database.
    """
    title: str
    description: str
    date_time_start: datetime
    date_time_end: datetime
    tags: List[EventTagEnum]
    public: bool
    location: Location
    max_capacity: int
    links: Optional[List[str]] = []
    image_ids: Optional[List[image_models.ImageId]] = []
    creator_id: common_models.UserId

    @validator("location", pre=True, always=True)
    def randomize_location_cords(cls: 'EventRegistrationForm',
                                 value: Dict[str, Any]) -> Dict[str, Any]:
        """
        Randomizes the lat/long for the location slightly
        """
        range_start = 0.00004
        range_end = 0.00006
        offset = lambda: random.uniform(range_start, range_end
                                        ) * random.choice([1, -1])
        value["latitude"] += offset()
        value["longitude"] += offset()
        return value

    class Config:
        use_enum_values = True


class EventRegistrationResponse(BaseModel):
    """
    Response for a succesful event registration response.

    Should consist of a way for the client to get back the data
    they just handed off.
    """
    event_id: str


class EventQueryResponse(BaseModel):
    """
    This is user-facing (i.e. public) data type for an event.

    Shouldn't hold any logistic/serverside details for events if possible.
    """
    title: str
    description: str
    date_time_start: datetime
    date_time_end: datetime
    tags: List[EventTagEnum]
    location: Location
    max_capacity: int
    public: bool
    attending: List[common_models.UserId]
    comment_ids: List[str]
    status: EventStatusEnum
    links: List[str]
    image_ids: List[image_models.ImageId]
    creator_id: common_models.UserId
    event_id: EventId


class ListOfEvents(BaseModel):
    """
    This seems kind of too simple to be necessary but this exact model
    comes up a lot when processing events, so extracting it out to it's own
    model could be really useful down the line. Also makes some models
    prettier and less repetitive.
    """
    events: List[EventQueryResponse]


# NOTE: The following few models seems really stupid but returning
#       a `ListOfEvents` makes a lot less sense when you're in the endpoint
#       for returning some sort of specific query.
#       This increases readability quite a bit for 0 overhead
#       and is akin to type aliasing.
class EventQueryByLocationResponse(ListOfEvents):
    """
    Returns the list of events found by a location query.
    """


class EventQueryByStatusResponse(ListOfEvents):
    """
    Returns the list of events filtered by status
    """


class AllEventsQueryResponse(ListOfEvents):
    """
    Returns all events in the database.
    """


class EventSearchResponse(ListOfEvents):
    """
    Returns the list of events filtered by status
    """


class EventSearchForm(BaseModel):
    """
    Form that represents values inputed for a search
    """
    keyword: str


class BatchEventQueryResponse(ListOfEvents):
    """
    Returns the list of events queried from the batch event
    query endpoint.
    """


class DateRange(common_models.CustomBaseModel):
    """
    Data model that holds a start and end date to signify a datetime range.
    """
    start_date: datetime
    end_date: datetime


class BatchEventQueryModel(common_models.CustomBaseModel):
    """
    Incoming data form model for the batch query request.

    Can be dynamic to accomodate multiple modalities of batch
    request types.
    """
    query_date: Optional[datetime] = datetime.today() - timedelta(hours=4)
    query_date_range: Optional[DateRange]
    event_tag_filter: Optional[List[EventTagEnum]] = []
    limit: Optional[int] = 5
    index: Optional[int] = 0
