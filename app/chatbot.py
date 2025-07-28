import numpy as np
from typing import List
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from app.vector_store import retrieve_relevant_docs
from app.config import config




# RAG Prompt Template
RAG_PROMPT_TEMPLATE = """
You are a helpful assistant for Changi Airport & Jewel Changi.

Answer the question below using ONLY the information provided in the context.
If the answer is not found in the context, say "Sorry, I could not find that in the documentation."

---

Context:
{context}

---

Question:
{question}
"""

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=RAG_PROMPT_TEMPLATE,
)


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Returns the Gemini Pro model for answer generation.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        temperature=0.3,
        google_api_key=config.GEMINI_API_KEY
    )


def format_context(chunks: List[str]) -> str:
    """
    Joins retrieved chunks into a single string context.
    """
    return "\n\n".join(chunks)


def answer_user_query(query: str) -> str:
    """
    Run a simple RAG pipeline:
    1. Embed and query Pinecone
    2. Format prompt with context + question
    3. Generate answer using Gemini
    """
    try:
        # Step 1: Retrieve relevant chunks from Pinecone
        context_chunks = retrieve_relevant_docs(query, top_k=5)

        if not context_chunks:
            return "Sorry, I could not find that in the documentation."

        # Step 2: Format the prompt correctly
        prompt = QA_PROMPT.format_prompt(
            context=format_context(context_chunks),
            question=query
        ).to_string()

        # Step 3: Generate answer using Gemini
        llm = get_llm()
        response = llm.invoke(prompt)

        return response.content

    except Exception as e:
        return f"Sorry, an error occurred while answering your question: {str(e)}"
