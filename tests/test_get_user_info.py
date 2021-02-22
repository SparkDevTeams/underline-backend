<<<<<<< HEAD
import time
from fastapi.testclient import TestClient
from app import app
import pytest
import logging

client = TestClient(app)


def check_get_user_response_valid(response, registration_data=None):
    response_json = response.json()
    if registration_data:
        try:
            assert response_json["first_name"] == registration_data[
                "first_name"]
            assert response_json["last_name"] == registration_data["last_name"]
            assert response_json["email"] == registration_data["email"]
        except AssertionError:
            return False

    try:
        assert response.status_code == 201
        assert "first_name" in response.json()
        assert "last_name" in response.json()
        assert "email" in response.json()
    except AssertionError:
        return False
    return True


# used to test "/users/find"
class TestGetUser:
    def test_get_user_success(self, registered_user):
        # get fake user data to test
        params = {"email": registered_user["email"]}
        # send request to test client
        response = client.get("/users/find", params=params)

        # check that response is good
        assert check_get_user_response_valid(response,
                                             registration_data=registered_user)

    def test_get_nonexistent_user_failure(self, registered_user):
        params = {"email": "fake@mail.com"}
        # send request to test client
        response = client.get("/users/find", params=params)
        # check that response is good
        assert not check_get_user_response_valid(response)

        assert response.status_code == 404

    def test_get_user_no_data_failure(self, registered_user):
        params = {}
        # send request to test client
        response = client.get("/users/find", params=params)
        # check that response is good
        assert not check_get_user_response_valid(response)
        assert response.status_code == 422
=======
# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for the get user info endpoint
"""
import logging
from typing import Dict, Any, Callable
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.users as user_models

client = TestClient(app)


def check_get_user_response_valid(response: HTTPResponse) -> bool:
    """
    Checks that the raw server response is valid.
    Returns true if all checks pass, else false
    """
    try:
        assert response.status_code == 200
        assert "first_name" in response.json()
        assert "last_name" in response.json()
        assert "email" in response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_user_matches_response(response: HTTPResponse,
                                user_data: user_models.User) -> bool:
    """
    Checks that the user data from the response is the same as
    the given user model passed.
    """
    response_json = response.json()
    try:
        user_data_dict = user_data.dict()
        query_data_dict = response_json
        for key in query_data_dict.keys():
            assert user_data_dict[key] == query_data_dict[key]
        return True
    except AssertionError:
        return False


def get_user_query_endpoint_string() -> str:
    """
    Returns the endpoint url string for "get user"
    """
    return "/users/find"


class TestGetUser:
    def test_get_user_success(
        self, registered_user: user_models.User,
        get_identifier_dict_from_user: Callable[[user_models.User],
                                                Dict[str, Any]]):
        """
        Tries to query a registered user from the database
        succesfully.
        """
        json_dict = get_identifier_dict_from_user(registered_user)
        endpoint_url = get_user_query_endpoint_string()
        response = client.post(endpoint_url, json=json_dict)

        assert check_get_user_response_valid(response)
        assert check_user_matches_response(response, registered_user)

    def test_get_nonexistent_user_fail(
        self, unregistered_user: user_models.User,
        get_identifier_dict_from_user: Callable[[user_models.User],
                                                Dict[str, Any]]):
        """
        Tries to query a nonexistent user expecting 404 failure.
        """
        json_dict = get_identifier_dict_from_user(unregistered_user)
        endpoint_url = get_user_query_endpoint_string()
        response = client.post(endpoint_url, json=json_dict)

        assert not check_get_user_response_valid(response)
        assert response.status_code == 404

    def test_get_user_no_data_failure(self, registered_user: user_models.User):
        """
        Try to query a valid user but sending no data, expecting a 422 failure
        """
        del registered_user  # unused fixture result
        empty_json_dict = {}
        endpoint_url = get_user_query_endpoint_string()
        response = client.post(endpoint_url, json=empty_json_dict)

        assert not check_get_user_response_valid(response)
        assert response.status_code == 422
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
