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


class Token:
    """
    Main top-level Token model. Holds a key for decoding,
    the type of algorithm, a default 30 minute expiry date,
    and a bool for checking if its expired or not
    """

    key: str = "00cb508e977fd82f27bf05e321f596b63bf2d" \
      "9f2452829e787529a52e64e7439"
    time_left: int = 30
    is_expired: bool = False

    def __init__(self, payload_dict: Dict[str, Any]):
        """
        Takes in a dict of data to be encoded in the JWT.
        """
        self.payload_dict = payload_dict
        self.encoded_token_str = self.get_encoded_token_str()

    @classmethod
    def from_encoded_token_str(cls, encoded_token_str: str):
        """
        Factory method that takes in an encoded JWT str
        and returns an instance of Token.
        """
        token = cls()
        token.encoded_token_str = encoded_token_str
        return token

    def get_encoded_token_str(self,
                     expiry_time: Optional[timedelta] = None) -> str:
        """
        Encodes the token, has an optional expiry date for input and
        returns the encoded token as a string
        """
        if expiry_time:
            expire = datetime.utcnow() + expiry_time
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.time_left)
        time_payload = {'exp': expire}
        self.payload_dict.update(time_payload)
        encoded_token_str = jwt.encode(self.payload_dict, self.key,
                                       algorithm="HS256")
        return encoded_token_str

    def get_decoded_token_dict(self) -> Dict[str, Any]:
        """
        Takes a token, decodes it, and returns it as a Dict
        """
        try:
            decoded_token_dict = jwt.decode(self.encoded_token_str, self.key,
                                            algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            self.is_expired = True
        else:
            return decoded_token_dict

    def check_if_expired(self) -> bool:
        """
        Returns the token's expiry status
        """
        return self.is_expired
