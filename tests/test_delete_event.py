"""
Holds endpoint tests for cancelling an event in the database by changing it's status Enum
"""
import asyncio
from typing import Dict, Any, Callable
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
    Returns the url string for the cancel event endpoint
    """
    return "/events/delete"


def get_valid_call_payload(event: event_models.Event) -> Dict[str, Any]:
    """
    Gets a valid json payload for event cancel body
    """
    return {"event_id": event.id}


def check_valid_cancel_response(response: HTTPResponse) -> bool:
    """
    Checks if response code is as expected for a valid event cancel
    """
    return response.status_code == 204


def check_unauthorized_response(response: HTTPResponse) -> bool:
    """
    Checks if response code is as expected for an unauthorized event cancel
    """
    return response.status_code == 403


def check_no_data_response(response: HTTPResponse) -> bool:
    """
    Checks if response code is as expected for an empty json payload
    """
    return response.status_code == 422


def check_no_header_response(response: HTTPResponse) -> bool:
    """
    Checks if response code is as expected for a tokenless header
    """
    return response.status_code == 422


def check_no_event_response(response: HTTPResponse) -> bool:
    """
    Checks if response code is as expected for an event id that
    doesn't correspond to an event in the database
    """
    return response.status_code == 404


def check_event_update_safe(old_event: event_models.Event,
                            new_event: event_models.Event) -> bool:
    """
    Checks if a newly acquired event object is the same as the old, except for
    an enum which is expected to now be cancelled on the new object.
    """
    old_event.status = event_models.EventStatusEnum.cancelled
    return old_event == new_event


def get_response_from_event_and_header(event: event_models.Event,
                                       header_dict: Dict[str, Any]) -> HTTPResponse:
    """
    Makes the endpoint call with te given event and header dict, returning the response.
    """
    json_payload = get_valid_call_payload(event)
    endpoint_url = get_delete_event_endpoint_url()
    response = client.delete(endpoint_url,
                             json=json_payload,
                             headers=header_dict)
    return response


def event_in_database(event: event_models.Event) -> bool:
    """
    Checks if the given event is in the database
    """
    id_dict = async_to_sync(event_utils.generate_event_id_dict)(event)
    var = event_utils.events_collection().find_one(id_dict)
    return bool(var)


class TestDeleteEvent:
    def test_creator_cancel_event(self, registered_user: user_models.User,
                                  registered_active_event_factory: Callable[[], event_models.Event],
                                  get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]
                                  ):
        """
        Tries to call the cancel endpoint from a User
        that created an event, expecting success
        """
        event = registered_active_event_factory(
            registered_user)  # todo: figure out why this gives lint error on pycharm
        header_dict = get_header_dict_from_user(registered_user)

        user_identifier = user_models.UserIdentifier(user_id=registered_user.id)
        old_user_data = async_to_sync(user_utils.get_user_info_by_identifier)(user_identifier) # todo: check this vs asyncio, then normalize
        old_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        response = get_response_from_event_and_header(event, header_dict)

        # get new state from database for comparison
        new_user_data = asyncio.run(
            user_utils.get_user_info_by_identifier(user_identifier))
        new_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        assert check_valid_cancel_response(response)
        assert new_user_data == old_user_data
        assert new_event_data.status == event_models.EventStatusEnum.cancelled.name
        assert check_event_update_safe(old_event_data, new_event_data)

    def test_admin_cancel_event(self, registered_admin_user: user_models.User,
                                registered_active_event_factory: Callable[[], event_models.Event],
                                get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]
                                ):
        """
        Tries to call the cancel endpoint from an admin, expecting success
        """
        event = registered_active_event_factory()  # don't pass the admin here
        header_dict = get_header_dict_from_user(registered_admin_user)

        user_identifier = user_models.UserIdentifier(user_id=registered_admin_user.id)
        old_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))
        old_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        response = get_response_from_event_and_header(event, header_dict)

        new_user_data = asyncio.run(
            user_utils.get_user_info_by_identifier(user_identifier))
        new_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        assert check_valid_cancel_response(response)
        assert new_user_data == old_user_data
        assert new_event_data.status == event_models.EventStatusEnum.cancelled.name
        assert check_event_update_safe(old_event_data, new_event_data)

    def test_unauthorized_cancel_event(self, registered_user: user_models.User,
                                       registered_active_event_factory: Callable[[], event_models.Event],
                                       get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]
                                       ):
        """
        Tries to call the cancel endpoint from a User that
        is not the creator or an admin, expecting failure
        """
        # FIXME: Figure out why this is generating an event with the registered_user as the creator
        event = registered_active_event_factory()
        header_dict = get_header_dict_from_user(registered_user)

        user_identifier = user_models.UserIdentifier(user_id=registered_user.id)
        old_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))
        old_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        response = get_response_from_event_and_header(event, header_dict)

        # get new state from database for comparison
        new_user_data = asyncio.run(
            user_utils.get_user_info_by_identifier(user_identifier))
        new_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        assert check_unauthorized_response(response)
        assert new_user_data == old_user_data
        assert old_event_data == new_event_data

    def test_no_data_cancel_event(self, registered_user: user_models.User,
                                  get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]):
        """
        Tries to call the cancel endpoint with a
        valid header but no data, expecting failure
        """
        json_payload = {}
        header_dict = get_header_dict_from_user(registered_user)
        endpoint_url = get_delete_event_endpoint_url()
        response = client.delete(endpoint_url,
                                 json=json_payload,
                                 headers=header_dict)
        assert check_no_data_response(response)

    def test_no_header_cancel_event(self, registered_user: user_models.User,
                                    registered_active_event_factory: Callable[[], event_models.Event],
                                    ):
        """
        Tries to call the cancel endpoint with
        no header but valid data, expecting failure
        """
        event = registered_active_event_factory()

        user_identifier = user_models.UserIdentifier(user_id=registered_user.id)
        old_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))
        old_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        response = get_response_from_event_and_header(event, {})

        # get new state from database for comparison
        new_user_data = asyncio.run(
            user_utils.get_user_info_by_identifier(user_identifier))
        new_event_data = asyncio.run(event_utils.get_event_by_id(event_id=event.id))

        assert check_no_header_response(response)
        assert new_user_data == old_user_data
        assert old_event_data == new_event_data

    def test_cancel_nonexistent_event(self, registered_user: user_models.User,
                                      unregistered_event: event_models.Event,
                                      get_header_dict_from_user: Callable[[user_models.User], Dict[str, Any]]
                                      ):
        """
        Tries to call the cancel endpoint with a valid event id
        that isn't tied to an actual registered event, expecting failure
        """
        header_dict = get_header_dict_from_user(registered_user)

        user_identifier = user_models.UserIdentifier(user_id=registered_user.id)
        old_user_data = asyncio.run(user_utils.get_user_info_by_identifier(user_identifier))

        response = get_response_from_event_and_header(unregistered_event, header_dict)

        # get new state from database for comparison
        new_user_data = asyncio.run(
            user_utils.get_user_info_by_identifier(user_identifier))

        assert check_no_event_response(response)
        assert new_user_data == old_user_data
        assert not event_in_database(unregistered_event)
