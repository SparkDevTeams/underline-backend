<<<<<<< HEAD
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
=======
# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Holds endpoint tests for getting all events in the database
"""
import logging
import random
from typing import List, Dict, Any, Callable

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app

client = TestClient(app)


def check_get_all_events_response_valid(  # pylint: disable=invalid-name
        response: HTTPResponse, total_events_registered: int) -> bool:
    """
    Takes the server response for the endpoint and the total
    amount of events registered, and returns the boolean
    status of the validity of the response.
    """
    try:
        assert response.status_code == 200
        assert "events" in response.json()

        events_list = response.json()["events"]
        assert len(events_list) == total_events_registered
        assert check_events_list_valid(events_list)

        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}, resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_events_list_valid(events_list: List[Dict[str, Any]]) -> bool:
    """
    Iterates over the list of returned events and checks that they're all valid.
    """
    try:
        for event in events_list:
            assert "_id" in event
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}"
        logging.debug(debug_msg)
        return False


def get_all_events_endpoint_url() -> str:
    """
    Returns endpoint url string
    """
    return "/events/find/all"


class TestGetAllEvents:
    def test_get_all_events_success(self,
                                    registered_event_factory: Callable[[],
                                                                       None]):
        """
        Registers a random amount of events between a set range,
        then tries to call them back and check them,
        expecting success.
        """
        num_events = random.randint(5, 20)
        for _ in range(num_events):
            registered_event_factory()
        endpoint_url = get_all_events_endpoint_url()
        response = client.get(endpoint_url)
        assert check_get_all_events_response_valid(response, num_events)

    def test_no_events_query_success(self):
        """
        Tries to gather all of the events in the database without
        registering any, expecting an empty response.
        """
        endpoint_url = get_all_events_endpoint_url()
        response = client.get(endpoint_url)
        assert check_get_all_events_response_valid(response, 0)
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
