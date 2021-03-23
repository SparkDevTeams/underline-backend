"""
Holds methods which perform several operations on the
incoming Header string, which is expected to be a JWT.
Additional functionality to validate and decode the
incoming JWT.
"""

from typing import Dict, Any
from fastapi import Header
from models.auth import Token
from models import exceptions


async def get_auth_token_from_header(token: str = Header(None)) -> str:
    """
    Attempts to get the auth token string from the request header,
    returning it if available, else raises an authentication error.
    """
    await check_token_data_passed_in(token)
    await check_token_str_is_decodable(token)

    return token


async def get_payload_from_token_header(token: str = Header(None)) -> Dict[
        str, Any]:
    """
    Attempts to get the auth token string from the request header,
    and, in the process, decodes the token, returning the payload if valid,
    else raising an authorization exception
    """
    await check_token_data_passed_in(token)
    await check_token_str_is_decodable(token)

    token_payload = Token.get_dict_from_enc_token_str(token)
    return token_payload


async def check_token_data_passed_in(token_str: str) -> None:
    """
    Checks if the token data exists and was passed in.
    If not, raises invalid data exception.
    """
    if not token_str:
        detail = "Missing header token string!"
        raise exceptions.InvalidDataException(detail=detail)


async def check_token_str_is_decodable(token_str: str) -> None:
    """
    Checks if encoded token string passed in is valid
    and decodable.

    If not, raises an authentication error.
    """
    invalid_token_data = not Token.check_if_valid(token_str)
    if invalid_token_data:
        raise exceptions.InvalidAuthHeaderException
