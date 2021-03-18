# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for user update calls.
"""
import asyncio
import logging
from typing import Dict, Any, Set
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.users as user_models
import util.users as user_utils
import models.auth as auth_models

client = TestClient(app)

def get_dict_of_attributes_expected_to_be_different() -> Set[Any]:
    return {"identifier"}

def get_dict_of_attributes_expected_to_be_hashed() -> Set[Any]:
    return {"password"}



def get_update_request_from_user(
        user_data: user_models.User) -> Dict[str, Any]:
    """
    Generates a random valid JSON payload dict to be used in
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


def check_update_user_response_ok(response: HTTPResponse,
                                  original_user: user_models.User) -> bool:
    """
    Checks if response code is valid
    """
    return response.status_code == 200


def get_update_user_endpoint_url() -> str:
    """
    Returns the url string for the user update endpoint
    """
    return "/users/update"


def check_fields_updated_correctly(old_user_data: user_models.User,
                                   updated_data_json: Dict[str, Any]) -> bool:
    """
    Checks the updated user response VS the original user data
    and returns True if the operation outcome was valid, else False.
    """

    user_identifier = user_models.UserIdentifier(user_id=old_user_data.get_id())
    new_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))
    breakpoint()
    # todo: check last name field WASNT changed
    for k, v in updated_data_json.items():
        # fixme: complex code, don't like
        if new_user_data.dict().get(k) != v and k not in get_dict_of_attributes_expected_to_be_different():
            if k in get_dict_of_attributes_expected_to_be_hashed():
                if not new_user_data.check_password(v):
                    return False
            else:
                return False
    return True


class TestUserUpdate:
    def test_valid_user_update(
            self, registered_user: user_models.User):
        """
        Tries to update an existing user data with new, valid data
        """
        print("password before patch" + registered_user.password)
        updated_data_json = get_update_request_from_user(registered_user)
        #  first name, email, and pass updated now
        endpoint_url = get_update_user_endpoint_url()

        response = client.patch(endpoint_url, json=updated_data_json)
        print("password after patch" + registered_user.password)

        assert check_update_user_response_ok(response, registered_user)
        assert check_fields_updated_correctly(registered_user, updated_data_json)

    def test_update_user_with_invalid_fields(self):
        pass

    def test_attempt_update_nonexistent_user(self):
        pass
