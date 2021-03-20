# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for user update calls.
"""
import asyncio
from typing import Dict, Any, Set
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.users as user_models
import util.users as user_utils

client = TestClient(app)


def get_set_of_attributes_expected_to_be_different() -> Set[Any]:
    return {"identifier"}


#  todo: review this. Not sure if it's being extensible or redundant
def get_set_of_attributes_expected_to_be_hashed() -> Set[Any]:
    return {"password"}


def get_update_user_endpoint_url() -> str:
    """
    Returns the url string for the user update endpoint
    """
    return "/users/update"


# todo: it'd be nice to have random invalid data generated here
def get_valid_update_request_from_user(
        user_data: user_models.User) -> Dict[str, Any]:
    """
    Generates an arbitrary valid JSON payload dict to be used in
    the update user call from a user object.
    """
    user_id = user_data.get_id()
    payload_dict = {
        "identifier": {
            "user_id": user_id
        },
        "first_name": "stringy",
        "email": "user@example456.com",
        "password": "string2"
    }

    return payload_dict


# todo: it'd be nice to have a refactor that generates random invalid fields
def get_invalid_update_request_from_user(
        user_data: user_models.User) -> Dict[str, Any]:
    """
    Generates an arbitrary invalid JSON payload dict to be used in
    the update user call from a user object.
    Current implementation is just to give an invalid first name,
    containing a numeric digit.
    """
    user_id = user_data.get_id()
    payload_dict = {
        "identifier": {
            "user_id": user_id
        },
        "first_name": "stringy2",
        "email": "user@example456.com",
        "password": "string2"
    }

    return payload_dict


def get_valid_update_request_nonexistent_user() -> Dict[str, Any]:
    """
    Generates a valid update request for a nonexistent user.
    """
    user_id = "20354d7a-e4fe-47af-8ff6-187bca92f3f9"
    payload_dict = {
        "identifier": {
            "user_id": user_id
        },
        "first_name": "stringy",
        "email": "user@example456.com",
        "password": "string2"
    }

    return payload_dict


def get_update_request_no_data() -> Dict[str, Any]:
    """
    Generates an invalid request that contains no information
    """
    payload_dict = {}
    return payload_dict


def check_response_valid_user_update(response: HTTPResponse) -> bool:
    """
    Checks if response code to successful user update is valid
    """
    breakpoint()
    return response.status_code == 200


def check_response_update_invalid_fields(response: HTTPResponse) -> bool:
    """
    Checks if response code to user update with illegal fields is valid
    """
    breakpoint()
    return response.status_code == 422


def check_response_update_nonexistent_user(response: HTTPResponse) -> bool:
    """
    Checks if response code to user update with incorrect identifier is valid
    """
    breakpoint()
    return response.status_code == 404


def check_response_no_data_given(response: HTTPResponse) -> bool:
    """
    Checks if response code to user update with no data provided is valid
    """
    breakpoint()
    return response.status_code == 422


def check_fields_updated_correctly(
        old_user_data: user_models.User,
        updated_data_json: Dict[str, Any]) -> bool:
    """
    todo: refactor: loop through new user fields. If field is in updated_data_json, expect that. If not, expect
    it to be whatever it is in the old user model.
    """
    """
    Checks the updated user response VS the original user data
    and returns True if the operation outcome was valid, else False.
    """

    new_user_data = get_user_data_from_user_model(old_user_data)
    unchecked_items = old_user_data.dict()

    # todo: check last name field WASN'T changed
    for k, v in updated_data_json.items():
        # fixme: complex code, don't like
        if new_user_data.dict().get(k) != v \
                and k not in get_set_of_attributes_expected_to_be_different():
            if k in get_set_of_attributes_expected_to_be_hashed():
                if not new_user_data.check_password(v):
                    return False
            else:
                return False
        # trims down a list to values that SHOULDN'T have been updated
        if k in unchecked_items:
            del unchecked_items[k]

    for k, v in unchecked_items.items():
        if new_user_data.dict().get(k) != v:
            return False
    return True


def check_fields_not_updated(old_user_data: user_models.User) -> bool:
    """
    Checks fields in Mongo are the same as they are in the provided user data.
    """
    new_user_data = get_user_data_from_user_model(old_user_data)

    for k, v in old_user_data.dict().items():
        if k in get_set_of_attributes_expected_to_be_hashed():
            if not new_user_data.check_password(v):
                return False
        else:
            if new_user_data.dict().get(k) != v:
                return False

    return True


def get_user_data_from_user_model(
        old_user_data: user_models.User) -> user_models.User:
    """
    Takes a user object and returns a new
    User object based off a fresh Mongo query
    """
    user_identifier = user_models.UserIdentifier(user_id=old_user_data.get_id())
    new_user_data = asyncio.run(
        user_utils.get_user_info_by_identifier(user_identifier))
    return new_user_data


def get_update_response_from_payload(
        update_json_payload: Dict[str, Any]) -> HTTPResponse:
    endpoint_url = get_update_user_endpoint_url()
    return client.patch(endpoint_url, json=update_json_payload)


class TestUserUpdate:
    def test_valid_user_update(
            self, registered_user: user_models.User):
        """
        Tries to update an existing user data with incoming valid data
        """
        update_json_payload = get_valid_update_request_from_user(
            registered_user)
        response = get_update_response_from_payload(
            update_json_payload)

        assert check_response_valid_user_update(
            response)
        assert check_fields_updated_correctly(
            registered_user, update_json_payload)

    def test_update_user_with_invalid_fields(
            self, registered_user: user_models.User):
        """
        Tries to update an existing user data with incoming invalid data
        """
        update_json_payload = get_invalid_update_request_from_user(
            registered_user)
        response = get_update_response_from_payload(
            update_json_payload)

        assert check_response_update_invalid_fields(response)
        assert check_fields_not_updated(registered_user)

    def test_attempt_update_nonexistent_user(self):
        """
        Tries to update a nonexistent user, using valid update fields
        """
        update_json_payload = get_valid_update_request_nonexistent_user()
        response = get_update_response_from_payload(update_json_payload)

        assert check_response_update_nonexistent_user(response)

    def test_attempt_update_no_data_given(self):
        """
        Tries to pass an empty dict as a json payload to the update endpoint
        """
        update_json_payload = get_update_request_no_data()
        response = get_update_response_from_payload(update_json_payload)

        assert check_response_no_data_given(response)
