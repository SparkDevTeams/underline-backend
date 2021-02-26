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
        num_events = 12
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
