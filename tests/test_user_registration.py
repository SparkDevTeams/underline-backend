import time
from fastapi.testclient import TestClient
from app import app
import pytest
import logging

client = TestClient(app)


# methods for testing user registration
def get_user_registration_form():
    user_data = {
        "first_name": "Testing_first",
        "last_name": "Testing_last",
        "email": "test@mail.com"
    }
    return user_data


def check_user_register_response_valid(response):
    test1 = response.status_code == 201
    test2 = "user_id" in response.json()
    return all([test1, test2])


# used to test "/users/register"
class TestUserRegister:
    def test_register_user_success(self):
        # get fake user data to test
        user_data = get_user_registration_form()
        # send request to test client
        response = client.post("/users/register", json=user_data)
        # check that response is good
        assert check_user_register_response_valid(response)

    def test_register_user_empty_data_failure(self):
        # send request to test client
        response = client.post("/users/register", json={})
        # check that response is good
        assert not check_user_register_response_valid(response)


def test_find_user_success(registered_user):
    params = {"email": registered_user.get("email")}
    response = client.get("/users/find", params=params)
    assert response.status_code == 201
