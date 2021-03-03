"""
Has some helper/util functions for general authentication handling.
"""
from fastapi import Header
import models.auth as token_model


from fastapi.security import OAuth2PasswordBearer

# async def get_auth_token_from_header(token: AuthTokenHeader = Header(None)) -> str:
#     # Authorization: Bearer <token>
#     # Bearer <token>
#     breakpoint()
#     token = token_model.Token.get_algorithm
#     return token



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

get_auth_token_from_header = oauth2_scheme