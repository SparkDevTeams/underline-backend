import time
from fastapi.testclient import TestClient
from app import app
from datetime import datetime
import pytest
import json
import logging

client = TestClient(app)

def get_event_location_form():
    user_data = {
        "lat": 75.0,
        "lon": 75.0,
        "radius": 5
    }
    return user_data

def test_register_event_success(registered_event):
    params = {  "title": "Test Event",
                "description": "Test event",
                "date": str(datetime.now()),
                "tag": "sporting_events",
                "location": {   
                    "latitude": 75.0,
                    "longitude": 75.0
                            },
                "max_capacity": 10,
                "public": False,
                "attending":[],
                "upvotes": 0,
                "comment_ids":[],
                "rating": 5.0,
                "status":"active",
                "creator_id":"0"
            }
    response = client.post("/events/register", json=params)
    assert response.status_code == 201

def check_event_locations_response_valid(response):
    test1 = response.status_code == 201
    
    response_json = response.json()

    if "events" in response_json:
        events = response_json["events"]
        test2 = len(events) > 0
    else:
        test2 = False

    return all([test1, test2])

class TestEventsLocation:
    def test_events_location_success(self):
        user_data = get_event_location_form()
        response = client.get("/events/location/", params=user_data)

        assert check_event_locations_response_valid(response)

    def test_events_location_empty_data_failure(self):
        response = client.get("/events/location/", params={})

        assert not check_event_locations_response_valid(response)