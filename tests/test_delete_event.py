"""
Holds endpoint tests for cancelling an event in the database by changing it's status Enum
"""
import asyncio
from typing import Dict, Any, Callable
from models import exceptions
from fastapi.testclient import TestClient
import models.users as user_models
import models.events as event_models
import util.users as user_utils
import util.events as event_utils
from requests.models import Response as HTTPResponse
from app import app
from asgiref.sync import async_to_sync


client = TestClient(app)


def get_delete_event_endpoint_url() -> str:
    """
    """
    return "/events/delete"


def get_valid_call_payload(event: event_models.Event) -> Dict[str, Any]:
    """
    """
    return {"event_id": event.id}


def check_valid_del_response(response: HTTPResponse) -> bool:
    """
    """
    return response.status_code == 204


def check_event_update_safe(old_event: event_models.Event,
                            new_event: event_models.Event) -> bool:
    old_event.status = event_models.EventStatusEnum.cancelled
    return old_event == new_event


class TestDeleteEvent:
    def test_creator_delete_event(self, registered_user: user_models.User,
                                  registered_active_event_factory: Callable[[], event_models.Event],
                                  get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]
                                  ):
        event = registered_active_event_factory(
            registered_user)  # todo: figure out why this gives lint error on pycharm
        endpoint_url = get_delete_event_endpoint_url()
        json_payload = get_valid_call_payload(event)
        header_dict = get_header_dict_from_user(registered_user)

        user_identifier = user_models.UserIdentifier(user_id=registered_user.id)
        old_user_data = async_to_sync(user_utils.get_user_info_by_identifier)(user_identifier)
        # old_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))
        old_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))
        breakpoint()

        response = client.delete(endpoint_url,
                                 json=json_payload,
                                 headers=header_dict)

        # get new state from database for comparison
        new_user_data = asyncio.run(
            user_utils.get_user_info_by_identifier(user_models.UserIdentifier(user_id=registered_user.id)))
        new_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        breakpoint()

        assert check_valid_del_response(response)
        assert new_user_data == old_user_data
        assert new_event_data.status == event_models.EventStatusEnum.cancelled.name
        assert check_event_update_safe(old_event_data, new_event_data)
