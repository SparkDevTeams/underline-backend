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
import models.feedback as feedback_models

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


def check_user_login_response_valid(response: HTTPResponse) -> bool:
    try:
        assert response.status_code == 200
        # todo: assert some more stuff? if not response.json()?
        return True
    except:
        # todo: specify exceptions, check AssertationError
        return False


class AttemptUserLogin:
    """
    Tests go inside the class
    """

    # todo: change this test to use fixtures
    def test_correct_pass(self, registered_user: user_models.User):
        """
        Tries to login an existing user with existing. Expects success and the correct response code
        todo: asserts for 200. Look up AssertationError
        """
        # create user here

        pass

    def test_incorrect_pass(self, registered_user: user_models.User):
        """
        Tries to login with a user and incorrect pass. Expects failure
        """
        pass

    def test_nonexisting_user(self):
        """
        Tries to login with a user that isn't in database. Expects failure
        todo: asserts for 404.
        """
        pass

# def get_delete_feedback_url_params(
#         feedback: feedback_models.Feedback) -> Dict[str, str]:
#     """
#     Returns the url params needed to delete the given feedback object
#     through the delete feedback endpoint.
#     """
#     event_id = feedback.event_id
#     feedback_id = feedback.get_id()
#     return {"event_id": event_id, "feedback_id": feedback_id}

#
# def check_user_login_response_valid(response: HTTPResponse) -> bool:  # pylint: disable=invalid-name
#     """
#     Checks that the incoming server response is valid,
#     returning True if all checks pass, else False.
#     """
#     try:
#         assert response.status_code == 200
#         assert not response.json()
#         return True
#     except AssertionError as assert_error:
#         debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
#         logging.debug(debug_msg)
#         return False
#
#
# class TestDeleteFeedback:
#     def test_delete_feedback_success(
#             self, registered_feedback: feedback_models.Feedback):
#         """
#         Tries to delete an existing piece of feedback on an existing event,
#         expecting success.
#         """
#         request_url = get_delete_feedback_endpoint_url()
#         params = get_delete_feedback_url_params(registered_feedback)
#
#         # delete then check response ok
#         response = client.delete(request_url, params=params)
#         assert check_delete_feedback_response_valid(response)
#
#     def test_delete_feedback_nonexistent_event_failure(  # pylint: disable=invalid-name
#             self, unregistered_feedback_object: feedback_models.Feedback):
#         """
#         Attempt to delete a piece of feedback without it existing,
#         expecting failure.
#         """
#         request_url = get_delete_feedback_endpoint_url()
#         params = get_delete_feedback_url_params(unregistered_feedback_object)
#
#         # send delete request then assure that it was invalid
#         response = client.delete(request_url, params=params)
#         assert not check_delete_feedback_response_valid(response)
#         assert response.status_code == 404
#
#     def test_delete_feedback_no_data(self):
#         """
#         Tries to delete a feedback object but sends no data,
#         expecting a 422 error.
#         """
#         request_url = get_delete_feedback_endpoint_url()
#         empty_params = {}
#
#         # send delete request then assure that it was invalid
#         response = client.delete(request_url, params=empty_params)
#         assert not check_delete_feedback_response_valid(response)
#         assert response.status_code == 422
