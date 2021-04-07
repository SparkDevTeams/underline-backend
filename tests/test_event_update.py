# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Holds endpoint tests for getting all events in the database
"""
from typing import Callable
import time
from unittest.mock import patch

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from asgiref.sync import async_to_sync
import util.events as util_events
import models.events as event_models
from app import app

client = TestClient(app)

def check_not_expired(event: event_models.Event) -> bool:
    if event.status == 'ongoing':
        return True
    if event.status == 'active':
        return True
    return False

class TestEventUpdate:
    def test_update_event_expired(self,
                                    expired_event_factory: Callable[[],
                                                                       None]):
        """
        Registers an event that should expire
        """
        event = expired_event_factory()
        event_id = event.id
        time.sleep(1)
        updated_event = async_to_sync(util_events.get_event_by_id)(event_id)
        assert updated_event.status == event_models.EventStatusEnum.expired


    def test_update_event_not_expired(self,active_event_factory: Callable[[],
                                                                       None]):
        with patch('time.sleep', return_value=None) as patched_time_sleep:
            """
            Registers an event that should not expire
            """
            event = active_event_factory()
            event_id = event.id
            time.sleep(10)
            updated_event = async_to_sync(util_events.get_event_by_id)(event_id)
            assert check_not_expired(updated_event)