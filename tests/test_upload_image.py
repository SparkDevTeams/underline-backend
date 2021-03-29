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


def get_upload_image_endpoint_url() -> str:
    return "/images/upload"


class TestImageUploadEndpoint:
    def test_upload_image_ok_success(self,
                                     valid_header_dict_with_user_id: Dict[str,
                                                                          Any],
                                     valid_file_data_dict: Dict[str, Any]):
        """
        Uploads a valid image file using the endpoint and passing in
        a valid header for an existing user, expecting success.
        """
        endpoint_url = get_upload_image_endpoint_url()
        response = client.post(endpoint_url,
                               files=valid_file_data_dict,
                               headers=valid_header_dict_with_user_id)
        assert check_upload_image_resp_valid(response)

    def test_upload_no_header_failure(self, valid_file_data_dict: Dict[str,
                                                                       Any]):
        """
        Tries to upload an image without passing
        in an auth token header, expecting failure
        """
        endpoint_url = get_upload_image_endpoint_url()
        response = client.post(endpoint_url, files=valid_file_data_dict)
        assert not check_upload_image_resp_valid(response)
        assert response.status_code == 422

    def test_upload_image_fake_user(self,
                                    nonexistent_user_header_dict: Dict[str,
                                                                       Any],
                                    valid_file_data_dict: Dict[str, Any]):
        """
        Tries to upload an image with an invalid auth token, expecting failure
        """
        endpoint_url = get_upload_image_endpoint_url()
        response = client.post(endpoint_url,
                               files=valid_file_data_dict,
                               headers=nonexistent_user_header_dict)
        assert not check_upload_image_resp_valid(response)
        assert response.status_code == 404

    def test_upload_image_no_data_fail(
            self, valid_header_dict_with_user_id: Dict[str, Any]):
        """
        Tries to upload empty data to the endpoint, expecting failure.
        """
        empty_file_data = {}
        endpoint_url = get_upload_image_endpoint_url()
        response = client.post(endpoint_url,
                               files=empty_file_data,
                               headers=valid_header_dict_with_user_id)
        assert not check_upload_image_resp_valid(response)
        assert response.status_code == 422

    def test_upload_bad_data_fail(self,
                                  valid_header_dict_with_user_id: Dict[str,
                                                                       Any],
                                  invalid_file_data_dict: Dict[str, Any]):
        """
        Sends bad (non-valid file) data to the endpoint, expecting failure.
        """
        endpoint_url = get_upload_image_endpoint_url()
        response = client.post(endpoint_url,
                               files=invalid_file_data_dict,
                               headers=valid_header_dict_with_user_id)
        assert not check_upload_image_resp_valid(response)
        assert response.status_code == 422
