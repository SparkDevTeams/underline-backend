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
from typing import Any, Dict, Callable

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from asgiref.sync import async_to_sync
import util.auth as auth
import util.events as events
import models.users as user_models
import models.events as events_models
from app import app

client = TestClient(app)


def get_queue_endpoint_url_str() -> str:
    """
    Returns the endpoint url string
    """
    return "/admin/events_queue"


def get_approval_endpoint_url_str() -> str:
    """
    Returns the endpoint url string
    """
    return "/admin/decide_event"


def check_event_approved(event_id: events_models.EventId) -> bool:
    event = async_to_sync(events.get_event_by_id)(event_id)
    if event.approval == 'approved':
        return True
    return False


def check_event_denied(event_id: events_models.EventId) -> bool:
    event = async_to_sync(events.get_event_by_id)(event_id)
    if event.approval == 'denied':
        return True
    return False


def create_query_data(choice: bool, event_id: events_models.EventId) \
                        -> Dict[Any, Any]:
    query_data = {"choice": choice, "event_id": event_id}
    return query_data


class TestAdminEventsQueue:
    def test_get_all_events_success(
            self, unapproved_event_factory: Callable[[], None],
            check_list_return_events_valid: Callable[[HTTPResponse, int],
                                                     bool],
            valid_admin_header: Dict[str, Any]):
        """
        Registers a random amount of events between a set range,
        then tries to call them back and check them,
        expecting success.
        """
        num_events = 12
        for _ in range(num_events):
            unapproved_event_factory()
        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url, headers=valid_admin_header)
        assert check_list_return_events_valid(response, num_events)

    def test_no_events_query_success(
            self, check_list_return_events_valid: Callable[[HTTPResponse, int],
                                                           bool]):
        """
        Tries to gather all of the events in the database without
        registering any, expecting an empty response.
        """
        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url)
        assert check_list_return_events_valid(response, 0)

    def test_approve_event_in_queue(
            self, registered_admin_factory: Callable[[], user_models.User],
            unapproved_event_factory: Callable[[], None]):
        """
        Tries to create and approve an event in a queue
        """
        admin = registered_admin_factory()
        admin_valid = async_to_sync(auth.get_admin_and_check_existence)(admin)
        if admin_valid:
            event = unapproved_event_factory()
            event_id = event.get_id()
            params = create_query_data(True, event_id)
            endpoint_url = get_approval_endpoint_url_str()
            response = client.post(endpoint_url, params=params)
            assert response.status_code == 200
            assert check_event_approved(event_id)

    def test_deny_event_in_queue(
            self, registered_admin_factory: Callable[[], user_models.User],
            unapproved_event_factory: Callable[[], None]):
        """
        Tries to create and deny an event in a queue
        """
        admin = registered_admin_factory()
        admin_valid = async_to_sync(auth.get_admin_and_check_existence)(admin)
        if admin_valid:
            event = unapproved_event_factory()
            event_id = event.get_id()
            params = create_query_data(False, event_id)
            endpoint_url = get_approval_endpoint_url_str()
            response = client.post(endpoint_url, params=params)
            assert response.status_code == 200
            assert check_event_denied(event_id)
