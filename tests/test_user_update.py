# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for user update calls.
"""
import asyncio
from random import randint
from typing import Dict, Any, Callable

from faker import Faker
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.users as user_models
import util.users as user_utils

client = TestClient(app)


def get_update_user_endpoint_url() -> str:
    """
    Returns the url string for the user update endpoint
    """
    return "/users/update"


def get_valid_update_request(user_data: user_models.User) -> Dict[str, Any]:
    """
    Generates an arbitrary valid JSON payload dict to be used in
    the update user call from a user object.
    """
    fake = Faker()
    user_id = user_data.get_id()
    payload_dict = {
        "identifier": {
            "user_id": user_id
        },
        "first_name": fake.first_name(),
        "email": fake.email(),
        "password": fake.password(),
        "image_id": fake.uuid4(),
        "user_links": [fake.url() for _ in range(3)]
    }

    return payload_dict


# todo: it'd be nice to have a refactor that generates random invalid fields
def get_invalid_update_request(user_data: user_models.User) -> Dict[str, Any]:
    """
    Generates an arbitrary invalid JSON payload dict to be used in
    the update user call from a user object.
    Current implementation is just to give an invalid first name,
    containing a numeric digit.
    """
    fake = Faker()
    invalid_name_field = lambda: fake.first_name() + str(randint(5, 10))
    user_id = user_data.get_id()
    payload_dict = {
        "identifier": {
            "user_id": user_id
        },
        "first_name": invalid_name_field(),
        "email": invalid_name_field(),
        "password": invalid_name_field(),
        "image_id": fake.uuid4(),
        "user_links": [invalid_name_field() for _ in range(3)]
    }

    return payload_dict


def get_update_request_no_data() -> Dict[str, Any]:
    """
    Generates an invalid request that contains no information
    """
    payload_dict = {}
    return payload_dict


def check_response_valid_update(response: HTTPResponse) -> bool:
    """
    Checks if response code to successful user update is valid
    """
    return response.status_code == 200


def check_response_invalid_fields(response: HTTPResponse) -> bool:
    """
    Checks if response code to user update with illegal fields is valid
    """
    return response.status_code == 422


def check_response_update_nonexistent(response: HTTPResponse) -> bool:  # pylint: disable=invalid-name
    """
    Checks if response code to user update with incorrect identifier is valid
    """
    return response.status_code == 404


def check_response_no_data(response: HTTPResponse) -> bool:
    """
    Checks if response code to user update with no data provided is valid
    """
    return response.status_code == 422


def check_fields_updated_correctly(old_user_data: user_models.User,
                                   updated_data_json: Dict[str, Any]) -> bool:
    """
    Checks the updated user response VS the original user data
    and returns True if the operation outcome was valid, else False.
    """

    updated_user_object = get_user_data_from_user_model(old_user_data)
    updated_user_data_dict = updated_user_object.dict()

    # basically just getting intersetion of keys from two dicts
    keys_to_compare = set(updated_user_data_dict).intersection(
        set(updated_data_json))

    try:
        is_password = lambda x: x == "password"
        for key in keys_to_compare:

            if is_password(key):
                password_str = updated_data_json[key]
                assert updated_user_object.check_password(password_str)

            assert updated_data_json[key] == updated_user_data_dict[key]
        return True
    except AssertionError:
        return False


def check_fields_not_updated(old_user_data: user_models.User) -> bool:
    """
    Checks fields in Mongo are the same as they are in the provided user data.
    """
    new_user_data = get_user_data_from_user_model(old_user_data)
    old_user_data_dict = old_user_data.dict()

    try:
        for key, val in new_user_data.dict().items():
            if key == "password":
                assert new_user_data.check_password(old_user_data_dict[key])
            else:
                assert old_user_data_dict[key] == val
    except AssertionError as assert_error:
        logging.debug(f"failed at: {assert_error}")
        return False

    return True


def get_user_data_from_user_model(
        old_user_data: user_models.User) -> user_models.User:
    """
    Takes a user object and returns a new
    User object based off a fresh Mongo query
    """
    user_identifier = user_models.UserIdentifier(
        user_id=old_user_data.get_id())
    new_user_data = asyncio.run(
        user_utils.get_user_info_by_identifier(user_identifier))
    return new_user_data


def get_response_from_json(update_json_payload: Dict[str, Any],
                           headers_dict: Dict[str, Any]) -> HTTPResponse:
    """
    Attemps to hit the update user endpoint with the given JSON
    payload and headers, returning the HTTP response.
    """
    endpoint_url = get_update_user_endpoint_url()
    return client.patch(endpoint_url,
                        json=update_json_payload,
                        headers=headers_dict)


class TestUserUpdate:
    def test_valid_user_update(
        self, registered_user: user_models.User,
        get_header_dict_from_user: Callable[[user_models.User], Dict[str,
                                                                     Any]]):
        """
        Tries to update an existing user data with incoming valid data
        """
        headers = get_header_dict_from_user(registered_user)
        update_json_payload = get_valid_update_request(registered_user)
        response = get_response_from_json(update_json_payload, headers)

        assert check_response_valid_update(response)
        assert check_fields_updated_correctly(registered_user,
                                              update_json_payload)

    def test_update_not_matching_token(
            self, registered_user: user_models.User,
            valid_header_dict_with_user_id: Dict[str, Any]):
        """
        Tries to update a user but sends an auth token with a
        different user_id in the payload than the in the identifier,
        expecting failure.
        """
        update_json_payload = get_valid_update_request(registered_user)
        response = get_response_from_json(update_json_payload,
                                          valid_header_dict_with_user_id)

        assert not check_response_valid_update(response)
        assert not check_fields_updated_correctly(registered_user,
                                                  update_json_payload)
        assert response.status_code == 401

    def test_update_invalid_fields(
        self, registered_user: user_models.User,
        get_header_dict_from_user: Callable[[user_models.User], Dict[str,
                                                                     Any]]):
        """
        Tries to update an existing user data with incoming invalid data
        """
        headers = get_header_dict_from_user(registered_user)
        update_json_payload = get_invalid_update_request(registered_user)
        response = get_response_from_json(update_json_payload, headers)

        assert check_response_invalid_fields(response)
        assert check_fields_not_updated(registered_user)

    def test_update_nonexistent_user(
        self, unregistered_user: user_models.User,
        get_header_dict_from_user: Callable[[user_models.User], Dict[str,
                                                                     Any]]):
        """
        Tries to update a nonexistent user, using valid update fields
        """
        headers = get_header_dict_from_user(unregistered_user)
        update_json_payload = get_valid_update_request(unregistered_user)
        response = get_response_from_json(update_json_payload, headers)

        assert check_response_update_nonexistent(response)

    def test_update_no_data(self, valid_header_dict_with_user_id: Dict[str,
                                                                       Any]):
        """
        Tries to pass an empty dict as a json payload to the update endpoint
        """
        headers = valid_header_dict_with_user_id
        update_json_payload = get_update_request_no_data()
        response = get_response_from_json(update_json_payload, headers)

        assert check_response_no_data(response)
