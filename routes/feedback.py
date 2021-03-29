"""
Endpoints for feedback operations.

Due to the nature of feedback being tied to events, lots of this code
will have cross reference with `event_id`'s.

This is as much coupling as should be allowed here; we need to leave the
actual union of events and feedback to code in `util/` files to remain
flexible and have this code be implementation-agnostic.
"""

from fastapi import APIRouter, Depends

import util.feedback as utils
import util.auth as auth_utils
from docs import feedback as docs
from models import exceptions
from models import events as event_models
from models import feedback as feedback_models

router = APIRouter()
ROUTER_TAG = "Feedback"


@router.delete(
    "/feedback/delete",
    description=docs.delete_feedback_desc,
    summary=docs.delete_feedback_summ,
    tags=[ROUTER_TAG],
    status_code=204,
)
async def delete_feedback(
    event_id: event_models.EventId,
    feedback_id: feedback_models.FeedbackId,
    user_id_from_token: str = Depends(
        auth_utils.get_user_id_from_header_and_check_existence)):
    """
    Endpoint for deleting feedback for an event given IDs for both.

    Returns nothing if it is successful (204).
    """
    # perform deletion
    await utils.delete_feedback(event_id, feedback_id, user_id_from_token)


@router.post(
    "/feedback/add",
    response_model=feedback_models.FeedbackRegistrationResponse,
    description=docs.register_feedback_desc,
    summary=docs.register_feedback_summ,
    tags=[ROUTER_TAG],
    status_code=201,
)
async def add_feedback(
    form: feedback_models.FeedbackRegistrationRequest,
    user_id_from_token: str = Depends(
        auth_utils.get_user_id_from_header_and_check_existence)):
    """
    Endpoint to register a feedback to an event.
    """
    if user_id_from_token != form.creator_id:
        raise exceptions.UnauthorizedIdentifierData

    # send the form data and DB instance to util.users.register_user
    feedback_id = await utils.register_feedback(form)

    # return response in response model
    return feedback_models.FeedbackRegistrationResponse(
        feedback_id=feedback_id)


@router.get("/feedback/{feedback_id}",
            response_model=feedback_models.FeedbackQueryResponse,
            description=docs.get_feedback_by_id_desc,
            summary=docs.get_feedback_by_id_summ,
            tags=[ROUTER_TAG],
            status_code=201)
async def get_feedback(feedback_id):
    """
    Endpoint to query a feedback by ID.
    """
    feedback_data = await utils.get_feedback(feedback_id)
    return feedback_models.FeedbackQueryResponse(**feedback_data)
