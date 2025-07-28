from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.chatbot import answer_user_query

router = APIRouter()


# Request schema
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, example="What are the top attractions at Jewel Changi?")


# Response schema
class QueryResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest) -> QueryResponse:
    """
    Endpoint to answer user queries using the RAG pipeline.
    """
    try:
        answer = answer_user_query(request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
