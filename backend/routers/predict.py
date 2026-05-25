"""
Cup competition prediction endpoint with streaming response.
"""

import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from chatbot.predictor import stream_prediction, build_context_summary

router = APIRouter(prefix="/predict", tags=["Predict"])

SUPPORTED_COMPETITIONS = [
    "UEFA Champions League",
    # Future: "UEFA Europa League", "FA Cup", "DFB Pokal", etc.
]


class PredictRequest(BaseModel):
    team1_id: str
    team2_id: str
    competition: str = "UEFA Champions League"
    message: Optional[str] = None


@router.post("/match")
async def predict_match(req: PredictRequest):
    """
    Stream a match prediction. Uses RAG: fetches live team stats from Supabase
    and injects them as context before calling Claude Haiku.

    Returns a streaming text/event-stream response.
    """
    if req.competition not in SUPPORTED_COMPETITIONS:
        raise HTTPException(
            400,
            detail=f"Unsupported competition. Supported: {SUPPORTED_COMPETITIONS}"
        )

    user_message = req.message or f"Predict the match between the two teams in the {req.competition}."

    async def event_stream():
        async for chunk in stream_prediction(
            team1_id=req.team1_id,
            team2_id=req.team2_id,
            competition=req.competition,
            user_message=user_message,
        ):
            # Server-sent events format
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/context")
async def get_context(team1_id: str, team2_id: str):
    """
    Returns the raw stats context used for the prediction.
    Powers the 'Show data used' panel in the frontend.
    """
    context = build_context_summary(team1_id, team2_id)
    return context
