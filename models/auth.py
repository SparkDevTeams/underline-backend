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
from typing import Optional, Dict
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
    def encode_token(self, payload: Dict, expiry_time:
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
        encoded = jwt.encode(payload, self.key, self.algorithm)
        return encoded

    def decode_token(self, token: str) -> Dict:
        """
        Takes a token, decodes it, and returns it as a Dict
        """
        try:
            decoded = jwt.decode(token, self.key, self.algorithm)
        except jwt.ExpiredSignatureError:
            self.is_expired = True
        except jwt.DecodeError:
            self.is_expired = True
        return decoded

    def check_if_expired(self) -> bool:
        """
        Returns the token's expiry status
        """
        return self.is_expired

    def get_key(self) -> str:
        """
        Returns the token's key
        """
        return self.key

    def set_key(self, new_key: str):
        """
        lets the key be changed if needed
        """
        self.key = new_key

    def get_algorithm(self) -> str:
        """
        Returns the token's algorithm
        """
        return self.algorithm

    def set_algorithm(self, new_algo: str):
        """
        Lets the algorithm be changed if needed
        """
        self.algorithm = new_algo
