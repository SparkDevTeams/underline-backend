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


def generate_range_of_events(register_event_factory: Callable[
    [event_models.BatchEventQueryModel, Optional[bool], Optional[bool]],
    event_models.Event], query_form: event_models.BatchEventQueryModel,
                             form_numbers: int) -> None:
    """
    Generates the given amount of valid, and invalid registered events.
    """
    for _ in range(form_numbers):
        register_event_factory(query_form)

    for _ in range(form_numbers):
        register_event_factory(query_form, date_in_range=False)

    for _ in range(form_numbers):
        register_event_factory(query_form, enum_valid=False)

    for _ in range(form_numbers):
        register_event_factory(query_form,
                               date_in_range=False,
                               enum_valid=False)


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
        form_numbers = 15
        query_form.limit = form_numbers

        generate_range_of_events(register_event_for_batch_query, query_form,
                                 form_numbers)

        json_data = get_json_dict_from_query_form(query_form)
        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
        assert len(response.json()["events"]) == form_numbers

    def test_batch_query_with_enums(
        self, register_event_for_batch_query: Callable[[
            event_models.BatchEventQueryModel, Optional[bool], Optional[bool]
        ], event_models.Event]):
        """
        Registers valid events and tries to query them by tag enum successfully
        """
        query_form = get_batch_query_form_with_tags()
        form_numbers = 10
        query_form.limit = form_numbers

        generate_range_of_events(register_event_for_batch_query, query_form,
                                 form_numbers)

        json_data = get_json_dict_from_query_form(query_form)
        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
        assert len(response.json()["events"]) == form_numbers

    def test_no_data_valid_response(
        self, register_event_for_batch_query: Callable[[
            event_models.BatchEventQueryModel, Optional[bool], Optional[bool]
        ], event_models.Event]):
        """
        Registers many events but passes in no data, expecting a valid response
        """
        number_of_events_registered = 5

        empty_query_form = event_models.BatchEventQueryModel()
        empty_query_form.limit = number_of_events_registered

        for _ in range(number_of_events_registered):
            register_event_for_batch_query(empty_query_form)

        json_data = get_json_dict_from_query_form(empty_query_form)

        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, empty_query_form)

    def test_batch_query_with_limits(
        self, register_event_for_batch_query: Callable[[
            event_models.BatchEventQueryModel, Optional[bool], Optional[bool]
        ], event_models.Event]):
        """
        Registers some events and then queries with limits, expecting
        the limit number of events to be returned instead of the amount
        of events registered.
        """
        limit_amount = 8
        query_form = get_batch_query_form_with_tags()
        query_form.limit = limit_amount

        form_numbers = 15
        generate_range_of_events(register_event_for_batch_query, query_form,
                                 form_numbers)

        json_data = get_json_dict_from_query_form(query_form)
        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
        assert len(response.json()["events"]) == limit_amount

    def test_batch_query_with_index(
        self, register_event_for_batch_query: Callable[[
            event_models.BatchEventQueryModel, Optional[bool], Optional[bool]
        ], event_models.Event]):
        """
        Registers some events then tries to request them twice, with overlapping
        indexes, expecting different, but overlapping data to be returned.
        """
        limit_amount = 8
        query_form = get_batch_query_form_with_tags()
        query_form.limit = limit_amount

        form_numbers = limit_amount * 2
        generate_range_of_events(register_event_for_batch_query, query_form,
                                 form_numbers)

        json_data = get_json_dict_from_query_form(query_form)
        endpoint_url = get_batch_query_endpoint_url()
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
        assert len(response.json()["events"]) == limit_amount

        event_to_be_compared = response.json()["events"][limit_amount - 1]

        # second request with index
        index_number = limit_amount - 1
        query_form.index = index_number
        json_data = get_json_dict_from_query_form(query_form)
        response = client.post(endpoint_url, json=json_data)

        assert check_query_events_resp_valid(response, query_form)
        assert len(response.json()["events"]) == min(
            form_numbers - index_number, limit_amount)

        # should be at least one item of overlap
        assert response.json()["events"][0] == event_to_be_compared
