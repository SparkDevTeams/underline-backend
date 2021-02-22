<<<<<<< HEAD
import pytest
import os
import uuid
from config.db import database_client, clear_test_collections
from fastapi.testclient import TestClient
from app import app
import datetime
import logging
client = TestClient(app)


# startup process
def pytest_configure(config):
    os.environ['_called_from_test'] = 'True'
    database_client.connect_to_mongo()


def pytest_unconfigure(config):
    os.environ['_called_from_test'] = 'False'
    clear_test_collections()
    database_client.close_connection_to_mongo()


@pytest.fixture(scope='module')
def registered_user():
    user_data = {
        "first_name": "Testing_first",
        "last_name": "Testing_last",
        "email": "test@mail.com"
    }
    response = client.post("/users/register", json=user_data)
    return user_data


@pytest.fixture(scope='module')
def registered_event():
    json = {
        "title": "Test Event",
        "description": "Test Description",
        "date": str(datetime.datetime.now()),
        "tag": "sporting_events",
        "location": {
            "latitude": 75.0,
            "longitude": 75.0
        },
        "max_capacity": 10,
        "public": False,
        "attending": [],
        "upvotes": 0,
        "comment_ids": [],
        "rating": 5.0,
        "status": "active",
        "creator_id": "0"
    }
    event_response = client.post("/events/register", json=json)
    assert event_response.status_code == 201

    return {"event_json": json, "response_json": event_response.json()}


@pytest.fixture(scope="module")
def registered_feedback_data():
    event_json = {
        "title": "Test event feedback",
        "description": "Test Description",
        "date": str(datetime.datetime.now()),
        "tag": "sporting_events",
        "location": {
            "latitude": 75.0,
            "longitude": 75.0
        },
        "max_capacity": 10,
        "public": False,
        "attending": [],
        "upvotes": 0,
        "comment_ids": [],
        "rating": 5.0,
        "status": "active",
        "creator_id": "0"
    }
    # send request to register event
    event_response = client.post("/events/register", json=event_json)
    assert event_response.status_code == 201

    # extract event ID from response json
    event_id = event_response.json()["event_id"]

    # now register feedback
    feedback_json = {"event_id": event_id, "comment": "Test feedback comment"}

    feedback_response = client.post("/feedback/add", json=feedback_json)
    assert feedback_response.status_code == 201

    # extract feedback_id from registration response json
    feedback_id = feedback_response.json()["feedback_id"]

    return {"feedback_id": feedback_id, "event_id": event_id}


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    clear_test_collections()
=======
# pylint: disable=redefined-outer-name
#       - this is how we use fixtures internally so this throws false positives
"""
pytest `conftest.py` file that holds global fixtures for tests
"""
import os
import random
import logging
import datetime
from enum import Enum
from uuid import uuid4
from typing import List, Callable, Dict, Any

import pytest
from asgiref.sync import async_to_sync
from faker import Faker
from fastapi.testclient import TestClient

from app import app
from config.db import database_client, clear_test_collections

import models.users as user_models
import models.events as event_models
import models.feedback as feedback_models

import util.users as user_utils
import util.events as event_utils
import util.feedback as feedback_utils

client = TestClient(app)


# startup process
def pytest_configure(config):
    """
    Startup process for tests.

    The change of the testing flag **MUST** be the first statement done here,
    any other statements for setup must be placed afterwards.
    """
    os.environ['_called_from_test'] = 'True'
    database_client.connect_to_mongo()
    logging.getLogger("faker").setLevel(logging.ERROR)
    del config  # unused variable


def pytest_unconfigure(config):  # pytest: disable=unused-argument
    """
    Shutdown process for tests, mostly involving the wiping of database
    documents and resetting the testing environment flag.
    """
    os.environ['_called_from_test'] = 'False'
    clear_test_collections()
    database_client.close_connection_to_mongo()
    del config  # unused variable


@pytest.fixture(autouse=True)
def run_around_tests():
    """
    Clears all documents in the test collections after every single test.
    """
    yield
    clear_test_collections()


@pytest.fixture(scope='function')
def registered_user() -> user_models.User:
    """
    Fixture that generates a random valid user and registers it directly to
    the database through the `util` method.

    Returns the original user object.
    """
    user_data = generate_random_user()
    async_to_sync(user_utils.register_user)(user_data)
    return user_data


@pytest.fixture(scope='function')
def unregistered_user() -> user_models.User:
    """
    Fixture that generates a valid user and returns it
    WITHOUT registering it to the database first.
    """
    return generate_random_user()


