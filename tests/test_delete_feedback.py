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
