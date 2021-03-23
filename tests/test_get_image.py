# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for the get image endpoint
"""
import logging
from typing import Any, Dict
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from app import app

client = TestClient(app)


def check_get_image_resp_valid(response: HTTPResponse) -> bool:
    try:
        assert response.status_code == 201
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


def get_image_endpoint_url() -> str:
    return "/images/get"


def get_params_from_image_data(
        image_data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a valid param dict for querying an image given an image data dict.
    """
    image_id = image_data_dict["image_id"]
    return {"image_id": image_id}


class TestImageUploadEndpoint:
    def test_upload_image_ok_success(self,
                                     registered_image_data_and_id: Dict[str,
                                                                        Any]):
        """
        Uploads a valid image file using the endpoint, expecting success.
        """
        params_dict = get_params_from_image_data(registered_image_data_and_id)
        endpoint_url = get_image_endpoint_url()
        response = client.get(endpoint_url, params=params_dict)
        assert check_get_image_resp_valid(response)

    def test_get_image_no_data_fail(self):
        """
        Tries to request an image sending no data, expecting failure
        """
        empty_params = {}

        endpoint_url = get_image_endpoint_url()
        response = client.get(endpoint_url, params=empty_params)

        assert not check_get_image_resp_valid(response)
        assert response.status_code == 422

    def test_nonexistent_image_lookup(
            self, nonexistent_image_data_and_id: Dict[str, Any]):
        """
        Sends a valid request for a nonexistent image, expecting a 404 failure
        """
        invalid_params = get_params_from_image_data(
            nonexistent_image_data_and_id)

        endpoint_url = get_image_endpoint_url()
        response = client.get(endpoint_url, params=invalid_params)

        assert not check_get_image_resp_valid(response)
        assert response.status_code == 404
