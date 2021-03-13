# pylint: disable=no-self-use
#       - pydantic validators use cls instead of self; theyre not instance based
# pylint: disable=line-too-long
#       - This is temporary, a better name will be issued
# #pylint: disable=invalid-name
#       - This is temporary, a better name will be issued
"""
Holds methods which perform several operations on the
incoming Header string, which is expected to be a JWK.
Additional functionality to validate and decode the
incoming JWK.
"""

from typing import Dict, Any
from fastapi import Header
import jwt
#from jose import jwt

from models.auth import Token
from models import exceptions



async def get_auth_token_from_header(token: str = Header(None)) -> str:
    """
    Attempts to get the auth token string from the request header,
    returning it if available, else raises an authentication error.
    """
    valid = check_token_valid(token)
    if valid:
        jwk_string = token
    else:
        raise exceptions.InvalidAuthHeaderException

    return jwk_string

async def get_and_decode_auth_token_from_header(token: str = Header(None)) -> str:
    """
    Attempts to get the auth token string from the request header,
    and, in the process, decodes the token, returning the payload if valid,
    else raising an authorization exception
    """
    valid = check_token_valid(token)
    if valid:
        jwk_string = token
    else:
        raise exceptions.InvalidAuthHeaderException
    auth_token = Token.get_dict_from_enc_token_str(jwk_string)
    # TODO: Something's funky about this function, ask Felipe
    return auth_token


# NOTE: placeholder code for the sole purpose of writing out the functions above
async def check_token_valid(token: str) -> bool:
    """
    Placeholder function for checking if a token is decodable (i.e. valid)
    """
    valid = Token.check_if_valid(token)
    return valid

async def get_payload_from_decoded_token(token: str) -> Dict[str, Any]:
    """
    Placeholder function for decoding a valid token and returning the payload.
    """
    valid = check_token_valid(token)
    if not valid:
        raise jwt.exceptions.InvalidTokenError
    payload = Token.get_dict_from_enc_token_str(token)

    return payload
