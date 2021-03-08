# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Holds endpoint tests for searching events in the database
"""
import logging
from typing import List, Dict, Any, Callable

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

import models.events as event_models

from app import app

client = TestClient(app)


def check_search_events_response_valid(  # pylint: disable=invalid-name
        response: HTTPResponse, search_form: event_models.EventSearchForm) -> bool:
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


def search_events_endpoint_url() -> str:
    """
    Returns endpoint url string
    """
    return "/events/search"


class TestSearchEvents:
    def test_search_events_success(self,
                                    registered_event: event_models.Event):
        """
        Registers a random event, then tries to search it back and 
        check it, expecting success.
        """
        event = registered_event()
        event_description = event.description
        event_title = event.title
        endpoint_url = search_events_endpoint_url()
        search_form = event_models.EventSearchForm()
        search_form.keyword = event_title
        response = client.get(endpoint_url, params= search_form)
        assert check_search_events_response_valid(response)
