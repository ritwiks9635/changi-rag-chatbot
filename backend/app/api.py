from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.chatbot import answer_user_query
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# Request schema
class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        example="What are the top attractions at Jewel Changi?"
    )


# Response schema
class QueryResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest) -> QueryResponse:
    """
    Endpoint to answer user queries using the RAG pipeline.
    """
    try:
        # Call directly (no asyncio.to_thread)
        answer = answer_user_query(request.query)

        return QueryResponse(answer=answer)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception:
        logger.exception("Unexpected error in /ask endpoint")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )

