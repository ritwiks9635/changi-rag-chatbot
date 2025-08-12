import sys, os, asyncio, threading, nest_asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from dotenv import load_dotenv
import groq
import opik
from opik import Opik, track
from opik.evaluation import evaluate
from opik.evaluation.metrics import Hallucination, AnswerRelevance
from opik.evaluation.models import LiteLLMChatModel

from app.chatbot import answer_user_query, retrieve_relevant_docs

# Allow nested event loops
nest_asyncio.apply()

# Patch threads to have loops
_original = threading.Thread.__init__
def patched_init(self, *a, **k):
    _original(self, *a, **k)
    _orig_run = self.run
    def run_wrapped():
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        _orig_run()
    self.run = run_wrapped
threading.Thread.__init__ = patched_init

# Load environment
load_dotenv()
OPIK_API_KEY = os.getenv("OPIK_API_KEY")
OPIK_WORKSPACE = os.getenv("OPIK_WORKSPACE_ID")
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


if not all([OPIK_API_KEY, OPIK_WORKSPACE, OPIK_PROJECT_NAME, GROQ_API_KEY, GEMINI_API_KEY]):
    raise ValueError("Missing credentials in .env - Ensure OPIK_API_KEY, OPIK_WORKSPACE, OPIK_PROJECT_NAME, GROQ_API_KEY, and GEMINI_API_KEY (or GOOGLE_API_KEY) are set.")

# Configure Opik
opik.configure(api_key=OPIK_API_KEY, workspace=OPIK_WORKSPACE)

# Groq client for your RAG generation (remains unchanged)
groq_client = groq.Groq(api_key=GROQ_API_KEY)

@track
def traced_retrieve_relevant_docs(query: str):
    return retrieve_relevant_docs(query)

@track
def traced_answer_user_query(user_query: str):
    return answer_user_query(user_query)

@track
def rag_pipeline(query: str):
    ctx = traced_retrieve_relevant_docs(query)
    ans = traced_answer_user_query(query)
    return ans, ctx

def evaluation_task(dataset_item: dict) -> dict:
    ans, ctx = rag_pipeline(dataset_item["Query"])
    return {
        "input": dataset_item["Query"],
        "output": ans,
        "context": ctx
    }

# Load dataset
DATASET_PATH = "evaluation/Changi_Airport_Dataset - Sheet1.csv"
df = pd.read_csv(DATASET_PATH)
client = Opik()
dataset = client.get_or_create_dataset(
    name="Production RAG Evaluation Dataset",
    description="Dataset for evaluating RAG pipeline performance with Groq",
)
dataset.insert_from_pandas(df)


gemini_eval_model = LiteLLMChatModel(model_name="gemini/gemini-1.5-flash-latest")

scoring_metrics = [
    Hallucination(model=gemini_eval_model),
    AnswerRelevance(model=gemini_eval_model),
]

if __name__ == "__main__":
    evaluate(
        dataset=dataset,
        task=evaluation_task,
        scoring_metrics=scoring_metrics,
        project_name=OPIK_PROJECT_NAME,
        experiment_config={
            "retriever_version": "v1.0",
            "generator_model": "groq/llama3-8b-8192", 
            "evaluation_purpose": "Production RAG pipeline evaluation",
            "evaluation_llm": "gemini/gemini-1.5-flash-latest" 
        },
        verbose=1,
        task_threads=1
    )
