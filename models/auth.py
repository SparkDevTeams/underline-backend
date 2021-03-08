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
from pydantic import BaseModel
import jwt


class Token(BaseModel):
    """
    Main top-level Token model. Holds a key for decoding,
    the type of algorithm, a default 30 minute expiry date,
    and a bool for checking if its expired or not
    """

    key: str = "00cb508e977fd82f27bf05e321f596b63bf2d" \
               "9f2452829e787529a52e64e7439"
    algorithm: str = "HS256"
    time_left: int = 30
    is_expired: bool = False

    @classmethod
    def from_payload_data(cls, payload_str: str): #getting a string returning a token
        token = cls()

        #decoded_data = decode_token(payload_str);
        return decoded_data

    @classmethod
    def from_payload_str_decode(cls, payload_str) -> Dict:
        token = cls()
        payload_str = token.decode_token(payload_str)
        return payload_str

    def encode_token(self, payload: Dict[str, Any], expiry_time:
                    Optional[timedelta] = None) -> str:
        """
        Encodes the token, has an optional expiry date for input and
        returns the encoded token as a string
        """
        if expiry_time:
            expire = datetime.utcnow() + expiry_time
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.time_left)
        time_payload = {'exp': expire}
        payload.update(time_payload)
        encoded_token_str = jwt.encode(payload, self.key, self.algorithm)
        return encoded_token_str

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Takes a token, decodes it, and returns it as a Dict
        """
        try:
            decoded_token_dict = jwt.decode(token, self.key, self.algorithm)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            self.is_expired = True
        return decoded_token_dict

    def check_if_expired(self) -> bool:
        """
        Returns the token's expiry status
        """
        return self.is_expired


