# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
# pylint: disable=redefined-outer-name
#       - this is how we use fixtures internally so this throws false positives
"""
Used to create tokens and tests encoding/decoding and checking for their expiration
"""
from datetime import timedelta
import time
from typing import Dict
from fastapi.testclient import TestClient
import jwt
from app import app
import models.auth as auth_models

client = TestClient(app)


def create_timedelta(minutes: int, sec: int) -> timedelta:
    delta = timedelta(minutes=minutes, seconds=sec)
    return delta

def check_decoded_token_is_dict(to_decode_token: str) -> bool:
    decoded_token_dict = from_payload_str_decode(to_decode_token) #Error considers encoded token as a str, not a Token
    if isinstance(decoded_token_dict,dict):
        return True
    else:
        return False

def check_token_expired(to_decode_token: str, token: auth_models.Token) -> bool:
    try:
        token.decode_token(to_decode_token)
    except jwt.ExpiredSignatureError:
        return True
    else:
        return False

class TestAuthUser:
    def test_encode_payload_data_ok(self, generate_random_token: auth_models.Token,
                          generate_random_str_data_dict: Dict[str, str]):
        """
        Generates a token as well as a payload before encoding it.
        It then looks to make sure it has been turned into a string that
        is a token.
        """
        token = generate_random_token()
        token_dict = generate_random_str_data_dict
        encoded_token = token.encode_token(token_dict)
        assert isinstance(encoded_token, str)

    def test_decode_token(self, generate_random_token: auth_models.Token,
                          generate_random_str_data_dict: Dict[str, str]):
        """
        Generates a token as well as a payload before encoding it.
        It then tries to decode it and checks if the payload is returned
        as a Dict.
        """
        token = generate_random_token()
        token_dict = generate_random_str_data_dict
        encoded_token = token.encode_token(token_dict)
        return check_decoded_token_is_dict(encoded_token)

    def test_token_expired(self, generate_random_token: auth_models.Token,
                           generate_random_str_data_dict: Dict[str, str]):
        """
        Generates a token, it's payload, and a timedelta set to 0.
        It then encodes it before attempting to decode it.
        Since the timedelta is set to 0, it should cause the token
        to expire when decoding.
        """
        token = generate_random_token()
        token_dict = generate_random_str_data_dict
        delta = create_timedelta(0, 0)
        encoded_token = token.encode_token(token_dict, delta)
        time.sleep(1)
        check_token_expired(encoded_token, token)


    def test_token_not_expired_default(self, generate_random_token:
                                       auth_models.Token,
                                       generate_random_str_data_dict:
                                       Dict[str, str]):
        """
        Generates a token and it's payload.
        It then encodes it before attempting to decode it.
        Since its using the default timedelta of 30 minutes,
        the token should not expire when decoding.
        """
        token = generate_random_token()
        token_dict = generate_random_str_data_dict
        encoded_token = token.encode_token(token_dict)
        token.decode_token(encoded_token)
        assert not token.is_expired

    def test_token_not_expired(self, generate_random_token: auth_models.Token,
                               generate_random_str_data_dict: Dict[str, str]):
        """
        Generates a token and it's payload.
        It then encodes it before attempting to decode it.
        Since its using the default timedelta of 30 minutes,
        the token should not expire when decoding.
        """
        token = generate_random_token()
        token_dict = generate_random_str_data_dict
        delta = create_timedelta(5, 0)
        encoded_token = token.encode_token(token_dict, delta)
        token.decode_token(encoded_token)
        assert not token.is_expired
