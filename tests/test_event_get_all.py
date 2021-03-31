# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Holds endpoint tests for getting all events in the database
"""
from typing import Callable

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app

client = TestClient(app)


def get_all_events_endpoint_url() -> str:
    """
    Returns endpoint url string
    """
    return "/events/find/all"


class TestGetAllEvents:
    def test_get_all_events_success(self,
                                    registered_event_factory: Callable[[],
                                                                       None],
                                    check_list_return_events_valid:
                                    Callable[[HTTPResponse, int], bool]):
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
        assert check_list_return_events_valid(response, num_events)

    def test_no_events_query_success(self, check_list_return_events_valid:
                                        Callable[[HTTPResponse, int], bool]):
        """
        Tries to gather all of the events in the database without
        registering any, expecting an empty response.
        """
        endpoint_url = get_all_events_endpoint_url()
        response = client.get(endpoint_url)
        assert check_list_return_events_valid(response, 0)
