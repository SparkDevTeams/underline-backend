"""
Endpoint routers for authentication/authorization handling
"""
from fastapi import APIRouter
from models import auth as models
from docs import auth as docs
from util import auth as utils

router = APIRouter()


@router.post(
    "/auth/validate",
    description=docs.auth_validate_token_desc,
    summary=docs.auth_validate_token_summ,
    tags=["Auth"],
    status_code=204,
)
async def validate_token(token_str=Depends(utils)):
    pass
