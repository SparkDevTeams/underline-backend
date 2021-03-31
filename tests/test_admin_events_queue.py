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


def check_event_registration_response_valid(response: HTTPResponse) -> bool:
    """
    Returns the boolean status of the validity of the raw
    http server response.
    """
    try:
        assert response.status_code == 201
        assert response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_reg_event_endpoint_url_str() -> str:
    """
    Returns the endpoint url string
    """
    return "/events/register"


def get_json_from_event_reg_form(
        event_form: event_models.EventRegistrationForm) -> Dict[str, Any]:
    """
    Creates and returns a valid json payload from an event registration form

    Turns all `datetimes` to `str(datetimes)` in place so they can be
    JSON serialized.
    """
    json_dict = event_form.dict()
    set_datetimes_to_str_in_place(json_dict)

    return json_dict


def set_datetimes_to_str_in_place(json_dict: Dict[str, Any]) -> None:
    """
    Sets all `datetime` instances to `str(datetime)` in-place.
    """
    for key, value in json_dict.items():
        if isinstance(value, datetime.datetime):
            json_dict[key] = str(value)


class TestAdminEventsQueue:
    def test_approve_event_success(
        self, event_registration_form: event_models.EventRegistrationForm,
        get_header_dict_from_user_id: Callable[[user_models.User],
                                                           Dict[str, Any]]):
        """
        Attempts to register a valid event, expecting success.
        """
        creator_user_id = event_registration_form.creator_id
        headers = get_header_dict_from_user_id(creator_user_id)

        event_form_json = get_json_from_event_reg_form(event_registration_form)

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url,
                                     json=event_form_json,
                                     headers=headers)
        assert check_event_registration_response_valid(event_response)