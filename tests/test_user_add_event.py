# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for user add event calls.
"""
import asyncio
from typing import Dict, Any, Callable
from requests.models import Response as HTTPResponse
from fastapi.testclient import TestClient

import models.users as user_models
import models.events as event_models
import models.commons as common_models
import util.users as user_utils
import util.auth as auth_utils
from app import app

client = TestClient(app)


def get_add_event_endpoint_url() -> str:
    """
    Returns the url string for the user add event endpoint
    """
    return "/users/add_event"


def get_add_event_payload(event_data: event_models.Event) -> Dict[str, Any]:
    """
    Creates a valid JSON payload to add an event to the user
    """
    add_event_dict = {"event_id": event_data.id}
    return add_event_dict


def get_add_event_header(user_data: user_models.User) -> Dict[str, Any]:
    """
    Creates a valid header dict from a User object
    """
    header_dict = {
        "token": user_utils.get_auth_token_from_user_data(user_data)
    }
    return header_dict


def check_response_valid_add(response: HTTPResponse) -> bool:
    """
    Checks if response code to a valid add is valid
    """
    return response.status_code == 201


def check_response_no_event(response: HTTPResponse) -> bool:
    """
    Checks if a response code to an add with a nonexistent event is valid
    """
    return response.status_code == 404


def check_response_no_user(response: HTTPResponse) -> bool:
    """
    Checks if a response code to add an event with a nonexistent user is valid
    """
    return response.status_code == 404


def check_response_duplicate_add(response: HTTPResponse) -> bool:
    """
    Checks if a response code to add
    """
    return response.status_code == 409


def check_response_no_data(response: HTTPResponse) -> bool:
    """
    Checks if response code to user update with no data provided is valid
    """
    return response.status_code == 422


def check_event_add_success(old_user: user_models.User,
                            event: event_models.Event,
                            new_user: user_models.User) -> bool:
    """
    Compares an old user object with a new one, returns if
    the new object is identical but with one instance of
    the parameterized event's id in the events_visible field
    """
    events_visible = new_user.dict().get("events_visible")
    if event.id not in events_visible:
        return False
    events_visible.remove(event.id)
    new_user.events_visible = events_visible
    return old_user.dict() == new_user.dict()


def get_user_data_from_id(user_id: common_models.UserId) -> user_models.User:
    """
    Returns an updated User object from a UserId
    """
    user_identifier = user_models.UserIdentifier(user_id=user_id)
    return asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))


def get_user_id_from_token_str(token_str: str) -> common_models.UserId:
    """
    Returns a UserId from jwt string representing that User
    """
    return asyncio.run(
        auth_utils.get_user_id_from_header_and_check_existence(
            token=token_str))


class TestUserAddEvent:
    def test_add_twice(self, registered_user: user_models.User,
                       registered_event: event_models.Event,
                       get_header_dict_from_user: Callable[[user_models.User],
                                                           Dict[str, Any]]
                       ):
        """
        Tests adding a valid event to a valid User,
        then tests a second add, expecting the responses
        and state to be correct and identical
        """

        endpoint_url = get_add_event_endpoint_url()
        add_event_payload = get_add_event_payload(registered_event)
        add_event_header = get_header_dict_from_user(registered_user)
        token_str = add_event_header.get("token")
        user_id = get_user_id_from_token_str(token_str)

        old_user_data = get_user_data_from_id(user_id)

        response = client.put(endpoint_url,
                              json=add_event_payload,
                              headers=add_event_header)

        new_user_data = get_user_data_from_id(user_id)

        assert check_response_valid_add(response)
        assert check_event_add_success(
            old_user_data, registered_event, new_user_data)

        # repeat process to ensure multiple calls are handled implicitly
        response = client.put(endpoint_url,
                              json=add_event_payload,
                              headers=add_event_header)

        newer_user_data = get_user_data_from_id(user_id)
        assert check_response_duplicate_add(response)
        assert check_event_add_success(
            old_user_data, registered_event, newer_user_data)
        assert new_user_data == newer_user_data

    def test_add_event_no_event(self, registered_user: user_models.User,
                                unregistered_event: event_models.Event,
                                get_header_dict_from_user: Callable
                                [[user_models.User],
                                 Dict[str, Any]]
                                ):
        """
        Tests calling the endpoint with a correctly formatted
        event id that isn't in the database.
        """
        endpoint_url = get_add_event_endpoint_url()
        add_event_payload = get_add_event_payload(unregistered_event)
        add_event_header = get_header_dict_from_user(registered_user)
        token_str = add_event_header.get("token")
        user_id = get_user_id_from_token_str(token_str)
        old_user_data = get_user_data_from_id(user_id)

        response = client.put(endpoint_url,
                              json=add_event_payload,
                              headers=add_event_header)
        new_user_data = get_user_data_from_id(user_id)

        assert check_response_no_event(response)
        assert old_user_data == new_user_data

    def test_add_event_no_user(self, unregistered_user: user_models.User,
                               registered_event: event_models.Event,
                               get_header_dict_from_user:
                               Callable[[user_models.User],
                                        Dict[str, Any]]
                               ):
        """
        Tests calling the endpoint with a correctly formatted
        user header that isn't in the database.
        """
        endpoint_url = get_add_event_endpoint_url()
        add_event_payload = get_add_event_payload(registered_event)
        add_event_header = get_header_dict_from_user(unregistered_user)
        response = client.put(endpoint_url,
                              json=add_event_payload,
                              headers=add_event_header)
        assert check_response_no_user(response)

    def test_add_event_bad_data(self):
        """
        Tests calling the endpoint with empty header and body
        """
        endpoint_url = get_add_event_endpoint_url()
        empty_payload = {}
        empty_header = {}
        response = client.put(endpoint_url,
                              json=empty_payload,
                              headers=empty_header)
        assert check_response_no_data(response)
