from fastapi import APIRouter

from app.schemas.ai import AskRequest, AskResponse
from app.services.ai_service import AIService


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)


ai_service = AIService()


@router.post(
    "/ask",
    response_model=AskResponse
)
def ask_hospice_ai(
    request: AskRequest
):
    return ai_service.ask(
        question=request.question,
        state=request.state,
        ownership=request.ownership,
        top_k=request.top_k,
        mode=request.mode,
        thread_id=request.thread_id
    )