"""
Endpoint routers for authentication/authorization handling
"""
from fastapi import APIRouter, Depends
from docs import auth as docs
from util import auth as utils

router = APIRouter()


@router.get(
    "/auth/validate",
    description=docs.auth_validate_token_desc,
    summary=docs.auth_validate_token_summ,
    tags=["Auth"],
    status_code=204,
)
async def validate_token(token_str: str = Depends(
    utils.get_auth_token_from_header)):
    del token_str  # unused var
