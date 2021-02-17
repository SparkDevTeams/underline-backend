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
