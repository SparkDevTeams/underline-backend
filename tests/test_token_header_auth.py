# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
"""
Unit tests for token authentication utility
"""
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app

client = TestClient(app)

def test_valid_token_string():
    pass

def test_invalid_token_string():
    pass
