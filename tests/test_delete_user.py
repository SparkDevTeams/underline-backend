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
