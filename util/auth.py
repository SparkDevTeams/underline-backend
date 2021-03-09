"""
Has some helper/util functions for general authentication handling.
"""

import json
import datetime

from typing import Dict, List, Optional, Any
from fastapi import Header, HTTPException
from jose import jwt

import models.auth as token_model
from models import exceptions



async def get_auth_token_from_header(token: str = Header(None)) -> str:
    """
    Attempts to get the auth token string from the request header,
    returning it if available, else raises an authentication error.
    """
    if token is None:
        raise exceptions.InvalidAuthHeaderException(
        detail='Token is empty')
    parts = token.split()

    if parts[0].lower() != "bearer":
        raise exceptions.InvalidAuthHeaderException(
        detail='Authorization header must start with Bearer')
    elif len(parts) == 1:
        raise exceptions.InvalidAuthHeaderException(
        detail='Authorization token not found')
    elif len(parts) > 2:
        raise exceptions.InvalidAuthHeaderException(
        detail='Authorization header be Bearer token')

    auth_token = parts[1]
    return auth_token

async def get_and_decode_auth_token_from_header(token: str = Header(None)) -> str: #pylint: disable=invalid-name
    """
    Attempts to get the auth token string from the request header,
    and, in the process, decodes the token, returning the payload if valid,
    else raising an authorization exception
    """
    auth_token = get_auth_token_from_header(token)
    if not check_token_valid(auth_token):
        raise exceptions.InvalidAuthHeaderException

    pass


# NOTE: placeholder code for the sole purpose of writing out the functions above
async def check_token_valid(token: str) -> bool:
    """
    Placeholder function for checking if a token is decodable (i.e. valid)
    """

    

    return len(token) < 5

async def get_payload_from_decoded_token(token: str) -> Dict[str, Any]:
    """
    Placeholder function for decoding a valid token and returning the payload.
    """
    return {"data": token.upper()}

    