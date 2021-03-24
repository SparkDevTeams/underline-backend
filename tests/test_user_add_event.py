# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
import models.users as user_models
import models.events as event_models
from typing import Dict, Any
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def get_update_user_endpoint_url() -> str:
    """
    Returns the url string for the user update endpoint
    """
    return "/users/add_event"


def get_add_event_payload(
        user_data: user_models.User,
        event_data: event_models.Event) -> Dict[str, Any]:
    """
    Creates a valid JSON payload to add an event to the user
    """


class TestUserAddEvent:
    def test_add(
            self, registered_user: user_models.User,
            unregistered_event=event_models.Event):
        """
        Tests adding a valid event to a valid User
        """

        endpoint_url = get_update_user_endpoint_url()
        add_event_payload = get_add_event_payload(
            registered_user, unregistered_event)

        client.put(endpoint_url, json=add_event_payload)
