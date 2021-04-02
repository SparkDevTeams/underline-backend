# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
# pylint: disable=unsubscriptable-object
#       - bug with pylint
"""
Holds endpoint tests for the batch event query requests.
"""
import random
import logging
from datetime import datetime
from typing import Dict, Any, Callable, Optional

from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

import models.events as event_models

from app import app

client = TestClient(app)


def check_query_events_resp_valid(
        response: HTTPResponse,
        query_form: event_models.BatchEventQueryModel) -> bool:
    """
    Checks that the server response is good and valid for the given
    request form.
    """
    try:
        assert response.status_code == 200
        assert response.json()
        assert "events" in response.json()

        list_of_events = response.json()["events"]
        assert check_list_of_events_returned_matches_query_form(
            list_of_events, query_form)

        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}, resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_list_of_events_returned_matches_query_form(  # pylint: disable=invalid-name
        list_of_event_dicts: Dict[str, Any],
        query_form: event_models.BatchEventQueryModel) -> bool:
    """
    Checks that the list of events returned by the endpoint is valid and
    adheres to the query filters given by the client's query form.
    """
    try:
        for event in list_of_event_dicts:
            assert event["public"]
            assert check_event_enums_match_query(event, query_form)
            assert check_event_query_datetimes_ok(event, query_form)
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}"
        logging.debug(debug_msg)
        return False


def check_event_enums_match_query(
        event: Dict[str, Any],
        query_form: event_models.BatchEventQueryModel) -> bool:
    """
    Checks that all of the enums (tag and status) are valid and match the
    query form used to find them
    """
    valid_tags = query_form.event_tag_filter
    valid_statuses = {
        event_models.EventStatusEnum.active.name,  # pylint: disable=no-member
        event_models.EventStatusEnum.ongoing.name  # pylint: disable=no-member
    }

    valid_tags_in_event = not valid_tags or bool(
        set(event["tags"]).intersection(set(valid_tags)))
    valid_status_in_event = event["status"] in valid_statuses

    return valid_tags_in_event and valid_status_in_event


def check_event_query_datetimes_ok(
        event: Dict[str, Any],
        query_form: event_models.BatchEventQueryModel) -> bool:
    """
    Checks that the event has a valid datetime according to the query form
    """
    datetime_from_str = datetime.fromisoformat

    start_datetime = datetime_from_str(event["date_time_start"])
    end_datetime = datetime_from_str(event["date_time_end"])

    query_datetime = query_form.query_date

    try:
        assert end_datetime > query_datetime
        assert start_datetime <= query_datetime
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}"
        logging.debug(debug_msg)
        return False


def get_batch_query_endpoint_url() -> str:
    """
    Returns endpoint url string
    """
    return "/events/find/batch"


def get_json_dict_from_query_form(
        query_form: event_models.BatchEventQueryModel) -> Dict[str, Any]:
    """
    Returns the request-ready dict to be used as JSON data
    for the batch query endpoint. Created from a query form object.
    """
    query_dict = query_form.dict()
    return query_dict


def get_batch_query_form_for_today() -> event_models.BatchEventQueryModel:
    """
    Gets a batch query form for today's date.
    """
    today = datetime.today()
    query_form = event_models.BatchEventQueryModel(query_date=today)
    return query_form


def get_batch_query_form_with_tags() -> event_models.BatchEventQueryModel:
    """
    Gets a batch query form with default date and some tag enums
    """
    enum_class = event_models.EventTagEnum
    enum_members_list = [enum_class(x) for x in enum_class.__members__]
    enums_list = list({
        random.choice(enum_members_list)
        for _ in range(random.randint(1, 4))
    })

    query_form = event_models.BatchEventQueryModel(event_tag_filter=enums_list)
    return query_form


class TestBatchEventQueryEndpoint:
    def test_register_many_query_ok(
        self, register_event_for_batch_query: Callable[[
            event_models.BatchEventQueryModel, Optional[bool], Optional[bool]
        ], event_models.Event]):
        """
        Registers a few valid events and then tries to query for
        them with a valid query form, expecting success.
        """
        query_form = get_batch_query_form_for_today()

        amount_of_valid_events = 5
        for _ in range(amount_of_valid_events):
            register_event_for_batch_query(query_form)

        for _ in range(5):
            register_event_for_batch_query(query_form, date_in_range=False)

        for _ in range(5):
            register_event_for_batch_query(query_form, enum_valid=False)

        for _ in range(5):
            register_event_for_batch_query(query_form,
                                           date_in_range=False,
                                           enum_valid=False)

        json_data = get_json_dict_from_query_form(query_form)
        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
        assert len(response.json()["events"]) == amount_of_valid_events

    def test_batch_query_with_enums(
        self, register_event_for_batch_query: Callable[[
            event_models.BatchEventQueryModel, Optional[bool], Optional[bool]
        ], event_models.Event]):
        """
        Registers valid events and tries to query them by tag enum successfully
        """
        query_form = get_batch_query_form_with_tags()

        amount_of_valid_events = 5
        for _ in range(amount_of_valid_events):
            register_event_for_batch_query(query_form)

        for _ in range(5):
            register_event_for_batch_query(query_form, date_in_range=False)

        for _ in range(5):
            register_event_for_batch_query(query_form, enum_valid=False)

        for _ in range(5):
            register_event_for_batch_query(query_form,
                                           date_in_range=False,
                                           enum_valid=False)

        json_data = get_json_dict_from_query_form(query_form)
        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
        assert len(response.json()["events"]) == amount_of_valid_events

    def test_no_data_valid_response(
        self, register_event_for_batch_query: Callable[[
            event_models.BatchEventQueryModel, Optional[bool], Optional[bool]
        ], event_models.Event]):
        """
        Registers many events but passes in no data, expecting a valid response
        """
        empty_query_form = event_models.BatchEventQueryModel()

        number_of_events_registered = 5
        for _ in range(number_of_events_registered):
            register_event_for_batch_query(empty_query_form)

        json_data = get_json_dict_from_query_form(empty_query_form)

        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, empty_query_form)
