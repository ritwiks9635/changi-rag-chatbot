from typing import List
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.vector_store import retrieve_relevant_docs
from app.config import config

RAG_PROMPT_TEMPLATE = """
You are a professional assistant trained to answer questions about **Changi Airport** and **Jewel Changi Airport** only.

Your job:
- Use only the context provided below.
- If the context contains relevant information — even partially — answer the user’s question clearly and professionally.
- If details are not explicitly stated, but **reasonable guidance** can be inferred (e.g., where to find it, how to get help), give that.
- If the question is unrelated to Changi Airport or Jewel, respond:
  "Sorry, I’m designed to assist with Changi Airport and Jewel Changi Airport only."

Avoid phrases like “Based on the context” or “The context mentions”.

---

📚 Context:
{context}

---

❓ Question:
{question}

---

💬 Answer:
"""

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=RAG_PROMPT_TEMPLATE,
)

# def get_llm() -> ChatGoogleGenerativeAI:
#     return ChatGoogleGenerativeAI(
#         model="gemini-1.5-flash-latest",
#         temperature=0.4,
#         google_api_key=config.GEMINI_API_KEY
#     )

def get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama3-8b-8192",
        temperature=0.4,
        groq_api_key=config.GROQ_API_KEY
    )

def clean_context(chunks: List[str]) -> List[str]:
    cleaned = []
    for chunk in chunks:
        # Remove social icons, share buttons, junk lines
        lines = chunk.split("\n")
        cleaned_lines = [
            line for line in lines
            if len(line.strip()) > 15 and
               not any(x in line.lower() for x in ["save share", "facebook", "tiktok", "cookie", "terms", "sign up", "oops", "copyright"])
        ]
        combined = " ".join(cleaned_lines).strip()
        if len(combined) > 50:
            cleaned.append(combined)
    return cleaned

def format_context(chunks: List[str]) -> str:
    return "\n\n".join(f"[{i+1}] {chunk}" for i, chunk in enumerate(clean_context(chunks)))

def answer_user_query(query: str) -> str:
    try:
        context_chunks = retrieve_relevant_docs(query, top_k=5)
        if not context_chunks:
            return "Sorry, I could not find that in the documentation."

        prompt = QA_PROMPT.format_prompt(
            context=format_context(context_chunks),
            question=query
        ).to_string()

        llm = get_llm()
        response = llm.invoke(prompt)
        return response.content.strip() if hasattr(response, "content") else str(response)

    except Exception as e:
        return f"Sorry, an error occurred while answering your question: {str(e)}"
