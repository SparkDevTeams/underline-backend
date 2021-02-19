# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=invalid-name
#       - this module has some pretty verbose names,
#         shrinking them feels worse than disabling this lint.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for get event by location query.
"""
import logging
from typing import Dict, Any
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.events as event_models

client = TestClient(app)


def get_location_query_from_event(event_form: event_models.Event,
                                  radius) -> Dict[str, Any]:
    """
    Returns a valid json query given a radius and an event form.
    """
    location = event_form.location
    query_data = {
        "lat": location.latitude,
        "lon": location.longitude,
        "radius": radius
    }
    return query_data


def check_event_locations_response_valid(response: HTTPResponse) -> bool:
    """
    Checks the response for a valid list of events and returns
    true if all the checks pass, else false.
    """
    try:
        assert response.status_code == 200
        response_json = response.json()
        assert "events" in response_json
        assert response_json["events"]
        assert len(response_json["events"]) > 0
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_query_event_location_url() -> str:
    """
    Returns the endpoint's url string
    """
    return "/events/location"


def get_invalid_query_from_event(event_form: event_models.Event,
                                 radius) -> Dict[str, Any]:
    """
    Returns an out of bounds (i.e. invalid) query dict from a given event.
    """
    location = event_form.location
    bad_query_data = {
        "lat": location.latitude + 1000,
        "lon": location.longitude - 1000,
        "radius": radius
    }

    return bad_query_data


class TestEventsLocation:
    def test_events_location_success(self,
                                     registered_event: event_models.Event):
        """
        Tries to query an existing event by it's approximate location,
        expecting success.
        """
        radius = 10
        query_data = get_location_query_from_event(registered_event, radius)
        endpoint_url = get_query_event_location_url()
        response = client.get(endpoint_url, params=query_data)

        assert check_event_locations_response_valid(response)

    def test_events_location_empty_data_failure(
            self, registered_event: event_models.Event):
        """
        Tries to query events by location but sends no args, expecting failure
        """
        del registered_event  # unused fixture result
        endpoint_url = get_query_event_location_url()
        response = client.get(endpoint_url, params={})
        assert not check_event_locations_response_valid(response)

    def test_events_location_no_events_failure(
            self, unregistered_event: event_models.Event):
        """
        Tries to query in a massive radius but without any events registered,
        expecting an empty response
        """
        huge_radius = 10_000
        query_data = get_location_query_from_event(unregistered_event,
                                                   huge_radius)

        endpoint_url = get_query_event_location_url()
        response = client.get(endpoint_url, params=query_data)
        assert not check_event_locations_response_valid(response)

    def test_events_location_invalid_lat_lon(
            self, registered_event: event_models.Event):
        """
        Tries to query with an invalid lat/lon range, expecting failure
        """
        radius = 10
        invalid_query_data = get_invalid_query_from_event(
            registered_event, radius)

        endpoint_url = get_query_event_location_url()
        response = client.get(endpoint_url, params=invalid_query_data)

        assert not check_event_locations_response_valid(response)
        assert response.status_code == 422
