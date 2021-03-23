# pylint: disable=redefined-outer-name
#       - calling an internal fixture; pylint does not like this.
# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
"""
Unit tests for the header util handler
"""
import logging
from typing import Dict

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app

client = TestClient(app)


def get_validate_token_endpoint() -> str:
    """
    Returns the endpoint string for the validate token route
    """
    return "/auth/validate"


def check_validation_response_ok(response: HTTPResponse) -> bool:
    """
    Checks that the response returned a 204 with no data.
    """
    try:
        assert response.status_code == 204
        assert not response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


class TestValidateTokenEndpoint:
    def test_header_token_valid_ok(self, valid_header_token_dict: Dict[str,
                                                                       str]):
        """
        Tries to validate a valid token expecting success.
        """
        endpoint_url = get_validate_token_endpoint()
        response = client.get(endpoint_url, headers=valid_header_token_dict)
        assert check_validation_response_ok(response)

    def test_invalid_header_token_str(self,
                                      invalid_token_header_dict: Dict[str,
                                                                      str]):
        """
        Tries to validate an INVALID token, expecting an auth error
        """
        endpoint_url = get_validate_token_endpoint()
        response = client.get(endpoint_url, headers=invalid_token_header_dict)

        assert not check_validation_response_ok(response)
        assert response.status_code == 401

    def test_empty_header_data_failure(self):
        """
        Tries to validate no data, expecting a bad data failure
        """
        empty_headers = {}
        endpoint_url = get_validate_token_endpoint()
        response = client.get(endpoint_url, headers=empty_headers)
        assert not check_validation_response_ok(response)
        assert response.status_code == 422
