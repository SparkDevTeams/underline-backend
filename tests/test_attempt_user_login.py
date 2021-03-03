# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint testing for deleting feedback off of an event.
"""
import logging
from typing import Dict
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
import models.users as user_models

from app import app

client = TestClient(app)
"""
Helper functions go outside the class
"""


def get_user_login_endpoint_url() -> str:  # pylint: disable=invalid-name
    """
    Returns the url string for the user login endpoint.

    Might seem a little verbose and unnecessary but raw strings
    are always trouble and take away lots of readability and flexibility.
    """
    return "/users/login"


def get_user_login_json_data(user: user_models.User) -> Dict[str, str]:
    """
    Returns the url params needed to login the given user object
    through the user login endpoint.
    """
    identifier = {"email": user.email}
    password = user.password
    return {"identifier": identifier, "password": password}


def check_user_login_response_valid(response: HTTPResponse) -> bool:
    """
    Helper function that checks if status code is valid
    """
    try:
        assert response.status_code == 200
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


class TestAttemptUserLogin:
    def test_correct_pass(self, registered_user: user_models.User):
        """
        Tries to login an existing user with existing.
        Expects success and 200 response code
        """
        request_url = get_user_login_endpoint_url()
        json_payload = get_user_login_json_data(registered_user)
        response = client.post(request_url, json=json_payload)
        assert check_user_login_response_valid(response)

    def test_incorrect_pass(self, registered_user: user_models.User):
        """
        Tries to login with a user and incorrect pass.
        Expects failure and a 422 response code
        """
        request_url = get_user_login_endpoint_url()
        json_payload = get_user_login_json_data(registered_user)
        identifier = json_payload.get("identifier")
        false_pass = 'aaaaaaaaaa'
        assert false_pass != json_payload.get("password")
        incorrect_pass_payload = {"identifier": identifier,
                                  "password": false_pass}

        response = client.post(request_url, json=incorrect_pass_payload)
        assert not check_user_login_response_valid(response)
        assert response.status_code == 422

    def test_nonexisting_user(self, unregistered_user: user_models.User):
        """
        Tries to login with a user that isn't in database.
        Expects failure and a 404 response code
        """
        request_url = get_user_login_endpoint_url()
        nonexistent_user_payload = get_user_login_json_data(unregistered_user)

        response = client.post(request_url, json=nonexistent_user_payload)
        assert not check_user_login_response_valid(response)
        assert response.status_code == 404
