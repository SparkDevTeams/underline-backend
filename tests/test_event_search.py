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
        response: HTTPResponse, search_form) -> bool:
    """
    Takes the server response for the endpoint and checks
    if the event returned contains the keyword
    """
    try:
        assert response.status_code == 200
        events = response.json()["events"]
        for event in events:
            assert event["title"] == search_form["keyword"] or event["description"] == search_form["keyword"]
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}, resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def search_events_endpoint_url() -> str:
    """
    Returns endpoint url string
    """
    return "/events/search"

class TestSearchEvents:
    def test_search_events_by_title(self,
                                    registered_event: event_models.Event):
        """
        Registers a random event, then tries to search it back and
        check it, expecting success.
        """
        search_form = event_models.EventSearchForm(
            keyword=registered_event.title)
        endpoint_url = search_events_endpoint_url()
        response = client.post(endpoint_url, json = search_form.dict())
        assert check_search_events_response_valid(response, search_form.dict())

    def test_search_events_by_description(self,
                                    registered_event: event_models.Event):
        """
        Registers a random event, then tries to search it back by its description
        and check it, expecting success.
        """
        search_form = event_models.EventSearchForm(
            keyword=registered_event.description)
        endpoint_url = search_events_endpoint_url()
        response = client.post(endpoint_url, json = search_form.dict())
        assert check_search_events_response_valid(response, search_form.dict())

    def test_search_events_not_found(self):
        """
        Tries to search for an event with a random string, expecting an empty response
        error.
        """
        search_form = event_models.EventSearchForm(
            keyword="Random string")
        endpoint_url = search_events_endpoint_url()
        response = client.post(endpoint_url, json = search_form.dict())
        logging.debug(response.json())
        assert len(response.json()["events"]) == 0
