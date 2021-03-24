# pylint: disable=redefined-outer-name
#       - this is how we use fixtures internally so this throws false positives
"""
pytest `conftest.py` file that holds global fixtures for tests
"""
import os
import io
import random
import logging
from enum import Enum
from uuid import uuid4
from datetime import datetime, timedelta
from typing import List, Callable, Dict, Any, Tuple

import pytest
import fastapi
from PIL import Image
from faker import Faker
from asgiref.sync import async_to_sync

from config.db import _get_global_database_instance

import models.users as user_models
import models.events as event_models
import models.feedback as feedback_models
import models.auth as auth_models

import util.users as user_utils
import util.events as event_utils
import util.feedback as feedback_utils
import util.images as image_utils


# startup process
def pytest_configure(config):
    """
    Startup process for tests.

    The change of the testing flag **MUST** be the first statement done here,
    any other statements for setup must be placed afterwards.
    """
    os.environ['_called_from_test'] = 'True'
    logging.getLogger("faker").setLevel(logging.ERROR)
    del config  # unused variable


def pytest_unconfigure(config):  # pytest: disable=unused-argument
    """
    Shutdown process for tests, mostly involving the wiping of database
    documents and resetting the testing environment flag.
    """
    del config  # unused variable
    global_database_instance = _get_global_database_instance()
    global_database_instance.delete_test_database()
    global_database_instance.close_client_connection()
    os.environ['_called_from_test'] = 'False'


@pytest.fixture(autouse=True)
def run_around_tests():
    """
    Clears all documents in the test collections after every single test.
    """
    yield
    global_database_instance = _get_global_database_instance()
    global_database_instance.clear_test_collections()


@pytest.fixture(scope='function')
def registered_user(
    user_registration_form: user_models.UserRegistrationForm
) -> user_models.User:
    """
    Fixture that generates a random valid user and registers it directly to
    the database through the `util` method.

    Returns the original user object.
    """
    user_data = register_user_reg_form_to_db(user_registration_form)
    return user_data


@pytest.fixture(scope='function')
def registered_admin_user(
    admin_user_registration_form: user_models.AdminUserRegistrationForm
) -> user_models.User:
    """
    Fixture that generates and registers a random, valid AdminUser
    to the database.

    Returns the original user object.
    """
    user_data = register_user_reg_form_to_db(admin_user_registration_form)
    return user_data


@pytest.fixture(scope='function')
def admin_user_registration_form() -> user_models.AdminUserRegistrationForm:
    """
    Returns a randomly generated admin user registration form object.
    """
    admin_user_type = user_models.UserTypeEnum.ADMIN
    user_dict = generate_random_user(user_type=admin_user_type).dict()
    return user_models.AdminUserRegistrationForm(**user_dict)


@pytest.fixture(scope='function')
def unregistered_user() -> user_models.User:
    """
    Fixture that generates a valid user and returns it
    WITHOUT registering it to the database first.
    """
    return generate_random_user()


@pytest.fixture(scope='function')
def unregistered_admin_user() -> user_models.User:
    """
    Fixture that generates a valid admin user and returns it
    WITHOUT registering it to the database first.
    """
    admin_user_type = user_models.UserTypeEnum.ADMIN
    return generate_random_user(user_type=admin_user_type)


@pytest.fixture(scope='function')
def user_registration_form() -> user_models.UserRegistrationForm:
    """
    Returns an unregistered, random, valid user registration form object.
    """
    user_dict = generate_random_user().dict()
    return user_models.UserRegistrationForm(**user_dict)


def register_user_reg_form_to_db(
        reg_form: user_models.UserRegistrationForm) -> user_models.User:
    """
    Helper function for registering a user given a registration form
    and returning the user data.
    """
    user_data = get_user_from_user_reg_form(reg_form)

    # user ID auto-instanciates so we reassign it to the actual ID
    user_id = async_to_sync(user_utils.register_user)(reg_form)
    user_data.id = user_id

    return user_data


def get_user_from_user_reg_form(
        user_reg_form: user_models.UserRegistrationForm) -> user_models.User:
    """
    Helper method that correctly casts a `UserRegistrationForm` into
    a valid `User` object and returns it.
    """
    user_type = user_reg_form.get_user_type()
    user_object = user_models.User(**user_reg_form.dict(), user_type=user_type)
    return user_object


