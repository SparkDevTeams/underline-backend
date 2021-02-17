import time
from fastapi.testclient import TestClient
from app import app
from datetime import datetime
import pytest
import logging

client = TestClient(app)


def check_event_registration_response_valid(response):
    try:
        assert response.status_code == 201
        assert response.json()
        return True
    except:
        return False


def get_event_form():
    json = {
        "title": "Test Event",
        "description": "Test Description",
        "date": str(datetime.now()),
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
    return json


class TestRegisterEvent:
    def test_register_event_success(self):
        event_form = get_event_form()
        event_response = client.post("/events/register", json=event_form)
        assert check_event_registration_response_valid(event_response)

    def test_register_event_no_data_failure(self):
        event_form = {}
        event_response = client.post("/events/register", json=event_form)
        assert not check_event_registration_response_valid(event_response)

    def test_register_event_bad_data_failure(self):
        event_form = get_event_form()
        # mess up some data for fault injection
        event_form["tag"] = "none"
        event_response = client.post("/events/register", json=event_form)
        assert not check_event_registration_response_valid(event_response)
