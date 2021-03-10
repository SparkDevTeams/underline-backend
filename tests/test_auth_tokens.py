# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
# pylint: disable=redefined-outer-name
#       - this is how we use fixtures internally so this throws false positives
"""
Used to create tokens and tests encoding/decoding
and checking for their expiration
"""
from datetime import timedelta
from typing import Dict, Any
import time
from fastapi.testclient import TestClient
from app import app
import models.auth as auth_models
from models.auth import Token

client = TestClient(app)


def create_timedelta(minutes: int, sec: int, milli: int) -> timedelta:
    delta = timedelta(minutes=minutes, seconds=sec, milliseconds=milli)
    return delta

def check_expiry(token: auth_models.Token) -> bool:
    return token.check_if_expired()

class TestAuthUser:
    def test_encode_payload_data_ok(self, generate_random_str_data_dict: Dict[str, Any]):
        """
        Generates a token as well as a payload before encoding it.
        It then looks to make sure it has been turned into a string that
        is a token.
        """
        payload_dict = generate_random_str_data_dict
        encoded_token = Token.get_encoded_str_from_payload_dict(payload_dict)
        assert isinstance(encoded_token, str)

    def test_decode_token(self, generate_random_str_data_dict: Dict[str, Any]):
        """
        Generates a token as well as a payload before encoding it.
        It then tries to decode it and checks if the payload is returned
        as a Dict.
        """
        payload_dict = generate_random_str_data_dict
        encoded_token_str = Token.get_encoded_str_from_payload_dict(payload_dict)
        decoded_dict = Token.get_payload_dict_from_encoded_token(encoded_token_str)
        assert isinstance(decoded_dict, dict)


    def test_token_expired(self, generate_random_str_data_dict: Dict[str, Any]):
        """
        Generates a token, it's payload, and a timedelta set to 0.
        It then encodes it before attempting to decode it.
        Since the timedelta is set to 0, it should cause the token
        to expire when decoding.
        """
        payload_dict = generate_random_str_data_dict
        delta = create_timedelta(0, 0, 0)
        encoded_token_str = Token.get_encoded_str_from_payload_dict(payload_dict, delta)
        time.sleep(1)
        Token.check_if_expired(encoded_token_str)


    def test_token_not_expired_default(self, generate_random_str_data_dict: Dict[str, Any]):
        """
        Generates a token and it's payload.
        It then encodes it before attempting to decode it.
        Since its using the default timedelta of 30 minutes,
        the token should not expire when decoding.
        """
        payload_dict = generate_random_str_data_dict
        encoded_token_str = Token.get_encoded_str_from_payload_dict(payload_dict)
        Token.check_if_expired(encoded_token_str)

    def test_token_not_expired(self, generate_random_str_data_dict: Dict[str, Any]):
        """
        Generates a token and it's payload.
        It then encodes it before attempting to decode it.
        This time it uses a generated timedelta of 5 minutes.
        """

        payload_dict = generate_random_str_data_dict
        delta = create_timedelta(5, 0, 0)
        encoded_token_str = Token.get_encoded_str_from_payload_dict(payload_dict, delta)
        Token.check_if_expired(encoded_token_str)