def generate_random_user(
    user_type: user_models.UserTypeEnum = user_models.UserTypeEnum.PUBLIC_USER
) -> user_models.User:
    """
    Uses a fake data generator to generate a unique
    and valid user object.

    Defaults to regular (public) user, but can optionally return an admin user.
    """
    fake = Faker()
    user_data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
        "user_type": user_type,
        "image_id": fake.uuid4()
    }
    return user_models.User(**user_data)


@pytest.fixture(scope='function')
def get_identifier_dict_from_user(
) -> Callable[[user_models.User], Dict[str, Any]]:
    """
    Takes data from a registered user and returns a dict with
    user identifier data to be passed as a json dict
    """
    def _user_data_to_json(user_data: user_models.User) -> Dict[str, Any]:

        user_email = user_data.email
        user_id = user_data.get_id()
        return {"email": user_email, "user_id": user_id}

    return _user_data_to_json


@pytest.fixture(scope='function')
def registered_event() -> event_models.Event:
    """
    Fixture that generates a random event and then directly registers it
    using an `util.events` method.

    Returns the original event object
    """
    event_data = generate_random_event()
    async_to_sync(event_utils.register_event)(event_data)

    return event_data


@pytest.fixture(scope='function')
def unregistered_event() -> event_models.Event:
    """
    Same as the registered event method but skips the actual
    database insertion step.

    Returns original unregistered object.
    """
    event_data = generate_random_event()
    return event_data


@pytest.fixture(scope='function')
def registered_event_factory() -> Callable[[], None]:
    """
    Returns a function that registers an event. Useful for when we want multiple
    event registration calls without caching the result.
    """
    def _register_event():
        event_data = generate_random_event()
        async_to_sync(event_utils.register_event)(event_data)
        return event_data

    return _register_event


@pytest.fixture(scope='function')
def event_registration_form() -> event_models.EventRegistrationForm:
    """
    Creates and returns a random valid event registration form object
    """
    event_data = generate_random_event().dict()
    return event_models.EventRegistrationForm(**event_data)


def generate_random_event() -> event_models.Event:
    """
    Uses a fake data generator to generate a unique, public,
    and valid event object.
    """
    fake = Faker()
    start_time, end_time = get_valid_date_range_from_now()

    event_tags = [
        get_random_enum_member_value(event_models.EventTagEnum)
        for _ in range(5)
    ]

    event_data = {
        "title": fake.text(),
        "description": fake.text(),
        "date_time_start": str(start_time),
        "date_time_end": str(end_time),
        "tags": event_tags,
        "location": {
            "title": fake.text(),
            "latitude": float(fake.latitude()),
            "longitude": float(fake.longitude()),
        },
        "max_capacity": random.randint(1, 100),
        "public": True,
        "attending": [],
        "comment_ids": [],
        "status": get_random_enum_member_value(event_models.EventStatusEnum),
        "links": [fake.text() for _ in range(5)],
        "image_ids": [fake.uuid4() for _ in range(5)],
        "creator_id": fake.uuid4(),
        "approval": get_random_enum_member_value(event_models.EventApprovalEnum)
    }
    return event_models.Event(**event_data)


def get_valid_date_range_from_now() -> Tuple[datetime, datetime]:
    """
    Generates a tuple of valid datetime where the first datetime
    is `datetime.now()` and the second is a random, valid range after
    the first one.
    """
    fake = Faker()
    datetime_from_start_range = lambda start: fake.date_time_between_dates(
        start, start + timedelta(days=10))

    start_datetime = datetime_from_start_range(datetime.now())
    end_datetime = datetime_from_start_range(start_datetime)

    return start_datetime, end_datetime


@pytest.fixture(scope="function")
def registered_feedback(
        registered_event: event_models.Event) -> feedback_models.Feedback:
    """
    Uses a previously declared fixture that returns a registered event in
    order to randomly generate a feedback object for it.

    Returns the original feedback object.
    """
    event_id = registered_event.get_id()
    feedback_data = generate_random_feedback(event_id)
    async_to_sync(feedback_utils.register_feedback)(feedback_data)

    return feedback_data


@pytest.fixture(scope="function")
def unregistered_feedback_object() -> feedback_models.Feedback:
    """
    Creates a random feedback object that is neither registered,
    not tied to a valid event, then returns it.
    """
    event_id = str(uuid4())
    feedback_data = generate_random_feedback(event_id)
    return feedback_data


def generate_random_feedback(
        event_id: event_models.EventId) -> feedback_models.Feedback:
    """
    Generates a random feedback for the given event.
    """
    fake = Faker()
    feedback_data = {
        "event_id": event_id,
        "comment": fake.text(),
    }
    return feedback_models.Feedback(**feedback_data)


