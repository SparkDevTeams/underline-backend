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


"""
put verb chosen over post due to my understanding of a SO post. Reference:
https://stackoverflow.com/questions/630453/put-vs-post-in-rest#:~:text=You%20can%20PUT%20a%20resource,the%20thing%20you%20will%20create.
patch might be good here? Since we are modifying the User model, but replacing the individual fields, that left
me a bit confused on which verb to use.
"""


@router.patch("/users/update",
              response_model=models.UserUpdateResponse,
              description=docs.update_user_desc,
              summary=docs.update_user_summ,
              tags=["Users"],
              status_code=200)
async def update_user(update_form: models.UserUpdateForm):
    return await utils.update_user(update_form)

