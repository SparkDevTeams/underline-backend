import time
from fastapi.testclient import TestClient
from app import app
from datetime import datetime
import pytest
import logging

client = TestClient(app)


def get_event_location_query(lat, lon, radius):
    query_data = {"lat": lat, "lon": lon, "radius": radius}
    return query_data


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
    def test_events_location_success(self, registered_event):
        query_data = get_event_location_query(75, 75, 5)
        response = client.get("/events/location/", params=query_data)

        assert check_event_locations_response_valid(response)

    def test_events_location_empty_data_failure(self, registered_event):
        response = client.get("/events/location/", params={})

        assert not check_event_locations_response_valid(response)

    def test_events_location_no_events_failure(self, registered_event):
        query_data = get_event_location_query(10, 10, 5)
        response = client.get("/events/location/", params=query_data)

        assert not check_event_locations_response_valid(response)

    def test_events_location_invalid_lat_lon(self, registered_event):
        query_data = get_event_location_query(100, -5, 5)
        response = client.get("/events/location/", params=query_data)

        assert not check_event_locations_response_valid(response)
