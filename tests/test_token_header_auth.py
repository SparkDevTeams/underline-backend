# pylint: disable=redefined-outer-name
#       - calling an internal fixture; pylint does not like this.
# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
"""
Unit tests for the header util handler
"""
from typing import Dict
import pytest
from fastapi import Depends, APIRouter
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

import util.auth as auth_util
from app import app

# Create a test endpoint for the handler
router = APIRouter()


@router.get("/header/token_str")
def header_test_endpoint(header_str: str = Depends(
    auth_util.get_auth_token_from_header)):
    """
    Testing-only endpoint that wraps the `get_auth_token_from_header` method.
    Returns the result of the `Depend` call.
    """
    return header_str


app.include_router(router)

client = TestClient(app)


def get_token_str_endpoint_url_str() -> str:
    """
    Returns the router string for the test endpoint that
    echoes back the result from the `get_auth_token_from_header` method.
    """
    return "/header/token_str"


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


class TestAuthHeaderHandler:
    """
    Tests auth header handler functions by calling a test endpoint that
    echoes the `Depends` function.
    """
    def test_header_token_decoded_ok(self, valid_header_token_dict: Dict[str,
                                                                         str]):
        """
        Calls the endpoint that tests the `get_auth_token_from_header` method
        with a valid header, expecting to get back the same token passed in.
        """
        endpoint_url = get_token_str_endpoint_url_str()
        response = client.get(endpoint_url, headers=valid_header_token_dict)
        assert check_token_str_response_valid(response,
                                              valid_header_token_dict)
