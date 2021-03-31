# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=invalid-name
#       - this module has some pretty verbose names,
#         shrinking them feels worse than disabling this lint.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for Admin Queue of Events.
"""
import logging
import datetime
from typing import Dict, Any, Callable

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.users as user_models
import models.events as event_models

client = TestClient(app)

def get_queue_endpoint_url_str() -> str:
    """
    Returns the endpoint url string
    """
    return "/admin/events_queue"

class TestAdminEventsQueue:
    def test_get_all_events_success(self,
                                    registered_unapproved_event_factory: Callable[[],
                                                                       None],
                                    check_list_of_returned_events_valid: Callable[[HTTPResponse, int], bool]):
        """
        Registers a random amount of events between a set range,
        then tries to call them back and check them,
        expecting success.
        """
        num_events = 12
        for _ in range(num_events):
            registered_unapproved_event_factory()
        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url)
        assert check_list_of_returned_events_valid(response, num_events)

    def test_no_events_query_success(self, check_list_of_returned_events_valid: Callable[[HTTPResponse, int], bool]):
        """
        Tries to gather all of the events in the database without
        registering any, expecting an empty response.
        """
        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url)
        assert check_list_of_returned_events_valid(response, 0)

