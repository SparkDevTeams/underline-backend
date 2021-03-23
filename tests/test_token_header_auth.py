# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
"""
Unit tests for the header util handler
"""
import logging
from typing import Dict, Any

from fastapi import Depends, APIRouter
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from models.auth import Token
import util.auth as auth_util
from app import app

# Create a test endpoint for the handler
router = APIRouter()


@router.get("/header/token/required/str")
def header_test_endpoint(header_str: str = Depends(
    auth_util.get_auth_token_from_header)):
    """
    Testing-only endpoint that wraps the `get_auth_token_from_header` method.
    Returns the result of the `Depend` call.
    """
    return header_str


@router.get("/header/token/optional/str")
def optional_header_test_endpoint(header_str: str = Depends(
    auth_util.get_token_from_optional_header)):
    """
    Tests the same endpoint as above but with the optional instead of
    required return function.
    """
    return header_str


@router.get("/header/token/required/dict")
def header_test_endpoint_payload(payload_dict: Dict[str, Any] = Depends(
    auth_util.get_payload_from_token_header)):
    """
    Testing-only endpoint that wraps the `get_payload_from_token_header` method.
    Returns the result of the `Depend` call.
    """
    return payload_dict


@router.get("/header/token/optional/dict")
def optional_header_payload_decode(payload_dict: Dict[str, Any] = Depends(
    auth_util.get_payload_from_optional_token_header)):
    """
    Wraps the same endpoint as "/header/token/optional/dict", but with an
    optional header, instead of required.
    """
    return payload_dict


app.include_router(router)
client = TestClient(app)


def get_token_str_endpoint_url_str() -> str:
    """
    Returns the router string for the test endpoint that
    echoes back the result from the `get_auth_token_from_header` method.
    """
    return "/header/token/required/str"


def get_optional_token_str_endpoint_url_str() -> str:  # pylint: disable=invalid-name
    """
    Returns the router string for the test endpoint that
    echoes back the result from the `get_auth_token_from_header` method.
    """
    return "/header/token/optional/str"


def get_decode_token_payload_endpoint() -> str:  # pylint: disable=invalid-name
    """
    Returns the router string for the test endpoint that
    echoes back the result from the `get_auth_token_from_header` method.
    """
    return "/header/token/required/dict"


def get_optional_decode_token_payload_endpoint() -> str:  # pylint: disable=invalid-name
    """
    Returns the router string for the test endpoint that
    echoes back the result from the `get_auth_token_from_header` method.
    """
    return "/header/token/optional/dict"


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


def check_response_valid_but_empty(response: HTTPResponse) -> bool:
    """
    Checks that the response returned was valid, but it contains
    no data, meaning the optional header was not passed in.
    """
    try:
        assert response.status_code == 200
        assert not response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


class TestAuthHeaderHandler:
    """
    Tests auth header handler functions by calling test endpoints that
    echoes the `Depends` function being tested.
    """
    class TestGetAuthTokenFromHeader:
        class TestRequiredHeader:
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

            def test_invalid_header_token_str(
                    self, invalid_token_header_dict: Dict[str, str]):
                """
                Tries to call the endpoint passing in an invalid token
                string that cannot be decoded, expecting failure.
                """
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

        class TestOptionalHeader:
            def test_header_token_ok(self, valid_header_token_dict: Dict[str,
                                                                         str]):
                """
                Calls the endpoint that tests the `get_auth_token_from_header`
                method with a valid header, expecting to get back the same
                token passed in.
                """
                endpoint_url = get_optional_token_str_endpoint_url_str()
                response = client.get(endpoint_url,
                                      headers=valid_header_token_dict)
                assert check_token_str_response_valid(response,
                                                      valid_header_token_dict)

            def test_invalid_header_token_str(
                    self, invalid_token_header_dict: Dict[str, str]):
                """
                Tries to call the endpoint passing in an invalid token
                string that cannot be decoded, expecting failure.
                """
                endpoint_url = get_optional_token_str_endpoint_url_str()
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
                endpoint_url = get_optional_token_str_endpoint_url_str()
                response = client.get(endpoint_url, headers=empty_headers)
                assert check_response_valid_but_empty(response)

    class TestDecodeTokenAndGetPayload:
        def test_payload_decodable_ok(self,
                                      valid_header_token_dict: Dict[str, str]):
            """
            Sends in a token_str header with some payload, expecting to be
            returned the same payload passed in.
            """
            endpoint_url = get_optional_decode_token_payload_endpoint()
            response = client.get(endpoint_url,
                                  headers=valid_header_token_dict)

            assert check_get_payload_from_token_response_valid(
                response, valid_header_token_dict)

        def test_invalid_header_token_str(
                self, invalid_token_header_dict: Dict[str, str]):
            """
            Tries to call the endpoint passing in an invalid token string that
            cannot be decoded, expecting failure.
            """
            endpoint_url = get_optional_decode_token_payload_endpoint()
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
            endpoint_url = get_optional_decode_token_payload_endpoint()
            response = client.get(endpoint_url, headers=empty_headers)
            assert check_response_valid_but_empty(response)
