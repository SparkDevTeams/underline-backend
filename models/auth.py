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
    @classmethod
    def from_encoded_token_str(cls, encoded_token_str: str):
        """
        Factory method that takes in an encoded JWT str
        and returns an instance of Token.
        """
        token = cls()  # pylint: disable=no-value-for-parameter
        token.encoded_token_str = encoded_token_str
        return token

    # get payload dict from encoded token string
    # get encoded token str from payload dict
    # check if expired
    # check if valid/decodable

    def get_encoded_token_str(self,
                              expiry_time: Optional[timedelta] = None) -> str:
        """
        Encodes the token, has an optional expiry date for input and
        returns the encoded token as a string
        """
        non_default_expiry_time = bool(expiry_time)

        if non_default_expiry_time:
            expire = datetime.utcnow()
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.time_left)

        time_payload = {'exp': expire}
        self.payload_dict.update(time_payload)
        encoded_token_str = jwt.encode(self.payload_dict,
                                       JWT_SECRET_KEY,
                                       algorithm="HS256")
        return encoded_token_str

    def get_decoded_token_dict(self) -> Dict[str, Any]:
        """
        Takes a token, decodes it, and returns it as a Dict
        """
        try:
            decoded_token_dict = jwt.decode(self.encoded_token_str,
                                            JWT_SECRET_KEY,
                                            algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            self.is_expired = True
        else:
            return decoded_token_dict

    def check_if_valid(self) -> bool:
        """
        Checks if the decoding doesn't raise
        any errors that make the token
        invalid
        """
        try:
            breakpoint()
            jwt.decode(self.encoded_token_str,
                       JWT_SECRET_KEY,
                       algorithms=["HS256"])
            return True
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError,
                jwt.exceptions.InvalidTokenError,
                jwt.exceptions.ExpiredSignatureError):
            breakpoint()
            return False
