# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
# pylint: disable=redefined-outer-name
#       - this is how we use fixtures internally so this throws false positives
"""
Used to test encoding/decoding JWT tokens
and checking for their expiration
"""
from datetime import timedelta
from typing import Dict, Any
import time
from fastapi.testclient import TestClient
from app import app
from models.auth import Token

client = TestClient(app)


def create_timedelta(minutes: int, sec: int, milli: int) -> timedelta:
    """
    Creates timedelta in order to encode token with different times.
    """
    delta = timedelta(minutes=minutes, seconds=sec, milliseconds=milli)
    return delta


class TestAuthUser:
    def test_encode_payload_data_ok(self,
                                    valid_header_dict_with_user_id: Dict[str,
                                                                         Any]):
        """
        Creates a random dict and encodes it. It then
        makes sure it returns an encoded string.
        """
        encoded_token = Token.get_enc_token_str_from_dict(
            valid_header_dict_with_user_id)
        is_valid = Token.check_if_valid(encoded_token)
        if is_valid:
            assert isinstance(encoded_token, str)

    def test_decode_token(self, valid_header_dict_with_user_id: Dict[str,
                                                                     Any]):
        """
        Creates a random dict and encodes it. It then decodes it
        and makes sure it returns a dict.
        """
        encoded_token_str = Token.get_enc_token_str_from_dict(
            valid_header_dict_with_user_id)
        decoded_dict = Token.get_dict_from_enc_token_str(encoded_token_str)
        assert set(decoded_dict.keys()) == set(
            valid_header_dict_with_user_id.keys())

    def test_token_expired(self, valid_header_dict_with_user_id: Dict[str,
                                                                      Any]):
        """
        Creates a random dict and a timedelta.
        Timedelta is 0 which means the token should
        expire in 0 seconds. It then encodes the dict and
        timedelta together, then checks to make
        sure it is expired.
        """
        delta = create_timedelta(0, 0, 0)
        encoded_token_str = Token.get_enc_token_str_from_dict(
            valid_header_dict_with_user_id, delta)
        time.sleep(1)
        token_is_expired = Token.check_if_expired(encoded_token_str)
        assert token_is_expired

    def test_token_not_expired_default(
            self, valid_header_dict_with_user_id: Dict[str, Any]):
        """
        Creates a random dict. It then encodes the dict
        and then checks to make sure it is not expired as
        it uses the default expiry time.
        """
        encoded_token_str = Token.get_enc_token_str_from_dict(
            valid_header_dict_with_user_id)
        assert not Token.check_if_expired(encoded_token_str)

    def test_token_not_expired(self,
                               valid_header_dict_with_user_id: Dict[str, Any]):
        """
        Creates a random dict and a timedelta for 5 minutes.
        It then encodes the dict and timedelta together,
        then checks to make sure it is not expired.
        """
        delta = create_timedelta(5, 0, 0)
        encoded_token_str = Token.get_enc_token_str_from_dict(
            valid_header_dict_with_user_id, delta)
        assert not Token.check_if_expired(encoded_token_str)
