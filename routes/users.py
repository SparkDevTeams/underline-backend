"""
Endpoint routers for users.

Eventually might need to handle auth here as well, so write code as if
that was an upcoming feature.
"""

from typing import Optional, Dict, Any
from fastapi import Header, APIRouter
from models import users as models
from docs import users as docs
import util.users as utils

router = APIRouter()


@router.post(
    "/users/register",
    response_model=models.UserRegistrationResponse,
    description=docs.registration_desc,
    summary=docs.registration_summ,
    tags=["Users"],
    status_code=201,
)
async def register_user(form: models.UserRegistrationForm,
token_header: Dict[str, Any] = Header(None)):
    # send the form data and DB instance to util.users.register_user
    user_id = await utils.register_user(form)

    # return response in reponse model
    return models.UserRegistrationResponse(user_id=user_id)


@router.delete(
    "/users/delete",
    description=docs.delete_user_desc,
    summary=docs.delete_user_summ,
    tags=["Users"],
    status_code=204,
)
async def delete_user(identifier: models.UserIdentifier):
    await utils.delete_user(identifier)


@router.post("/users/find",
             response_model=models.UserInfoQueryResponse,
             description=docs.find_user_by_identifier_desc,
             summary=docs.find_user_by_identifier_summ,
             tags=["Users"],
             status_code=200)
async def get_user(identifier: models.UserIdentifier):
    user_data = await utils.get_user_info_by_identifier(identifier)
    return models.UserInfoQueryResponse(**user_data.dict())
