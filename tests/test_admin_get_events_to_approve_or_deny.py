# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for Admin Queue of Events.
"""
from typing import Any, Dict, Callable

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
import models.events as event_models
from app import app

client = TestClient(app)


def get_queue_endpoint_url_str() -> str:
    """
    Returns the endpoint url string
    """
    return "/admin/events_queue"


class TestAdminGetEventsQueue:
    def test_get_all_events_success(
            self, unapproved_event_factory: Callable[[], None],
            check_list_return_events_valid: Callable[[HTTPResponse, int],
                                                     bool],
            registered_event_factory: Callable[[], event_models.Event],
            valid_admin_header: Dict[str, Any]):
        """
        Registers a random amount of events between a set range,
        then tries to call them back and check them,
        expecting success.
        """
        num_events = 12
        for _ in range(num_events):
            unapproved_event_factory()

        num_events_to_not_show = 5
        for _ in range(num_events):
            registered_event_factory()

        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url, headers=valid_admin_header)
        assert check_list_return_events_valid(response, num_events)

    def test_no_events_query_success(
            self, check_list_return_events_valid: Callable[[HTTPResponse, int],
                                                           bool],
            valid_admin_header: Dict[str, Any]):
        """
        Tries to gather all of the events in the database without
        registering any, expecting an empty response.
        """
        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url, headers=valid_admin_header)
        assert check_list_return_events_valid(response, 0)

    def test_user_not_admin_failure(
            self, unapproved_event_factory: Callable[[], None],
            check_list_return_events_valid: Callable[[HTTPResponse, int],
                                                     bool],
            valid_header_dict_with_user_id: Dict[str, Any]):
        """
        Tries to get the events but using a regular user's token instead of
        an admin token, expecting auth failure.
        """
        num_events = 12
        for _ in range(num_events):
            unapproved_event_factory()
        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url,
                              headers=valid_header_dict_with_user_id)
        assert response.status_code == 401
        assert not check_list_return_events_valid(response, num_events)
