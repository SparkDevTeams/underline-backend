# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
# pylint: disable=redefined-outer-name
#       - this is how we use fixtures internally so this throws false positives
"""
Testing Tokens by encoding/decoding and checking for their expiration
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


class TestAuthUser:
    def test_encode_token(self, generate_random_token: auth_models.Token,
                          generate_dict_for_token_auth: Dict[str, str]):
        """
        Generates a token as well as a payload before encoding it.
        It then looks to make sure it has been turned into a string that
        is a token.
        """
        token = generate_random_token()
        token_dict = generate_dict_for_token_auth
        encoded_token = token.encode_token(token_dict)
        assert isinstance(encoded_token, str)

    def test_decode_token(self, generate_random_token: auth_models.Token,
                          generate_dict_for_token_auth: Dict[str, int]):
        """
        Generates a token as well as a payload before encoding it.
        It then tries to decode it and checks if the payload is returned
        as a Dict.
        """
        token = generate_random_token()
        token_dict = generate_dict_for_token_auth
        encoded_token = token.encode_token(token_dict)
        decode = token.decode_token(encoded_token)
        assert isinstance(decode, dict)

    def test_token_expired(self, generate_random_token: auth_models.Token,
                           generate_dict_for_token_auth: Dict[str, int]):
        """
        Generates a token, it's payload, and a timedelta set to 0.
        It then encodes it before attempting to decode it.
        Since the timedelta is set to 0, it should cause the token
        to expire when decoding.
        """
        token = generate_random_token()
        token_dict = generate_dict_for_token_auth
        delta = create_timedelta(0, 0)
        encoded_token = token.encode_token(token_dict, delta)
        time.sleep(1)
        token.decode_token(encoded_token)
        assert jwt.ExpiredSignatureError

    def test_token_not_expired_default(self, generate_random_token:
                                       auth_models.Token,
                                       generate_dict_for_token_auth:
                                       Dict[str, int]):
        """
        Generates a token and it's payload.
        It then encodes it before attempting to decode it.
        Since its using the default timedelta of 30 minutes,
        the token should not expire when decoding.
        """
        token = generate_random_token()
        token_dict = generate_dict_for_token_auth
        encoded_token = token.encode_token(token_dict)
        token.decode_token(encoded_token)
        assert not token.is_expired

    def test_token_not_expired(self, generate_random_token: auth_models.Token,
                               generate_dict_for_token_auth: Dict[str, int]):
        """
        Generates a token and it's payload.
        It then encodes it before attempting to decode it.
        Since its using the default timedelta of 30 minutes,
        the token should not expire when decoding.
        """
        token = generate_random_token()
        token_dict = generate_dict_for_token_auth
        delta = create_timedelta(5, 0)
        encoded_token = token.encode_token(token_dict, delta)
        token.decode_token(encoded_token)
        assert not token.is_expired
