# pylint: disable=unsubscriptable-object
#       - this is actually a pylint bug that hasn't been resolved.
# pylint: disable=fixme
#       - don't want to break lint but also don't want to create tickets.
#         as soon as this is on the board, remove this disable.
# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
"""
Holds the database models for user operations.

Pydantic offers fast, safe, and extendable validation
Think of it as strong typing without the verbosity.

These models should be the only places where raw input/output data is changed.
"""
from enum import auto
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
import models.users as user_models
import models.images as image_models
import models.commons as model_commons

# type alias for event ids
EventId = str


class EventTagEnum(model_commons.AutoName):
    """
    Enum that holds the different possible types or labels of events.
    """
    sporting_events = auto()
    food_events = auto()
    art_expo = auto()
    music_show = auto()
    restroom = auto()


class EventStatusEnum(model_commons.AutoName):
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


class Event(model_commons.ExtendedBaseModel):
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
    attending: List[user_models.UserId] = []
    status: EventStatusEnum = EventStatusEnum.active
    links: List[str]
    image_ids: List[image_models.ImageId] = []
    creator_id: user_models.UserId


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
    public: bool  # TODO: this has to actually be handled
    location: Location
    max_capacity: int
    links: Optional[List[str]] = []
    image_ids: Optional[List[image_models.ImageId]] = []
    creator_id: user_models.UserId

    class Config:
        use_enum_values = True


class EventRegistrationResponse(BaseModel):
    """
    Response for a succesful event registration response.

    Should consist of a way for the client to get back the data
    they just handed off.
    """
    event_id: str


class ListOfEvents(BaseModel):
    """
    This seems kind of too simple to be necessary but this exact model
    comes up a lot when processing events, so extracting it out to it's own
    model could be really useful down the line. Also makes some models
    prettier and less repetitive.
    """
    events: List[Event]


class EventQueryResponse(BaseModel):
    """
    This is user-facing (i.e. public) data type for an event.

    Shouldn't hold any logistic/serverside details for events if possible.
    """
    title: str
    description: str
    date_time_start: str
    date_time_end: str
    tags: List[EventTagEnum]
    location: Location
    max_capacity: int
    public: bool
    attending: List[user_models.UserId]
    comment_ids: List[str]
    status: EventStatusEnum
    links: List[str]
    image_ids: List[image_models.ImageId]
    creator_id: user_models.UserId
    event_id: EventId


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
