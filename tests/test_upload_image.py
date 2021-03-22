# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for the upload image endpoint
"""
from typing import Any, Dict
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from app import app

client = TestClient(app)




def check_upload_image_resp_valid(response: HTTPResponse) -> bool:
    return response.status_code == 201

def get_image_endpoint_url() -> str:
    return "/images/upload"

class TestImage:
    def test_upload_image(self, generate_image_and_its_dict: Dict[str, Any]):
        files = generate_image_and_its_dict
        endpoint_url = get_image_endpoint_url()
        response = client.post(endpoint_url, files=files)
        assert check_upload_image_resp_valid(response)
