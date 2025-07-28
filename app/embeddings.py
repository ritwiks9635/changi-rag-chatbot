import time
from typing import List
import numpy as np
from tenacity import retry, wait_random_exponential, stop_after_attempt
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import config


_embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    task_type="retrieval_document",
    google_api_key=config.GEMINI_API_KEY,
)


@retry(wait=wait_random_exponential(min=2, max=20), stop=stop_after_attempt(5))
def _embed_batch(batch: List[str]) -> List[List[float]]:
    """
    Embed a batch of documents using Google Generative AI embeddings.
    Retries on transient API errors.
    """
    return _embedding_model.embed_documents(batch)


def embed_texts(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Embed a list of texts with batching and retry logic.
    """
    if not texts:
        return []

    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        print(f"[Embed] Processing batch {i // batch_size + 1} / {len(texts) // batch_size + 1}")

        try:
            embeddings = _embed_batch(batch)
            all_embeddings.extend(embeddings)
        except Exception as e:
            print(f"[Embedding Error] Batch {i}-{i+len(batch)} failed: {e}")
            time.sleep(5) 

    return all_embeddings


def get_gemini_embedding(query: str) -> np.ndarray:
    """
    Generate embedding for a user query using Gemini.
    """
    model = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        task_type="retrieval_query",
        google_api_key=config.GEMINI_API_KEY,
    )
    embedding = model.embed_query(query)
    return np.array(embedding)


def get_embedding_model_name() -> str:
    """
    Return the model identifier used for embeddings.
    """
    return "models/text-embedding-004"
