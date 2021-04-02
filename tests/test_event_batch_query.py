# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Holds endpoint tests for the batch event query requests.
"""
import logging
from typing import Dict, List, Any, Callable
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

import models.events as event_models

from app import app

client = TestClient(app)


def check_query_events_resp_valid(
        response: HTTPResponse,
        query_form: event_models.BatchEventQueryModel) -> bool:
    """
    Checks that the server response is good and valid for the given
    request form.
    """
    try:
        assert response.status_code == 200
        assert response.json()
        assert "events" in response.json()

        list_of_events = response.json()["events"]
        assert check_list_of_events_returned_matches_query_form(
            list_of_events, query_form)

        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}, resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_list_of_events_returned_matches_query_form(  # pylint: disable=invalid-name
        list_of_events: List[event_models.Event],
        query_form: event_models.BatchEventQueryModel) -> bool:
    """
    Checks that the list of events returned by the endpoint is valid and
    adheres to the query filters given by the client's query form.
    """
    try:
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}, resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_batch_query_endpoint_url() -> str:
    """
    Returns endpoint url string
    """
    return "/events/find/batch"


def get_json_dict_from_query_form(
        query_form: event_models.BatchEventQueryModel) -> Dict[str, Any]:
    """
    Returns the request-ready dict to be used as JSON data
    for the batch query endpoint. Created from a query form object.
    """
    pass


class TestBatchEventQueryEndpoint:
    def test_register_many_query_ok(
            self, register_an_event: Callable[[], event_models.Event]):
        """
        Registers a few valid events and then tries to query for
        them with a valid query form, expecting success.
        """
        for _ in range(10):
            register_an_event()

        json_data = get_json_dict_from_query_form(query_form)
        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
