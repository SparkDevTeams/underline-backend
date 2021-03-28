# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
import asyncio

import models.users as user_models
import models.events as event_models
import util.users as user_utils
import util.auth as auth_utils
import models.commons as common_models
from typing import Dict, Any, Callable
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from app import app
from models.auth import Token

client = TestClient(app)


def get_update_user_endpoint_url() -> str:
    """
    Returns the url string for the user update endpoint
    """
    return "/users/add_event"


def get_add_event_payload(event_data: event_models.Event) -> Dict[str, Any]:
    """
    Creates a valid JSON payload to add an event to the user
    """
    add_event_dict = {"event_id": event_data.id}
    return add_event_dict


def get_add_event_header(user_data: user_models.User) -> Dict[str, Any]:
    """

    """
    header_dict = {
        "token": user_utils.get_auth_token_from_user_data(user_data)
    }
    return header_dict

def check_response_valid_add(response: HTTPResponse) -> bool:
    return response.status_code == 201


def check_event_add_success(old_user: user_models.User,
                            event: event_models.Event,
                            new_user: user_models.User) -> bool:

    events_visible = new_user.dict().get("events_visible")
    if event.id not in events_visible:
        return False
    breakpoint()
    events_visible.remove(event.id)
    new_user.dict().get()
    return old_user.dict() == new_user.dict()



# def get_user_data_hashed_pass(old_user_data: user_models.User) -> user_models.User:
#     user_id = old_user_data.dict().get("_id")
#     user_identifier = user_models.UserIdentifier(user_id=user_id)
#     return user_utils.get_user_info_by_identifier(user_identifier)

def get_user_data_from_id(user_id: common_models.UserId) -> user_models.User:
    user_identifier = user_models.UserIdentifier(user_id=user_id)
    return asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))


class TestUserAddEvent:
    def test_add(self, registered_user: user_models.User,
                 registered_event: event_models.Event,
                 get_header_dict_from_user: Callable[[user_models.User],
                                                     Dict[str, Any]]
                 ):  # todo: why does copying the [] give me lint errors?
        """
        Tests adding a valid event to a valid User
        """

        # 1. get valid header token dict from user using Felipe's function: conftest.get_valid_header_token_dict_from_user
        # 2. call client.put with header as seen : client.put(endpoint_url, json=add_event_payload, header=add_event_header)

        endpoint_url = get_update_user_endpoint_url()
        add_event_payload = get_add_event_payload(registered_event)
        add_event_header = get_header_dict_from_user(registered_user)
        token_str = add_event_header.get("token")

        user_id = asyncio.run(
            auth_utils.get_user_id_from_header_and_check_existence(
                token=token_str))  
        
        old_user_data = get_user_data_from_id(user_id)

        response = client.put(endpoint_url,
                   json=add_event_payload,
                   headers=add_event_header)

        new_user_data = get_user_data_from_id(user_id)

        assert check_response_valid_add(response)
        assert check_event_add_success(old_user_data, registered_event, new_user_data)
        breakpoint()


    def test_add_event_no_event(self, registered_user: user_models.User,
                                    unregistered_event: event_models.Event):
        """
        Testing
        """
        
        endpoint_url = get_update_user_endpoint_url()
        add_event_payload = get_add_event_payload(unregistered_event)