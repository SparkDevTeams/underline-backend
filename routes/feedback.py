"""
Endpoints for feedback operations.

Due to the nature of feedback being tied to events, lots of this code
will have cross reference with `event_id`'s.

This is as much coupling as should be allowed here; we need to leave the
actual union of events and feedback to code in `util/` files to remain
flexible and have this code be implementation-agnostic.
"""

from fastapi import APIRouter

from models import feedback as feedback_models
from models import events as event_models
from docs import feedback as docs
import util.feedback as utils

router = APIRouter()
ROUTER_TAG = "Feedback"


@router.delete(
    "/feedback/delete",
    description=docs.delete_feedback_desc,
    summary=docs.delete_feedback_summ,
    tags=[ROUTER_TAG],
    status_code=204,
)
async def delete_feedback(event_id: event_models.EventId,
                          feedback_id: feedback_models.FeedbackId):
    """
    Endpoint for deleting feedback for an event given IDs for both.

    Returns nothing if it is successful (204).
    """
    # perform deletion
    await utils.delete_feedback(event_id, feedback_id)


@router.post(
    "/feedback/add",
    response_model=feedback_models.FeedbackRegistrationResponse,
    description=docs.register_feedback_desc,
    summary=docs.register_feedback_summ,
    tags=[ROUTER_TAG],
    status_code=201,
)
async def add_feedback(form: feedback_models.FeedbackRegistrationRequest):
    """
    Endpoint to register a feedback to an event.
    """
    # send the form data and DB instance to util.users.register_user
    feedback_id = await utils.register_feedback(form)

    # return response in reponse model
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
