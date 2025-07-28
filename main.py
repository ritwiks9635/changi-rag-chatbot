from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api

app = FastAPI(
    title="Changi Airport Chatbot",
    description="Production-grade RAG Chatbot using Gemini + Pinecone",
    version="1.0.0"
)

# Enable CORS for development / frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api.router, prefix="/api")
