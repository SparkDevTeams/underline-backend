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
    response_model=models.UserAuthenticationResponse,
    description=docs.registration_desc,
    summary=docs.registration_summ,
    tags=["Users"],
    status_code=201,
)
async def register_user(form: models.UserRegistrationForm):
    # send the form data and DB instance to util.users.register_user
    user_id = await utils.register_user(form)

    auth_token_str = await utils.get_auth_token_from_user_id(user_id)

    # return response in response model
    return models.UserAuthenticationResponse(jwt=auth_token_str)


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


@router.post("/users/login",
             response_model=models.UserAuthenticationResponse,
             description=docs.login_user_desc,
             summary=docs.login_user_summ,
             tags=["Users"],
             status_code=200)
async def login_user(login_form: models.UserLoginForm):
    return await utils.login_user(login_form)

@router.put("/users/add_event/",
             response_model=models.UserAddEventResponse,
             description=docs.user_add_event_desc,
             summary=docs.user_add_event_summ,
             tags=["Users"],
             status_code=201)
async def add_event_to_user(add_event_form: models.UserAddEventForm):
    return await utils.user_add_event(add_event_form)

@router.patch("/users/update",
              response_model=models.UserUpdateResponse,
              description=docs.update_user_desc,
              summary=docs.update_user_summ,
              tags=["Users"],
              status_code=200)
async def update_user(update_form: models.UserUpdateForm):
    return await utils.update_user(update_form)