def get_random_enum_member_value(enum_class: Enum) -> Enum:
    """
    Given an Enum class, returns a single, valid, random member of the class.
    """
    possible_tags = get_list_of_values_from_enum(enum_class)
    random_tag = random.choice(possible_tags)
    return random_tag


def get_list_of_values_from_enum(enum_class: Enum) -> List[Enum]:
    """
    Given an Enum, returns a list of all possible values of the class.
    """
    enum_values = enum_class.__members__
    return [enum_class(x) for x in enum_values]


@pytest.fixture(scope="function")
def valid_payload_data_dict() -> Dict[str, str]:
    """
    Fixture that generates a dict with 5 values

    Returns that dict so it can be used as a payload for tokens
    """
    random_data_dict = dict()
    for _ in range(5):
        random_key = str(uuid4())
        random_str_value = Faker().text()

        random_data_dict[random_key] = random_str_value

    return random_data_dict


@pytest.fixture(scope="function")
def valid_file_data_dict(
        valid_image_data_byte_buffer: bytes) -> Dict[str, Any]:
    """
    Uses a randomly generated image to returns a valid file dict.
    """
    file_data_dict = {"file": valid_image_data_byte_buffer}
    return file_data_dict


@pytest.fixture(scope="function")
def invalid_file_data_dict(
        invalid_image_data_byte_buffer: bytes) -> Dict[str, Any]:
    """
    Generates invalid file data dict to be used for failing tests.
    """
    file_data_dict = {"file": invalid_image_data_byte_buffer}
    return file_data_dict


@pytest.fixture(scope="function")
def valid_image_data_byte_buffer() -> bytes:
    """
    Generates a random image and saves it into a byte buffer,
    then returns the raw bytes.
    """
    image_data_buffer = io.BytesIO()
    image_data = Image.new('RGB', (60, 30), color='red')
    image_data.save(image_data_buffer, format="PNG")

    return image_data_buffer.getvalue()


@pytest.fixture(scope="function")
def invalid_image_data_byte_buffer() -> bytes:
    """
    Generates faulty (non-image) data and returns it as raw bytes.
    """
    bad_data_bytes = os.urandom(1024)
    image_data_buffer = io.BytesIO(bad_data_bytes)
    return image_data_buffer.getvalue()


@pytest.fixture(scope="function")
def valid_encoded_token_str(valid_payload_data_dict: Dict[str, Any]) -> str:
    """
    Creates a random dict and encodes it. It then
    packs and returns the token as an encoded string.
    """
    encoded_token = auth_models.Token.get_enc_token_str_from_dict(
        valid_payload_data_dict)
    return encoded_token


@pytest.fixture(scope="function")
def valid_header_token_dict(valid_encoded_token_str: str) -> Dict[str, str]:
    """
    Returns a valid dict to be used as the header for
    the test requests on the client.
    """
    header_dict = {"token": valid_encoded_token_str}
    return header_dict


@pytest.fixture(scope="function")
def invalid_token_header_dict(
        valid_header_token_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reverses the token string in the header making it invalid.
    Returns new, modified dict.
    """
    reversed_token_str = valid_header_token_dict["token"][::-1]
    invalid_token_header_dict = {"token": reversed_token_str}

    return invalid_token_header_dict


@pytest.fixture(scope="function")
def registered_image_data_and_id(
        random_valid_upload_file: fastapi.UploadFile) -> Dict[str, Any]:
    """
    Generates a random image and registers it to the database,
    returning both the image and the ID.
    """
    image_id = async_to_sync(
        image_utils.image_upload)(random_valid_upload_file)
    image_data_dict = {
        "image_id": image_id,
        "image_data": random_valid_upload_file
    }
    return image_data_dict


@pytest.fixture(scope="function")
def nonexistent_image_data_and_id(
        random_valid_upload_file: fastapi.UploadFile) -> Dict[str, Any]:
    """
    Generates a random image and ID, without registering it,
    returning both.
    """
    fake_image_id = str(uuid4())
    image_data_dict = {
        "image_id": fake_image_id,
        "image_data": random_valid_upload_file
    }
    return image_data_dict


@pytest.fixture(scope="function")
def random_valid_upload_file(
        valid_image_data_byte_buffer: bytes) -> fastapi.UploadFile:
    """
    Generates a random, valid `UploadFile` to be used to register images.
    """
    file_object = io.BytesIO(valid_image_data_byte_buffer)
    filename = "file"
    upload_file = fastapi.UploadFile(filename, file=file_object)
    return upload_file
