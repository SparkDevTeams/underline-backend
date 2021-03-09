"""
Endpoitns for admin only calls.

These endpoints overlap heavily with the `user` endpoints,
but have different schemas and should be logically/physically
separated so as to never have a data or logic mix.
"""
from fastapi import APIRouter
from models import users as models
from docs import admin as docs
from util import admin as utils

router = APIRouter()


@router.post(
        "/admin/register",
        response_model=models.,
        description=docs.,
        summary=docs.,
        tags=["Admin"],
        status_code=201,
        )
async def register_admin(form: models.):
    raise Exception
#  user_id = await utils.register_user(form)
    #  return models.UserRegistrationResponse(user_id=user_id)


@router.delete(
        "/admin/delete",
        description=docs.delete_user_desc,
        summary=docs.delete_user_summ,
        tags=["Admin"],
        status_code=204,
        )
async def delete_user(identifier: models.UserIdentifier):
    #  await utils.delete_user(identifier)


@router.post("/admin/find",
        response_model=models.,
        description=docs.,
        summary=docs.,
        tags=["Admin"],
        status_code=200)
async def get_user(identifier: models.):
    #  user_data = await utils.get_user_info_by_identifier(identifier)
    #  return models.UserInfoQueryResponse(**user_data.dict())


@router.post("/admin/login",
        response_model=models.,
        description=docs.,
        summary=docs.,
        tags=["Admin"],
        status_code=200)
async def login_user(login_form: models.):
    #  return await utils.attempt_user_login(login_form)
