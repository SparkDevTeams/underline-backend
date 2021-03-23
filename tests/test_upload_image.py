# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for the upload image endpoint
"""
import logging
from typing import Any, Dict
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from app import app

client = TestClient(app)


def check_upload_image_resp_valid(response: HTTPResponse) -> bool:
    try:
        assert response.status_code == 201
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


def get_image_endpoint_url() -> str:
    return "/images/upload"


class TestImageUploadEndpoint:
    def test_upload_image_ok_success(self, valid_file_data_dict: Dict[str,
                                                                      Any]):
        """
        Uploads a valid image file using the endpoint, expecting success.
        """
        endpoint_url = get_image_endpoint_url()
        response = client.post(endpoint_url, files=valid_file_data_dict)
        breakpoint()
        assert check_upload_image_resp_valid(response)

    def test_upload_image_no_data_fail(self):
        """
        Tries to upload empty data to the endpoint, expecting failure.
        """
        empty_file_data = {}
        endpoint_url = get_image_endpoint_url()
        response = client.post(endpoint_url, files=empty_file_data)
        assert not check_upload_image_resp_valid(response)
        assert response.status_code == 422

    def test_upload_bad_data_fail(self, invalid_file_data_dict: Dict[str,
                                                                     Any]):
        """
        Sends bad (non-valid file) data to the endpoint, expecting failure.
        """
        endpoint_url = get_image_endpoint_url()
        response = client.post(endpoint_url, files=invalid_file_data_dict)
        assert not check_upload_image_resp_valid(response)
        assert response.status_code == 422
