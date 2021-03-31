"""
Endpoints for admin only calls.

These endpoints overlap heavily with the `user` endpoints,
but have different schemas and should be logically/physically
separated so as to never have a data or logic mix.
"""
from fastapi import APIRouter
from models import users as models
from models import events as events_model
from docs import admin as docs
from util import users as utils
from util import events as utils_events

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

@router.get("/admin/events_queue",
            response_model=events_model.AllEventsQueryResponse,
            description=docs.get_all_events_desc,
            summary=docs.get_all_events_summ,
            tags=["Admin"],
            status_code=200)
async def get_all_events_in_queue():
    """
    Endpoint for returning events in the queue.
    """
    events = await utils_events.get_events_queue()
    return events



@router.post("/admin/decide_event",
            response_model=events_model.EventQueryResponse,
            description=docs.get_event_desc,
            summary=docs.get_event_summ,
            tags=["Admin"],
            status_code=200)
async def approve_or_deny_event(choice: bool, event_id: events_model.EventId):
    """
    Passes in a boolean that depending on which, changes to approve or denied
    to the event.
    """
    await utils_events.change_event_approval(event_id, choice)
    await utils_events.remove_event_from_queue(event_id)
    return event_id