# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint testing for deleting feedback off of an event.
"""
import logging
from typing import Dict, Callable, Any
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.feedback as feedback_models
import models.users as user_models

client = TestClient(app)


def get_delete_feedback_endpoint_url() -> str:  # pylint: disable=invalid-name
    """
    Returns the url string for the delete feedback endpoint.

    Might seem a little verbose and unnecessary but raw strings
    are always trouble and take away lots of readability and flexibility.
    """
    return "/feedback/delete"


def get_delete_feedback_url_params(
        feedback: feedback_models.Feedback) -> Dict[str, str]:
    """
    Returns the url params needed to delete the given feedback object
    through the delete feedback endpoint.
    """
    event_id = feedback.event_id
    feedback_id = feedback.get_id()
    return {"event_id": event_id, "feedback_id": feedback_id}


def check_delete_feedback_response_valid(response: HTTPResponse) -> bool:  # pylint: disable=invalid-name
    """
    Checks that the incoming server response is valid,
    returning True if all checks pass, else False.
    """
    try:
        assert response.status_code == 204
        assert not response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


class TestDeleteFeedback:
    def test_delete_feedback_success(
        self, registered_feedback: feedback_models.Feedback,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Tries to delete an existing piece of feedback on an existing event,
        expecting success.
        """
        headers = get_header_dict_from_user_id(registered_feedback.creator_id)
        request_url = get_delete_feedback_endpoint_url()
        params = get_delete_feedback_url_params(registered_feedback)

        # delete then check response ok
        response = client.delete(request_url, params=params, headers=headers)
        assert check_delete_feedback_response_valid(response)

    def test_delete_feedback_nonexistent_event_failure(  # pylint: disable=invalid-name
        self, no_event_unregistered_feedback: feedback_models.Feedback,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Attempt to delete a piece of feedback without it existing,
        expecting failure.
        """
        request_url = get_delete_feedback_endpoint_url()
        params = get_delete_feedback_url_params(no_event_unregistered_feedback)
        headers = get_header_dict_from_user_id(
            no_event_unregistered_feedback.creator_id)

        # send delete request then assure that it was invalid
        response = client.delete(request_url, params=params, headers=headers)
        assert not check_delete_feedback_response_valid(response)
        assert response.status_code == 404

    def test_delete_feedback_nonexistent_user_failure(  # pylint: disable=invalid-name
        self, no_user_unregistered_feedback: feedback_models.Feedback,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Attempt to delete a piece of feedback without it existing,
        being tied to an existing user, expecting failure
        """
        request_url = get_delete_feedback_endpoint_url()
        params = get_delete_feedback_url_params(no_user_unregistered_feedback)
        headers = get_header_dict_from_user_id(
            no_user_unregistered_feedback.creator_id)

        # send delete request then assure that it was invalid
        response = client.delete(request_url, params=params, headers=headers)
        assert not check_delete_feedback_response_valid(response)
        assert response.status_code == 404

    def test_delete_feedback_no_event_no_user_failure(  # pylint: disable=invalid-name
        self, invalid_unregistered_feedback: feedback_models.Feedback,
        get_header_dict_from_user_id: Callable[[user_models.UserId],
                                               Dict[str, Any]]):
        """
        Attempt to delete a piece of feedback without either the user or
        the event existing, expecting failure
        """
        request_url = get_delete_feedback_endpoint_url()
        params = get_delete_feedback_url_params(invalid_unregistered_feedback)
        headers = get_header_dict_from_user_id(
            invalid_unregistered_feedback.creator_id)

        # send delete request then assure that it was invalid
        response = client.delete(request_url, params=params, headers=headers)
        assert not check_delete_feedback_response_valid(response)
        assert response.status_code == 404

    def test_delete_feedback_no_data(
            self, valid_header_dict_with_user_id: Dict[str, Any]):
        """
        Tries to delete a feedback object but sends no data,
        expecting a 422 error.
        """
        request_url = get_delete_feedback_endpoint_url()
        empty_params = {}

        # send delete request then assure that it was invalid
        response = client.delete(request_url,
                                 params=empty_params,
                                 headers=valid_header_dict_with_user_id)
        assert not check_delete_feedback_response_valid(response)
        assert response.status_code == 422
