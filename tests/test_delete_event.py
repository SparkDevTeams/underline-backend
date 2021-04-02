"""
Holds endpoint tests for cancelling an event in the database by changing it's status Enum
"""

from models import exceptions
from fastapi.testclient import TestClient

client = TestClient(app)


class TestDeleteEvent:
    def test_creator_delete_event():
