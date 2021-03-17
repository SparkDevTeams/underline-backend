"""
Endpoints for admin only calls.

These endpoints overlap heavily with the `user` endpoints,
but have different schemas and should be logically/physically
separated so as to never have a data or logic mix.
"""
from fastapi import APIRouter
from models import users as models
from docs import admin as docs
from util import users as utils

router = APIRouter()


@router.post(
    "/admin/register",
    response_model=models.UserAuthenticationResponse,
    description=docs.admin_registration_desc,
    summary=docs.admin_registration_summ,
    tags=["Admin"],
    status_code=201,
)
async def register_admin(form: models.AdminUserRegistrationForm):
    user_id = await utils.register_user(form)
    auth_token_str = await utils.get_auth_token_from_user_id(user_id)

    return models.UserAuthenticationResponse(jwt=auth_token_str)


@router.delete(
    "/admin/delete",
    description=docs.admin_delete_user_desc,
    summary=docs.admin_delete_user_summ,
    tags=["Admin"],
    status_code=204,
)
async def delete_user(identifier: models.UserIdentifier):
    await utils.delete_user(identifier)


@router.post("/admin/find",
             response_model=models.AdminUserInfoQueryResponse,
             description=docs.admin_query_desc,
             summary=docs.admin_query_desc,
             tags=["Admin"],
             status_code=200)
async def get_user(identifier: models.UserIdentifier):
    user_data = await utils.get_user_info_by_identifier(identifier)
    return models.AdminUserInfoQueryResponse(**user_data.dict())


@router.post("/admin/login",
             response_model=models.UserAuthenticationResponse,
             description=docs.admin_login_desc,
             summary=docs.admin_login_summ,
             tags=["Admin"],
             status_code=200)
async def login_user(login_form: models.UserLoginForm):
    return await utils.login_user(login_form)
