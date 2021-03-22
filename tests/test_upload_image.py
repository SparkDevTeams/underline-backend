# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for the upload image endpoint
"""
import io
from PIL import Image
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from app import app

client = TestClient(app)




def check_upload_image_resp_valid(response: HTTPResponse) -> bool:
    return response.status_code == 201

def get_image_endpoint_url() -> str:
    return "/images/upload"

class TestImage:
    def test_upload_image(self):
        img = Image.new('RGB', (60, 30), color='red')
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        img_bytes = buf.getvalue()
        files = {"file": io.BytesIO(img_bytes)}
        endpoint_url = get_image_endpoint_url()
        response = client.post(endpoint_url, files=files)
        assert check_upload_image_resp_valid(response)
