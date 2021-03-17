# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for user update calls.
"""
import logging
from typing import Dict, Any
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.users as user_models
import models.auth as auth_models

client = TestClient(app)


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
    Checks the updated user response VS the original user data
    and returns True if the operation outcome was valid, else False.
    """
    return False


def get_update_user_endpoint_url() -> str:
    """
    Returns the url string for the user update endpoint
    """
    return "/users/update"


class TestUserUpdate:
    def test_valid_user_update(
            self, registered_user: user_models.UserRegistrationForm):
        """
        Tries to update an existing user data with new, valid data
        """
        updated_data_json = get_update_request_from_user(registered_user)
        endpoint_url = get_update_user_endpoint_url()

        response = client.patch(endpoint_url, json=updated_data_json)
        assert check_update_user_response_ok(response, registered_user)

    def test_update_user_with_invalid_fields(self):
        pass

    def test_attempt_update_nonexistent_user(self):
        pass
