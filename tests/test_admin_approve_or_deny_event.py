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
from asgiref.sync import async_to_sync
import util.auth as auth
import util.events as events
import models.users as user_models
import models.events as event_models
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


def check_endpoint_response_valid(response: HTTPResponse,
                                  params_sent: Dict[str, Any]) -> bool:
    """
    Given the HTTP response from server, and the request sent
    alongside it, checks that the event decision was taken and
    that the events collection and event queue reflect the transaction.
    """
    try:
        assert response.status_code == 200
        assert check_event_not_in_queue(params_sent["event_id"])
        assert check_event_enum_changed(params_sent["event_id"],
                                        params_sent["approved"])
        assert response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_event_not_in_queue(event_id: event_models.EventId) -> bool:
    """
    Given an event_id, checks that the event is not found in
    the events_queue database
    """
    event_exists = async_to_sync(
        event_utils.check_if_event_in_approval_queue_by_id)(event_id)
    return not event_exists


def check_event_enum_changed(event_id: event_models.EventId,
                             approved: bool) -> bool:
    """
    Given the event id and the decision, checks that the enum was properly
    set on the event document.
    """
    enum_class = event_models.EventApprovalEnum
    enum_to_compare = enum_class.approved.name if approved else enum_class.denied.name

    event = async_to_sync(events.get_event_by_id)(event_id)
    return event.approval == enum_to_compare


def get_params_dict_for_endpoint(
        choice: bool, event_id: event_models.EventId) -> Dict[Any, Any]:
    """
    Creates the parameters dict for the request.
    """
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
                                                           bool],
            valid_admin_header: Dict[str, Any]):
        """
        Tries to gather all of the events in the database without
        registering any, expecting an empty response.
        """
        endpoint_url = get_queue_endpoint_url_str()
        response = client.get(endpoint_url)
        assert check_list_return_events_valid(response, 0)

    def test_approve_event_in_queue(
            self, registered_admin_factory: Callable[[], user_models.User],
            unapproved_event_factory: Callable[[], None],
            valid_admin_header: Dict[str, Any]):
        """
        Tries to create and approve an event in a queue
        """
        admin = registered_admin_factory()
        admin_valid = async_to_sync(auth.get_admin_and_check_existence)(admin)
        if admin_valid:
            event = unapproved_event_factory()
            event_id = event.get_id()
            params = get_params_dict_for_endpoint(True, event_id)
            endpoint_url = get_approval_endpoint_url_str()
            response = client.post(endpoint_url, params=params)
            assert response.status_code == 200
            assert check_event_approved(event_id)

    def test_deny_event_in_queue(
            self, registered_admin_factory: Callable[[], user_models.User],
            unapproved_event_factory: Callable[[], None],
            valid_admin_header: Dict[str, Any]):
        """
        Tries to create and deny an event in a queue
        """
        event = unapproved_event_factory()
        event_id = event.get_id()
        params = get_params_dict_for_endpoint(False, event_id)
        endpoint_url = get_approval_endpoint_url_str()
        response = client.post(endpoint_url, params=params)
        assert response.status_code == 200
        assert check_event_denied(event_id)
