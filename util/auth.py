"""
Has some helper/util functions for general authentication handling.
"""
from fastapi import Header

async def get_auth_token_from_header(token: str = Header(None)) -> str:
    pass