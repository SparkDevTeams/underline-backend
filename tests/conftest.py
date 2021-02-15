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
