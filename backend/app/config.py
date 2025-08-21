import os
from dotenv import load_dotenv
from typing import Optional

class ConfigError(Exception):
    """Custom exception for missing configuration values."""
    pass

class Config:
    def __init__(self):
        load_dotenv()

        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")
        self.PINECONE_INDEX = os.getenv("PINECONE_INDEX")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

        self.validate()

    def validate(self):
        missing = []
        if not self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not self.PINECONE_API_KEY:
            missing.append("PINECONE_API_KEY")
        if not self.PINECONE_ENV:
            missing.append("PINECONE_ENVIRONMENT")
        if not self.PINECONE_INDEX:
            missing.append("PINECONE_INDEX")
        if not self.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")

        if missing:
            raise ConfigError(f"Missing environment variables: {', '.join(missing)}")


config = Config()