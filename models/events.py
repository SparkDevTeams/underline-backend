<<<<<<< HEAD
# pylint: disable=unsubscriptable-object
#       - this is actually a pylint bug that hasn't been resolved.
# pylint: disable=fixme
#       - don't want to break lint but also don't want to create tickets.
#         as soon as this is on the board, remove this disable.
"""
Holds the database models for user operations.

Pydantic offers fast, safe, and extendable validation
Think of it as strong typing without the verbosity.

These models should be the only places where raw input/output data is changed.
"""
from typing import List, Optional
from enum import Enum, auto
from pydantic import BaseModel
import models.users as user_models


class AutoName(Enum):
    """
    Hacky but abstracted-enough solution to the dumb enum naming problem that
    python has. Basically returns enums in string form when referenced by value
    """
    def _generate_next_value_(name, start, count, last_values):
        """
        Returns name of enum rather than assigned value.
        """
        return name


class TagEnum(AutoName):
    """
    Enum that holds the different possible types or labels of events.
    """
    sporting_events = auto()
    food_events = auto()
    art_expo = auto()
    music_show = auto()
    restroom = auto()


class StatusEnum(AutoName):
    """
    Holds the different life statuses that events can cycle through.
    """
    active = auto()
    cancelled = auto()
    ongoing = auto()
    expired = auto()


class Location(BaseModel):
    """
    Simple tuple-like to group lat,long into a logical pairing.
    """
    latitude: float
    longitude: float


class Event(BaseModel):
    """
    Main Event model that should have a 1:1 correlation with the database
    rendition of an event.

    Any changes here can have lots of side effects, as many forms inherit this
    model, thereby sharing fields. Refactor or extend thoughtfully.
    """
    title: str
    description: str
    date: str
    tag: TagEnum
    location: Location
    max_capacity: int
    public: bool
    attending: List[user_models.Users]
    upvotes: int
    comment_ids: List[str]
    rating: float
    status: StatusEnum
    creator_id: str
    event_id: Optional[str]
    # TODO: add landmark flag OR extend into own class
    # TODO: think about how to handle expiration based on dates


# pylint: disable=invalid-name
class registration_form(Event):
    """
    Form that represents an event registration.
    """


class registration_response(BaseModel):
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


# NOTE: The following few models seems really stupid but returning
#       a `ListOfEvents` makes a lot less sense when you're in the endpoint
#       for returning some sort of specific query.
#       This increases readability quite a bit for 0 overhead
#       and is akin to type aliasing.
class events_by_location_response(ListOfEvents):
    """
    Returns the list of events found by a location query.
    """


class get_all_events_by_status_response(ListOfEvents):
    """
    Returns the list of events filtered by status
    """


class all_events_response(ListOfEvents):
    """
    Returns all events in the database.
    """
=======
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
from enum import Enum, auto
from typing import List, Any, Dict
from pydantic import BaseModel, validator, Field
import models.users as user_models
import models.commons as model_commons

# type alias for event ids
EventId = str


class AutoName(Enum):
    """
    Hacky but abstracted-enough solution to the dumb enum naming problem that
    python has. Basically returns enums in string form when referenced by value
    """

    # since this is a funky should-be-private method, we have to break
    # a couple of lint rules
    # pylint: disable=unused-argument, no-self-argument
    def _generate_next_value_(name, start, count, last_values):
        """
        Returns name of enum rather than assigned value.
        """
        return name


class EventTagEnum(AutoName):
    """
    Enum that holds the different possible types or labels of events.
    """
    sporting_events = auto()
    food_events = auto()
    art_expo = auto()
    music_show = auto()
    restroom = auto()


class EventStatusEnum(AutoName):
    """
    Holds the different life statuses that events can cycle through.
    """
    active = auto()
    cancelled = auto()
    ongoing = auto()
    expired = auto()


class Location(BaseModel):
    """
    Simple tuple-like to group lat,long into a logical pairing.
    """
    latitude: float
    longitude: float


class Event(BaseModel):
    """
    Main Event model that should have a 1:1 correlation with the database
    rendition of an event.

    Any changes here can have lots of side effects, as many forms inherit this
    model, thereby sharing fields. Refactor or extend thoughtfully.
    """
    # alias needed for validator access
    id: EventId = Field("", alias="_id")  # pylint: disable=invalid-name
    title: str
    description: str
    date: str
    tag: EventTagEnum
    location: Location
    max_capacity: int
    public: bool
    attending: List[user_models.User]
    upvotes: int
    comment_ids: List[str]
    rating: float
    status: EventStatusEnum
    creator_id: user_models.UserId

    # TODO: add landmark flag OR extend into own class
    # TODO: think about how to handle expiration based on dates
    class Config:
        use_enum_values = True

    @validator("id", pre=True, always=True)
    def set_id(cls, value) -> str:
        """
        Workaround on dynamic default setting for UUID.
        From: https://github.com/samuelcolvin/pydantic/issues/866
        """
        return value or model_commons.generate_uuid4_str()

    def get_id(self) -> EventId:
        """
        Returns this instance's ID
        """
        return self.id

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Override the base `dict` method in order to get the mongo ID fix
        """
        parent_dict = super().dict(*args, **kwargs)
        parent_dict["_id"] = self.get_id()
        return parent_dict


class EventRegistrationForm(Event):
    """
    Form that represents an event registration.
    """


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


class EventQueryResponse(Event):
    """
    This is user-facing (i.e. public) data type for an event.

    Shouldn't hold any logistic/serverside details for events if possible.
    """


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
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
