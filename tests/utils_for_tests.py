import uuid
import datetime
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def generate_uuid():
    return str(uuid.uuid4())


def register_an_event():
    json = {
        "title": "Test Event",
        "description": "Test Description",
        "date": str(datetime.datetime.now()),
        "tag": "sporting_events",
        "location": {
            "latitude": 75.0,
            "longitude": 75.0
        },
        "max_capacity": 10,
        "public": False,
        "attending": [],
        "upvotes": 0,
        "comment_ids": [],
        "rating": 5.0,
        "status": "active",
        "creator_id": "0"
    }
    event_response = client.post("/events/register", json=json)
    assert event_response.status_code == 201
