<<<<<<< HEAD
import time
from fastapi.testclient import TestClient
from tests.utils_for_tests import generate_uuid
from app import app
import pytest
import logging

client = TestClient(app)


def check_delete_user_response_valid(response):
    response_code_check = response.status_code == 204
    data_valid_check = not response.json()
    return all([response_code_check, data_valid_check])


# used to test "/users/delete"
class TestDeleteUser:
    def test_delete_user_success(self, registered_user):
        params = {"email": registered_user["email"]}
        # send request to check if client is deleted
        response = client.delete("/users/delete", params=params)
        # check that response is good
        assert check_delete_user_response_valid(response)

    def test_delete_user_empty_data_failure(self):
        # send request to test client
        response = client.post("/users/delete", params={})
        # check that response is good
        assert not check_delete_user_response_valid(response)

    def test_delete_user_nonexistent_failure(self):
        # make fake email to test
        params = {"email": "fake@mail.com"}
        # send request to test client
        response = client.post("/users/delete", params=params)
        # check that response is good
        assert not check_delete_user_response_valid(response)

    # FIXME: the fixture runs twice (???) on this, making it broken.
    # eventually get this to work.
    #  def test_delete_user_twice_failure(self, registered_user):
    #  params = {"email": registered_user["email"]}
    #  # send request to check if client is deleted
    #  breakpoint()
    #  response = client.delete("/users/delete", params=params)
    #  # check that response is good
    #  assert check_delete_user_response_valid(response)
    #  breakpoint()
    #  # try to delete user once more and expect failure
    #  response = client.delete("/users/delete", params=params)
    #  assert not check_delete_user_response_valid(response)
=======
# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=invalid-name
#       - this module has some pretty verbose names,
#         shrinking them feels worse than disabling this lint.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for deleting a user.

Should use mostly fixtures in order to supply the necessary dependencies.
"""
import logging
from typing import Dict, Callable, Any
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.users as user_models

client = TestClient(app)


# helper methods
def check_delete_user_response_valid(response: HTTPResponse) -> bool:
    """
    Checks the raw server response and returns true if it passes all
    of the validity tests, else false.
    """
    try:
        assert response.status_code == 204
        assert not response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json {response.json()}"
        logging.debug(debug_msg)
        return False


class TestDeleteUser:
    def test_delete_user_success(
        self, registered_user: user_models.User,
        get_identifier_dict_from_user: Callable[[user_models.User],
                                                Dict[str, Any]]):
        """
        Tries to delete a registered user from the database,
        expecting success.
        """
        json_payload = get_identifier_dict_from_user(registered_user)
        # send request to check if client is deleted
        response = client.delete("/users/delete", json=json_payload)
        # check that response is good
        assert check_delete_user_response_valid(response)

    def test_delete_user_empty_data_failure(self):
        """
        Tries to delete a user without sending in a payload expecting failure.
        """
        empty_json_payload = {}
        response = client.delete("/users/delete", json=empty_json_payload)

        assert not check_delete_user_response_valid(response)
        assert response.status_code == 422

    def test_delete_user_nonexistent_failure(
        self, unregistered_user: user_models.User,
        get_identifier_dict_from_user: Callable[[user_models.User],
                                                Dict[str, Any]]):
        """
        Tries to delete a user that does not exist
        (i.e. has not been registered), expecting failure.
        """
        fake_json_payload = get_identifier_dict_from_user(unregistered_user)
        response = client.delete("/users/delete", json=fake_json_payload)

        assert not check_delete_user_response_valid(response)
        assert response.status_code == 404

    def test_delete_user_twice_failure(
        self, registered_user: user_models.User,
        get_identifier_dict_from_user: Callable[[user_models.User],
                                                Dict[str, Any]]):
        """
        Deletes a valid registered user, then tries to delete it again,
        expecting failure from the second request.
        """
        json_payload = get_identifier_dict_from_user(registered_user)
        response = client.delete("/users/delete", json=json_payload)
        assert check_delete_user_response_valid(response)

        failed_response = client.delete("/users/delete", json=json_payload)
        assert not check_delete_user_response_valid(failed_response)
        assert failed_response.status_code == 404
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
