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


"""
def get_valid_header_token_dict_from_user(
    get_valid_header_token_dict_from_user_id: Callable[[common_models.UserId],
                                                       Dict[str, Any]]
) -> Callable[[user_models.User], Dict[str, Any]]:
"""


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

        # todo: see if this is hacky
        user_id = asyncio.run(
            auth_utils.get_user_id_from_header_and_check_existence(
                token=token_str))  # this wants a str
        # user_id = Token.get_dict_from_enc_token_str(add_event_header.get(token_str)) # todo: figure out why this fails

        client.put(endpoint_url,
                   json=add_event_payload,
                   headers=add_event_header)

        new_user_data = asyncio.run(
            user_utils.get_user_info_by_identifier(
                user_models.UserIdentifier(user_id=user_id)))
        breakpoint()

        # 6. Create a new user object with the id and new data
        # 7. Compare the 2 user objects, assert they are the exact same but with the 1 extra id
