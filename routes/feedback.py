from fastapi import APIRouter, Response

from models import events as eventModel
from models import feedback as feedbackModel
from docs import feedback as docs
import logging
import util.feedback as utils
from starlette.exceptions import HTTPException

router = APIRouter()


@router.delete(
    "/feedback/delete/{event_id}/{feedback_id}",
    description=docs.delete_feedback_desc,
    summary=docs.delete_feedback_summ,
    tags=["Feedback"],
    status_code=204,
)
async def delete_feedback(event_id, feedback_id):
    # perform deletion
    await utils.delete_feedback(event_id, feedback_id)

    # prevent console error
    return Response(
        status_code=204
    )  # https://github.com/tiangolo/fastapi/issues/717#issuecomment-583826657


@router.post(
    "/feedback/add",
    response_model=feedbackModel.registration_response,
    description=docs.register_feedback_desc,
    summary=docs.register_feedback_summ,
    tags=["Feedback"],
    status_code=201,
)
async def add_feedback(form: feedbackModel.registration_form):
    # send the form data and DB instance to util.users.register_user
    feedback_id = await utils.add_feedback(form)

    # return response in reponse model
    return feedbackModel.registration_response(feedback_id=feedback_id)


@router.get("/feedback/{feedback_id}",
            description=docs.get_feedback_by_id_desc,
            summary=docs.get_feedback_by_id_summ,
            tags=["Feedback"],
            response_model=feedbackModel.Feedback,
            status_code=201)
async def get_feedback(feedback_id):
    feedback_data = await utils.get_feedback(feedback_id)
    return feedbackModel.Feedback(**feedback_data)
