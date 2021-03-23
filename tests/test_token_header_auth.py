# pylint: disable=redefined-outer-name
#       - calling an internal fixture; pylint does not like this.
# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
"""
Unit tests for the header util handler
"""
import logging
from typing import Dict, Any

import pytest
from fastapi import Depends, APIRouter
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from models.auth import Token
import util.auth as auth_util
from app import app

# Create a test endpoint for the handler
router = APIRouter()


@router.get("/header/token/str")
def header_test_endpoint(header_str: str = Depends(
    auth_util.get_auth_token_from_header)):
    """
    Testing-only endpoint that wraps the `get_auth_token_from_header` method.
    Returns the result of the `Depend` call.
    """
    return header_str


@router.get("/header/token/dict")
def header_test_endpoint_decode(payload_dict: Dict[str, Any] = Depends(
    auth_util.get_payload_from_token_header)):
    """
    Testing-only endpoint that wraps the `get_payload_from_token_header` method.
    Returns the result of the `Depend` call.
    """
    return payload_dict


app.include_router(router)

client = TestClient(app)


def get_token_str_endpoint_url_str() -> str:
    """
    Returns the router string for the test endpoint that
    echoes back the result from the `get_auth_token_from_header` method.
    """
    return "/header/token/str"


def get_decode_token_payload_endpoint() -> str:  # pylint: disable=invalid-name
    """
    Returns the router string for the test endpoint that
    echoes back the result from the `get_auth_token_from_header` method.
    """
    return "/header/token/dict"


@pytest.fixture(scope="function")
def valid_header_token_dict(valid_encoded_token_str: str) -> Dict[str, str]:
    """
    Returns a valid dict to be used as the header for
    the test requests on the client.
    """
    header_dict = {"token": valid_encoded_token_str}
    return header_dict


def check_token_str_response_valid(response: HTTPResponse,
                                   header_dict: Dict[str, str]) -> bool:
    """
    Does some assert statements to make sure that the endpoint to
    get a token from the header returns a valid response

    Checks that the data passed in as the header is the same as the data
    returned from the endpoint.
    """
    try:
        assert response.status_code == 200
        assert isinstance(response.json(), str)
        assert header_dict["token"] == response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


def check_get_payload_from_token_response_valid(  # pylint: disable=invalid-name
        response: HTTPResponse, header_dict: Dict[str, str]) -> bool:
    """
    Does some assert statements to make sure that the endpoint to
    get a token from the header returns a valid response

    Checks that the data passed in as the header is the same as the data
    returned from the endpoint.
    """
    try:
        assert response.status_code == 200
        original_payload = Token.get_dict_from_enc_token_str(
            header_dict["token"])
        assert original_payload == response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


def get_invalid_token_header_dict(
        valid_header_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reverses the token string in the header making it invalid.
    Returns new, modified dict.
    """
    reversed_token_str = valid_header_dict["token"][::-1]
    invalid_token_header_dict = {"token": reversed_token_str}

    return invalid_token_header_dict


class TestAuthHeaderHandler:
    """
    Tests auth header handler functions by calling test endpoints that
    echoes the `Depends` function being tested.
    """
    class TestGetAuthTokenFromHeader:
        def test_header_token_ok(self, valid_header_token_dict: Dict[str,
                                                                     str]):
            """
            Calls the endpoint that tests the `get_auth_token_from_header`
            method with a valid header, expecting to get back the same
            token passed in.
            """
            endpoint_url = get_token_str_endpoint_url_str()
            response = client.get(endpoint_url,
                                  headers=valid_header_token_dict)
            assert check_token_str_response_valid(response,
                                                  valid_header_token_dict)

        def test_invalid_header_token_str(self,
                                          valid_header_token_dict: Dict[str,
                                                                        str]):
            """
            Tries to call the endpoint passing in an invalid token string that
            cannot be decoded, expecting failure.
            """
            invalid_token_header_dict = get_invalid_token_header_dict(
                valid_header_token_dict)

            endpoint_url = get_token_str_endpoint_url_str()
            response = client.get(endpoint_url,
                                  headers=invalid_token_header_dict)

            assert not check_token_str_response_valid(
                response, invalid_token_header_dict)
            assert response.status_code == 401

        def test_empty_header_data_failure(self):
            """
            Tries to call the test endpoint without pasing a header,
            expecting failure
            """
            empty_headers = {}
            endpoint_url = get_token_str_endpoint_url_str()
            response = client.get(endpoint_url, headers=empty_headers)
            assert response.status_code == 422

    class TestDecodeTokenAndGetPayload:
        def test_payload_decodable_ok(self,
                                      valid_header_token_dict: Dict[str, str]):
            """
            Sends in a token_str header with some payload, expecting to be
            returned the same payload passed in.
            """
            endpoint_url = get_decode_token_payload_endpoint()
            response = client.get(endpoint_url,
                                  headers=valid_header_token_dict)

            assert check_get_payload_from_token_response_valid(
                response, valid_header_token_dict)

        def test_invalid_header_token_str(self,
                                          valid_header_token_dict: Dict[str,
                                                                        str]):
            """
            Tries to call the endpoint passing in an invalid token string that
            cannot be decoded, expecting failure.
            """
            invalid_token_header_dict = get_invalid_token_header_dict(
                valid_header_token_dict)

            endpoint_url = get_decode_token_payload_endpoint()
            response = client.get(endpoint_url,
                                  headers=invalid_token_header_dict)

            assert not check_token_str_response_valid(
                response, invalid_token_header_dict)
            assert response.status_code == 401

        def test_empty_header_data_failure(self):
            """
            Tries to call the test endpoint without pasing a header,
            expecting failure
            """
            empty_headers = {}
            endpoint_url = get_decode_token_payload_endpoint()
            response = client.get(endpoint_url, headers=empty_headers)
            assert response.status_code == 422
