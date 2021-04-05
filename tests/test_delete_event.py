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


class TestDeleteEvent:
    def test_creator_delete_event(self, registered_user: user_models.User,
                                  registered_event_factory: Callable[[], event_models.Event],
                                  get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]
                                  ):
        event = registered_event_factory(registered_user)  # todo: figure out why this gives lint error on pycharm
        endpoint_url = get_delete_event_endpoint_url()
        json_payload = get_valid_call_payload(event)
        header_dict = get_header_dict_from_user(registered_user)

        old_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_models.UserIdentifier(user_id=registered_user.id)))
        old_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))
        breakpoint()

        response = client.delete(endpoint_url,
                               json=json_payload,
                               headers=header_dict)

        # now we need to get new state- get event and user from db. Assert user is same,
        new_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_models.UserIdentifier(user_id=registered_user.id)))
        new_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        breakpoint()

        assert new_user_data == old_user_data

        # ultimate goal of test is to ensure every field of User and Event is the same, EXCEPT for the event status enum
        assert event.creator_id == registered_user.id
        assert new_event_data.status == "cancelled"  # todo:why event_models.EventStatusEnum.cancelled doesnt work
        old_event_data.status = event_models.EventStatusEnum.cancelled
        assert new_event_data == old_event_data
        assert check_valid_del_response(response)