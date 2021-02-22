<<<<<<< HEAD
import time
from tests.utils_for_tests import generate_uuid
from fastapi.testclient import TestClient
from app import app
import pytest
import logging

client = TestClient(app)


class TestDeleteFeedback:
    def test_delete_feedback_success(self, registered_feedback_data):
        # get relevant event info from fixture
        event_id = registered_feedback_data["event_id"]
        feedback_id = registered_feedback_data["feedback_id"]

        # Check if feedback exists and that it's registered to the event id from the fixture
        response = client.get(f"/feedback/{feedback_id}")
        assert response.status_code == 201
        assert response.json()["event_id"] == event_id

        # Delete it and ensure the deletion goes through
        response = client.delete(f"/feedback/delete/{event_id}/{feedback_id}")
        assert response.status_code == 204

        # Attempt to get the deleted feedback, should fail
        response = client.get(f"/feedback/{feedback_id}")
        assert response.status_code == 404

    def test_delete_feedback_nonexistent_event_failure(self):
        # get fake event id and feedback id
        event_id = generate_uuid()
        feedback_id = generate_uuid()

        # attempt a delete expecting failure
        response = client.delete(f"/feedback/delete/{event_id}/{feedback_id}")
        assert response.status_code == 404
=======
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

from app import app
import models.feedback as feedback_models

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
            self, registered_feedback: feedback_models.Feedback):
        """
        Tries to delete an existing piece of feedback on an existing event,
        expecting success.
        """
        request_url = get_delete_feedback_endpoint_url()
        params = get_delete_feedback_url_params(registered_feedback)

        # delete then check response ok
        response = client.delete(request_url, params=params)
        assert check_delete_feedback_response_valid(response)

    def test_delete_feedback_nonexistent_event_failure(  # pylint: disable=invalid-name
            self, unregistered_feedback_object: feedback_models.Feedback):
        """
        Attempt to delete a piece of feedback without it existing,
        expecting failure.
        """
        request_url = get_delete_feedback_endpoint_url()
        params = get_delete_feedback_url_params(unregistered_feedback_object)

        # send delete request then assure that it was invalid
        response = client.delete(request_url, params=params)
        assert not check_delete_feedback_response_valid(response)
        assert response.status_code == 404
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
