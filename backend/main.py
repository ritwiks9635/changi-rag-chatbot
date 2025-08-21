from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Environment configuration
ENV = os.getenv("ENV", "development")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(
    title="Changi Airport Chatbot",
    description="Production-grade RAG Chatbot using Gemini + Pinecone",
    version="1.0.0"
)

# CORS setup — secure in prod, flexible in dev
if ENV == "development":
    allow_origins = ["*"]
else:
    allow_origins = [FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api.router, prefix="/api")


@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Simple health check endpoint for monitoring and deployment validation.
    """
    logger.info("Health check request received.")
    return {"status": "ok", "environment": ENV}
