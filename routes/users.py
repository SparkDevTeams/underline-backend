<<<<<<< HEAD
from pydantic import EmailStr
from fastapi import APIRouter
from starlette.exceptions import HTTPException
from models import users as models
from docs import users as docs
import logging
import util.users as utils

router = APIRouter()


@router.post(
    "/users/register",
    response_model=models.registration_response,
    description=docs.registration_desc,
    summary=docs.registration_summ,
    tags=["Users"],
    status_code=201,
)
async def register_user(form: models.registration_form):
    # receive data from client -> util.register method -> return user_id from DB insertion
    # send the form data and DB instance to util.users.register_user
    user_id = await utils.register_user(form)

    # return response in reponse model
    return models.registration_response(user_id=user_id)


@router.delete(
    "/users/delete",
    description=docs.delete_user_desc,
    summary=docs.delete_user_summ,
    tags=["Users"],
    status_code=204,
)
async def delete_user(email: str):
    # if email input is none, raise error
    if not email:
        raise HTTPException(status_code=400,
                            detail="Input invalid/not present")

    # Delete User
    await utils.delete_user(email)


@router.get("/users/find",
            response_model=models.Users,
            description=docs.find_user_by_email_desc,
            summary=docs.find_user_by_email_summ,
            tags=["Users"],
            status_code=201)
async def get_user(email: EmailStr):
    user_data = await utils.get_user_info(email)
    return models.Users(**user_data)
=======
"""
Endpoint routers for users.

Eventually might need to handle auth here as well, so write code as if
that was an upcoming feature.
"""
from fastapi import APIRouter
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
async def register_user(form: models.UserRegistrationForm):
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
>>>>>>> 559d0efdd9290f5413cd1bad9600779541811d95
