# pylint: disable=unsubscriptable-object
#       - this is actually a pylint bug that hasn't been resolved.
# pylint: disable=fixme
#       - don't want to break lint but also don't want to create tickets.
#         as soon as this is on the board, remove this disable.
# pylint: disable=no-self-argument
#       - pydantic models are technically class models, so they dont use self.
# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
"""
Holds the database models for token operations.
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import jwt

from config.main import JWT_SECRET_KEY, JWT_EXPIRY_TIME


class Token:
    """
    Main top-level Token model. Holds a key for decoding,
    the type of algorithm, a default 30 minute expiry date,
    and a bool for checking if its expired or not
    """

    # get payload dict from encoded token string
    # get encoded token str from payload dict
    # check if expired
    # check if valid/decodable

    @staticmethod
    def get_payload_dict_from_encoded_token(
            encoded_token_str: str) -> Dict[Any, Any]:
        valid = Token.check_if_valid(encoded_token_str)
        not_expired = Token.check_if_expired(encoded_token_str)
        if valid and not_expired:
            payload_dict = jwt.decode(encoded_token_str,
                                      JWT_SECRET_KEY,
                                      algorithms=["HS256"])
            return payload_dict
        else:
            payload_dict = {'Error:', 'not valud'}
            return payload_dict

    @staticmethod
    def get_encoded_str_from_payload_dict(
            payload_dict: Dict[Any, Any],
            expiry_time: Optional[timedelta] = None) -> str:

        custom_expiry_time_set = expiry_time is not None

        if custom_expiry_time_set:
            expire = datetime.utcnow() + expiry_time
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_TIME)

        time_payload = {'exp': expire}
        payload_dict.update(time_payload)
        encoded_token_str = jwt.encode(payload_dict,
                                       JWT_SECRET_KEY,
                                       algorithm="HS256")
        return encoded_token_str

    @staticmethod
    def check_if_expired(encoded_token_str: str) -> bool:
        try:
            jwt.decode(encoded_token_str, JWT_SECRET_KEY, algorithms=["HS256"])
            return False
        except jwt.ExpiredSignatureError:
            return True

    @staticmethod
    def check_if_valid(encoded_token_str: str) -> bool:
        try:
            jwt.decode(encoded_token_str, JWT_SECRET_KEY, algorithms=["HS256"])
            return True
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError,
                jwt.exceptions.ExpiredSignatureError):
            return False
