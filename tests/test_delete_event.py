"""
Holds endpoint tests for cancelling an event in the database by changing it's status Enum
"""

from typing import Dict, Any, Callable
from models import exceptions
from fastapi.testclient import TestClient
import models.users as user_models
import models.events as event_models
from app import app

client = TestClient(app)

def get_delete_event_endpoint_url() -> str:
    """
    """
    return "/events/delete"

def get_

class TestDeleteEvent:
    def test_creator_delete_event(self, registered_user: user_models.User,
    registered_event_factory: Callable[[], event_models.Event],
    get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]
                                  ):
        event = registered_event_factory(registered_user)

        endpoint_url = get_delete_event_endpoint_url()
        header_dict = get_header_dict_from_user()
        response = client.post(get_delete_event_endpoint_url,
                                 params=empty_params,
                                 headers=header_dict)

        assert event.creator_id == registered_user.id
        assert event.status == event_models.EventStatusEnum.cancelled