@pytest.fixture(scope='function')
def user_registration_form() -> user_models.UserRegistrationForm:
    """
    Returns an unregistered, random, valid user registration form object.
    """
    user_dict = generate_random_user().dict()
    return user_models.UserRegistrationForm(**user_dict)


def generate_random_user() -> user_models.User:
    """
    Uses a fake data generator to generate a unique
    and valid user object.
    """
    fake = Faker()
    user_data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email()
    }
    return user_models.User(**user_data)


@pytest.fixture(scope='function')
def get_identifier_dict_from_user(
) -> Callable[[user_models.User], Dict[str, Any]]:
    """
    Takes data from a registered user and returns a dict with
    user identifier data to be passed as a json dict
    """
    def _user_data_to_json(user_data: user_models.User):
        user_email = user_data.email
        return {"email": user_email}

    return _user_data_to_json


@pytest.fixture(scope='function')
def registered_event() -> event_models.Event:
    """
    Fixture that generates a random event and then directly registers it
    using an `util.events` method.

    Returns the original event object
    """
    event_data = generate_random_event()
    async_to_sync(event_utils.register_event)(event_data)

    return event_data


@pytest.fixture(scope='function')
def unregistered_event() -> event_models.Event:
    """
    Same as the registered event method but skips the actual
    database insertion step.

    Returns original unregistered object.
    """
    event_data = generate_random_event()
    return event_data


@pytest.fixture(scope='function')
def registered_event_factory() -> Callable[[], None]:
    """
    Returns a function that registers an event. Useful for when we want multiple
    event registration calls without caching the result.
    """
    def _register_event():
        event_data = generate_random_event()
        async_to_sync(event_utils.register_event)(event_data)
        return event_data

    return _register_event


@pytest.fixture(scope='function')
def event_registration_form() -> event_models.EventRegistrationForm:
    """
    Creates and returns a random valid event registration form object
    """
    event_data = generate_random_event().dict()
    return event_models.EventRegistrationForm(**event_data)


def generate_random_event() -> event_models.Event:
    """
    Uses a fake data generator to generate a unique
    and valid event object.
    """
    fake = Faker()
    event_data = {
        "title": fake.text(),
        "description": fake.text(),
        "date": str(datetime.datetime.now()),
        "tag": get_random_enum_member_value(event_models.EventTagEnum),
        "location": {
            "latitude": float(fake.latitude()),
            "longitude": float(fake.longitude()),
        },
        "max_capacity": random.randint(1, 100),
        "public": random.choice([True, False]),
        "attending": [],
        "upvotes": 0,
        "comment_ids": [],
        "rating": random.randint(0, 5),
        "status": get_random_enum_member_value(event_models.EventStatusEnum),
        "creator_id": fake.uuid4()
    }
    return event_models.Event(**event_data)


@pytest.fixture(scope="function")
def registered_feedback(
        registered_event: event_models.Event) -> feedback_models.Feedback:
    """
    Uses a previously declared fixture that returns a registered event in
    order to randomly generate a feedback object for it.

    Returns the original feedback object.
    """
    event_id = registered_event.get_id()
    feedback_data = generate_random_feedback(event_id)
    async_to_sync(feedback_utils.register_feedback)(feedback_data)

    return feedback_data


@pytest.fixture(scope="function")
def unregistered_feedback_object() -> feedback_models.Feedback:
    """
    Creates a random feedback object that is neither registered,
    not tied to a valid event, then returns it.
    """
    event_id = str(uuid4())
    feedback_data = generate_random_feedback(event_id)
    return feedback_data


def generate_random_feedback(
        event_id: event_models.EventId) -> feedback_models.Feedback:
    """
    Generates a random feedback for the given event.
    """
    fake = Faker()
    feedback_data = {
        "event_id": event_id,
        "comment": fake.text(),
    }
    return feedback_models.Feedback(**feedback_data)


def get_random_enum_member_value(enum_class: Enum) -> Enum:
    """
    Given an Enum class, returns a single, valid, random member of the class.
    """
    possible_tags = get_list_of_values_from_enum(enum_class)
    random_tag = random.choice(possible_tags)
    return random_tag


def get_list_of_values_from_enum(enum_class: Enum) -> List[Enum]:
    """
    Given an Enum, returns a list of all possible values of the class.
    """
    enum_values = enum_class.__members__
    return [enum_class(x) for x in enum_values]
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
