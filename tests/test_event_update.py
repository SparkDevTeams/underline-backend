# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Holds endpoint tests for updating events
"""
from typing import Callable
import time
from unittest.mock import patch

from fastapi.testclient import TestClient
from asgiref.sync import async_to_sync
import util.events as util_events
import util.users as user_utils
import models.events as event_models
import models.users as user_models
from app import app

client = TestClient(app)


def check_not_expired(event: event_models.Event) -> bool:
    return event.status in {"ongoing", "active"}


class TestEventUpdate:
    def test_update_event_expired(self, registered_user: user_models.User,
                                  expired_event_factory: Callable[[], None]):
        """
        Registers an event that should expire and makes sure it's archived
        """
        event = expired_event_factory()
        event_id = event.id

        user_id = registered_user.id
        identifier = user_models.UserIdentifier(user_id=user_id)
        async_to_sync(user_utils.add_event_to_user_visible)(user_id, event_id)

        time.sleep(1)
        updated_event = async_to_sync(util_events.get_event_by_id)(event_id)
        assert updated_event.status == event_models.EventStatusEnum.expired

        new_user_data = async_to_sync(
            user_utils.get_user_info_by_identifier)(identifier)

        assert event_id in new_user_data.events_visible
        assert event_id not in new_user_data.events_archived

        async_to_sync(user_utils.archive_user_event)(user_id, event)

        new_user_data = async_to_sync(
            user_utils.get_user_info_by_identifier)(identifier)

        assert event_id not in new_user_data.events_visible
        assert event_id in new_user_data.events_archived

    def test_update_event_not_expired(self,
                                      active_event_factory: Callable[[],
                                                                     None]):
        """
        Registers an event that should not expire
        """
        with patch('time.sleep', return_value=None) as _patched_time_sleep:
            event = active_event_factory()
            event_id = event.id
            time.sleep(10)
            updated_event = async_to_sync(
                util_events.get_event_by_id)(event_id)
            assert check_not_expired(updated_event)
