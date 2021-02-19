import logging
from datetime import datetime
from typing import Dict, Any

from requests.models import Response as HTTPResponse
from fastapi.testclient import TestClient

from app import app
import models.events as event_models

client = TestClient(app)


def check_event_registration_response_valid(response: HTTPResponse) -> bool:
    """
    Returns the boolean status of the validity of the raw
    http server response.
    """
    try:
        assert response.status_code == 201
        assert response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_reg_event_endpoint_url_str() -> str:
    """
    Returns the endpoint url string
    """
    return "/events/register"


def get_json_from_event_reg_form(
        event_form: event_models.EventRegistrationForm) -> Dict[str, Any]:
    """
    Creates and returns a valid json payload from an event registration form
    """
    json_dict = event_form.dict()
    return json_dict


def get_invalid_json_from_reg_form(
        event_form: event_models.EventRegistrationForm) -> Dict[str, Any]:
    """
    Takes a valid event form object and returns an invalid json payload from it
    """
    event_dict = event_form.dict()
    # make data dirty by reversing the order of values with their keys
    values = list(event_dict.values())[::-1]
    for key, value in zip(event_dict.keys(), values):
        event_dict[key] = value
    return event_dict


class TestRegisterEvent:
    def test_register_event_success(
            self, event_registration_form: event_models.EventRegistrationForm):
        """
        Attempts to register a valid event, expecting success.
        """
        event_form_json = get_json_from_event_reg_form(event_registration_form)

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url, json=event_form_json)
        assert check_event_registration_response_valid(event_response)

    def test_register_event_no_data_failure(self):
        """
        Tries to register an event while sending no data,
        expecting failure.
        """
        empty_event_form = {}

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url, json=empty_event_form)

        assert not check_event_registration_response_valid(event_response)
        assert event_response.status_code == 422

    def test_register_event_bad_data_failure(
            self, event_registration_form: event_models.EventRegistrationForm):
        """
        Tries to register an event with a faulty piece of data,
        expecting a 422 failure.
        """
        invalid_event_json = get_invalid_json_from_reg_form(
            event_registration_form)

        endpoint_url = get_reg_event_endpoint_url_str()
        event_response = client.post(endpoint_url, json=invalid_event_json)

        assert not check_event_registration_response_valid(event_response)
        assert event_response.status_code == 422
