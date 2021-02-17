import time
from fastapi.testclient import TestClient
from tests.utils_for_tests import register_an_event
from app import app
from datetime import datetime
import pytest
import logging

client = TestClient(app)


def check_get_all_events_response_valid(response, events_registered):
    try:
        assert response.status_code == 200
        assert len(response.json()["events"]) == events_registered
        events = [event for event in response.json()["events"]]
        assert all(["event_id" in event for event in events])
        return True
    except Exception as e:
        logging.debug(f"exception: {e}")
        return False


class TestGetAllEvents:
    def test_get_all_events_success(self):
        # register multiple events
        num_events = 3
        for _ in range(num_events):
            register_an_event()
        response = client.get("/events/find/all")
        assert check_get_all_events_response_valid(response, num_events)

    def test_no_events_empty_query_success(self):
        response = client.get("/events/find/all")
        assert check_get_all_events_response_valid(response, 0)
