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
        fields_to_check = [
            "first_name", "last_name", "user_type", "image_id", "user_links"
        ]
        for field in fields_to_check:
            assert field in response.json()
        assert response.status_code == 200
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
    try:
        user_data_dict = user_data.dict()
        response_dict = response.json()

        non_comparable_keys = {"password"}
        keys_to_compare = [
            x for x in response_dict if x not in non_comparable_keys
        ]

        for key in keys_to_compare:
            assert user_data_dict[key] == response_dict[key]
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_user_query_endpoint_string() -> str:
    """
    Returns the endpoint url string for "get user"
    """
    return "/users/find"


class TestGetRegularUser:
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


class TestGetAdminUser:
    def test_get_user_success(
        self, registered_admin_user: user_models.User,
        get_identifier_dict_from_user: Callable[[user_models.User],
                                                Dict[str, Any]]):
        """
        Tries to query a registered_admin user from the database
        succesfully.
        """
        json_dict = get_identifier_dict_from_user(registered_admin_user)
        endpoint_url = get_user_query_endpoint_string()
        response = client.post(endpoint_url, json=json_dict)

        assert check_get_user_response_valid(response)
        assert check_user_matches_response(response, registered_admin_user)

    def test_get_nonexistent_user_fail(
        self, unregistered_admin_user: user_models.User,
        get_identifier_dict_from_user: Callable[[user_models.User],
                                                Dict[str, Any]]):
        """
        Tries to query a nonexistent user expecting 404 failure.
        """
        json_dict = get_identifier_dict_from_user(unregistered_admin_user)
        endpoint_url = get_user_query_endpoint_string()
        response = client.post(endpoint_url, json=json_dict)

        assert not check_get_user_response_valid(response)
        assert response.status_code == 404

    def test_get_user_no_data_failure(self,
                                      registered_admin_user: user_models.User):
        """
        Try to query a valid user but sending no data, expecting a 422 failure
        """
        del registered_admin_user  # unused fixture result
        empty_json_dict = {}
        endpoint_url = get_user_query_endpoint_string()
        response = client.post(endpoint_url, json=empty_json_dict)

        assert not check_get_user_response_valid(response)
        assert response.status_code == 422
