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
async def validate_token(user_id_from_token: str = Depends(
    utils.get_user_id_from_header_and_check_existence)):
    del user_id_from_token  # unused var
