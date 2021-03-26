# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint testing for adding feedback to an event.
"""
import logging
from typing import Dict, Callable, Any

from asgiref.sync import async_to_sync
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.feedback as feedback_models
import models.users as user_models
import util.feedback as feedback_utils

client = TestClient(app)


def get_add_feedback_url_str() -> str:
    """
    Returns the url string for the register feedback endpoint.
    """
    return "/feedback/add"


def get_payload_dict_from_reg_form(
    feedback_reg_form: feedback_models.FeedbackRegistrationRequest
) -> Dict[str, Any]:
    """
    Returns a valid dict to be used as JSON for a feedback
    registration request
    """
    json_dict = feedback_reg_form.dict()
    return json_dict


def check_add_feedback_resp_valid(response: HTTPResponse) -> bool:
    """
    Checks that the incoming server response is valid,
    returning True if all checks pass, else False.
    """
    try:
        assert response.status_code == 201
        assert response.json()
        assert "feedback_id" in response.json()
        assert check_feedback_added_exists(response)
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_feedback_added_exists(response: HTTPResponse) -> bool:
    """
    Given the registration server response, ensures the feedback exists,
    returning a boolean
    """
    response_feedback_id = response.json()["feedback_id"]
    try:
        assert async_to_sync(feedback_utils.get_feedback)(response_feedback_id)
        return True
    except AssertionError as compare_error:
        debug_msg = f"failed at: {compare_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


class TestAddFeedback:
    def test_add_feedback_success(
        self,
        valid_feedback_reg_form: feedback_models.FeedbackRegistrationRequest,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Tries to register a valid feedback form, expecting success
        """
        headers = get_header_dict_from_user_id(
            valid_feedback_reg_form.creator_id)
        json_dict = get_payload_dict_from_reg_form(valid_feedback_reg_form)

        request_url = get_add_feedback_url_str()
        response = client.post(request_url, json=json_dict, headers=headers)
        assert check_add_feedback_resp_valid(response)

    def test_add_feedback_nonexistent_event_failure(  # pylint: disable=invalid-name
        self, no_event_feedback_reg_form: feedback_models.
        FeedbackRegistrationRequest,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Attempt to add a piece of feedback without it
        being tied to an existing event, expecting failure
        """
        request_url = get_add_feedback_url_str()
        json_dict = get_payload_dict_from_reg_form(no_event_feedback_reg_form)
        headers = get_header_dict_from_user_id(
            no_event_feedback_reg_form.creator_id)

        response = client.post(request_url, json=json_dict, headers=headers)
        assert not check_add_feedback_resp_valid(response)
        assert response.status_code == 404

    def test_add_feedback_nonexistent_user_failure(  # pylint: disable=invalid-name
        self,
        no_user_feedback_reg_form: feedback_models.FeedbackRegistrationRequest,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Attempt to add a piece of feedback without it
        being tied to an existing user, expecting failure
        """
        request_url = get_add_feedback_url_str()
        json_dict = get_payload_dict_from_reg_form(no_user_feedback_reg_form)
        headers = get_header_dict_from_user_id(
            no_user_feedback_reg_form.creator_id)

        response = client.post(request_url, json=json_dict, headers=headers)
        assert not check_add_feedback_resp_valid(response)
        assert response.status_code == 404

    def test_add_feedback_no_event_no_user_failure(  # pylint: disable=invalid-name
        self,
        invalid_feedback_reg_form: feedback_models.FeedbackRegistrationRequest,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Attempt to add a piece of feedback without either the user or
        the event existing, expecting failure
        """
        request_url = get_add_feedback_url_str()
        json_dict = get_payload_dict_from_reg_form(invalid_feedback_reg_form)
        headers = get_header_dict_from_user_id(
            invalid_feedback_reg_form.creator_id)

        response = client.post(request_url, json=json_dict, headers=headers)
        assert not check_add_feedback_resp_valid(response)
        assert response.status_code == 404

    def test_add_feedback_no_data(self,
                                  valid_header_dict_with_user_id: Dict[str,
                                                                       Any]):
        """
        Tries to add a feedback object but sends no data,
        expecting a 422 error.
        """
        request_url = get_add_feedback_url_str()
        json_dict = {}

        response = client.post(request_url,
                               json=json_dict,
                               headers=valid_header_dict_with_user_id)
        assert not check_add_feedback_resp_valid(response)
        assert response.status_code == 422
