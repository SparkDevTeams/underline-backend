# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=invalid-name
#       - this module has some pretty verbose names,
#         shrinking them feels worse than disabling this lint.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for registering events.
"""
import logging
import datetime
from typing import Dict, Any, Callable

from asgiref.sync import async_to_sync
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import util.users as user_utils
import util.events as event_utils
import models.users as user_models
import models.events as event_models

client = TestClient(app)


def check_event_registration_response_valid(
        response: HTTPResponse, user_id: user_models.UserId) -> bool:
    """
    Returns the boolean status of the validity of the raw
    http server response.

    Also validates that the user had the event_id added to
    it's list of `events_created`.
    """
    try:
        assert response.status_code == 201
        assert response.json()
        event_id = response.json().get("event_id")
        assert check_event_id_added_to_user(event_id, user_id)
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_event_id_added_to_user(event_id: event_models.EventId,
                                 user_id: user_models.UserId) -> bool:
    """
    Checks that the event was added to the user's `events_created` list
    """
    try:
        user_identifier = user_models.UserIdentifier(user_id=user_id)
        user_from_db = async_to_sync(
            user_utils.get_user_info_by_identifier)(user_identifier)
        assert event_id in user_from_db.events_created
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}.\
                    event_id: {event_id}, user_id: {user_id}"

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


def get_invalid_json_from_reg_form(
        event_form: event_models.EventRegistrationForm) -> Dict[str, Any]:
    """
    Takes a valid event form object and returns an invalid json payload from it
    """
    event_dict = event_form.dict()
    # make data dirty by reversing the order of values with their keys
    values = list(event_dict.values())[::-1]
    for key, value in zip(event_dict.keys(), values):
        event_dict[key] = value

    # we still have to make datetimes valid
    set_datetimes_to_str_in_place(event_dict)

    return event_dict


def set_datetimes_to_str_in_place(json_dict: Dict[str, Any]) -> None:
    """
    Sets all `datetime` instances to `str(datetime)` in-place.
    """
    for key, value in json_dict.items():
        if isinstance(value, datetime.datetime):
            json_dict[key] = str(value)

def check_admin_event_registration(response: HTTPResponse) -> bool:
    """
    Validates that an event registered by an admin, is public and
    approved instantly upon creation
    """
    try:
        assert response.json()
        event_id = response.json().get("event_id")
        event = async_to_sync(event_utils.get_event_by_id)(event_id)
        is_public = event.public
        approval = event.approval
        assert is_public
        assert approval == "approved"
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False

    return True

class TestRegisterEvent:
    def test_register_event_success(
        self, event_registration_form: event_models.EventRegistrationForm,
        get_header_dict_from_user_id: Callable[[user_models.User], Dict[str,
                                                                        Any]]):
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
        assert check_event_registration_response_valid(event_response,
                                                       creator_user_id)

    def test_register_event_no_data_failure(
        self, event_registration_form: event_models.EventRegistrationForm,
        get_header_dict_from_user_id: Callable[[user_models.User], Dict[str,
                                                                        Any]]):
        """
        Tries to register an event while sending no data,
        expecting failure.
        """
        creator_user_id = event_registration_form.creator_id
        headers = get_header_dict_from_user_id(creator_user_id)

        empty_event_form = {}

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url,
                                     json=empty_event_form,
                                     headers=headers)

        assert not check_event_registration_response_valid(
            event_response, creator_user_id)
        assert event_response.status_code == 422

    def test_register_event_bad_data_failure(
        self, event_registration_form: event_models.EventRegistrationForm,
        get_header_dict_from_user_id: Callable[[user_models.User], Dict[str,
                                                                        Any]]):
        """
        Tries to register an event with a faulty piece of data,
        expecting a 422 failure.
        """
        creator_user_id = event_registration_form.creator_id
        headers = get_header_dict_from_user_id(creator_user_id)

        invalid_event_json = get_invalid_json_from_reg_form(
            event_registration_form)

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url,
                                     json=invalid_event_json,
                                     headers=headers)

        assert not check_event_registration_response_valid(
            event_response, creator_user_id)
        assert event_response.status_code == 422

    def test_register_nonexistent_user(
        self, random_valid_uuid4_str: str,
        event_registration_form: event_models.EventRegistrationForm,
        get_header_dict_from_user_id: Callable[[user_models.User], Dict[str,
                                                                        Any]]):
        """
        Attempts to register a valid event but with a nonexistent user,
        expecting 404 failure.
        """
        # change creator id in event and header to a random id
        nonexistent_user_id = random_valid_uuid4_str
        event_registration_form.creator_id = nonexistent_user_id
        headers = get_header_dict_from_user_id(nonexistent_user_id)

        event_form_json = get_json_from_event_reg_form(event_registration_form)

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url,
                                     json=event_form_json,
                                     headers=headers)
        assert not check_event_registration_response_valid(
            event_response, nonexistent_user_id)
        assert event_response.status_code == 404

    def test_bad_header_creator_id(
        self, registered_user: user_models.User,
        event_registration_form: event_models.EventRegistrationForm,
        get_header_dict_from_user: Callable[[user_models.User], Dict[str,
                                                                     Any]]):
        """
        Attempts to register a valid event, but sends in an erroneous
        header containing the ID for a different, valid user.
        Expects 401 auth error.
        """
        wrong_user_header = get_header_dict_from_user(registered_user)

        event_form_json = get_json_from_event_reg_form(event_registration_form)

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url,
                                     json=event_form_json,
                                     headers=wrong_user_header)
        assert not check_event_registration_response_valid(
            event_response, registered_user.get_id())
        assert event_response.status_code == 401

    def test_admin_register_event_success(
        self, admin_event_registration_form: event_models.EventRegistrationForm,
        get_header_dict_from_user_id: Callable[[user_models.User], Dict[str,
                                                                        Any]]):
        """
        Attempts to register a valid event, expecting success.
        """
        creator_user_id = admin_event_registration_form.creator_id
        headers = get_header_dict_from_user_id(creator_user_id)

        event_form_json = get_json_from_event_reg_form(\
                                                admin_event_registration_form)

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url,
                                     json=event_form_json,
                                     headers=headers)
        assert check_event_registration_response_valid(event_response,
                                                       creator_user_id)
        assert check_admin_event_registration(event_response)
