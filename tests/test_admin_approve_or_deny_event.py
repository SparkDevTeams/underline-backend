# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for Admin Queue of Events.
"""
import logging
from typing import Any, Dict, Callable

from asgiref.sync import async_to_sync
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

import util.events as event_utils
import models.events as event_models

from app import app

client = TestClient(app)


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
        assert response.status_code == 204
        assert check_event_not_in_queue(params_sent["event_id"])
        assert check_event_enum_changed(params_sent["event_id"],
                                        params_sent["approve_bool"])
        assert not response.json()
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
    enum_to_compare = enum_class.approved if approved else enum_class.denied

    event = async_to_sync(event_utils.get_event_by_id)(event_id)
    return event.approval == enum_to_compare.name  # pylint: disable=no-member


def get_params_dict_for_endpoint(
        approved: bool, event_id: event_models.EventId) -> Dict[Any, Any]:
    """
    Creates the parameters dict for the request.
    """
    query_data = {"approve_bool": approved, "event_id": event_id}
    return query_data


class TestAdminEventsQueue:
    def test_approve_event_in_queue(self,
                                    unapproved_event_factory: Callable[[],
                                                                       None],
                                    valid_admin_header: Dict[str, Any]):
        """
        Tries to create and approve an event in a queue, expecting
        the data to change as well as a success code.
        """
        event = unapproved_event_factory()
        event_id = event.get_id()

        approved_bool = True
        params = get_params_dict_for_endpoint(approved_bool, event_id)

        endpoint_url = get_approval_endpoint_url_str()
        response = client.get(endpoint_url,
                              params=params,
                              headers=valid_admin_header)

        assert check_endpoint_response_valid(response, params)

    def test_deny_event_in_queue(self,
                                 unapproved_event_factory: Callable[[], None],
                                 valid_admin_header: Dict[str, Any]):
        """
        Tries to create and deny an event in a queue
        """
        event = unapproved_event_factory()
        event_id = event.get_id()

        approved_bool = True
        params = get_params_dict_for_endpoint(approved_bool, event_id)

        endpoint_url = get_approval_endpoint_url_str()
        response = client.get(endpoint_url,
                              params=params,
                              headers=valid_admin_header)

        assert check_endpoint_response_valid(response, params)

    def test_try_send_request_no_event(self, random_valid_uuid4_str: str,
                                       valid_admin_header: Dict[str, Any]):
        """
        Try to interact with an event that does not exist,
        expecting failure.
        """
        event_id = random_valid_uuid4_str

        approved_bool = True
        params = get_params_dict_for_endpoint(approved_bool, event_id)

        endpoint_url = get_approval_endpoint_url_str()
        response = client.get(endpoint_url,
                              params=params,
                              headers=valid_admin_header)

        assert not check_endpoint_response_valid(response, params)
        assert response.status_code == 404

    def test_user_not_admin_failure(self,
                                    unapproved_event_factory: Callable[[],
                                                                       None],
                                    valid_header_dict_with_user_id: Dict[str,
                                                                         Any]):
        """
        Tries to get the events but using a regular user's token instead of
        an admin token, expecting auth failure.
        """
        event = unapproved_event_factory()
        event_id = event.get_id()

        approved_bool = True
        params = get_params_dict_for_endpoint(approved_bool, event_id)

        endpoint_url = get_approval_endpoint_url_str()
        response = client.get(endpoint_url,
                              params=params,
                              headers=valid_header_dict_with_user_id)

        assert not check_endpoint_response_valid(response, params)
        assert response.status_code == 401
