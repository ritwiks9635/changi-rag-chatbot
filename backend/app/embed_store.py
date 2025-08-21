import os
import json
from typing import List
from langchain.schema import Document
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.utils.cleaner import clean_and_chunk
from app.vector_store import init_pinecone_index, store_documents_in_pinecone

SCRAPED_DATA_PATH = os.path.join("scrapers", "data", "scraped_pages.json")


def load_scraped_data(path: str) -> List[dict]:
    """
    Load JSON data from the specified path.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected a list of pages in scraped JSON.")
    return data


def prepare_documents(pages: List[dict]) -> List[Document]:
    """
    Clean and chunk HTML content into a list of LangChain Document objects.
    """
    documents = []

    for page in pages:
        url = page.get("url", "")
        raw_html = page.get("content", "")

        chunks = clean_and_chunk(raw_html)

        for chunk in chunks:
            doc = Document(
                page_content=chunk,
                metadata={"source": url}
            )
            documents.append(doc)

    return documents


def parallel_store_in_pinecone(documents: List[Document], batch_size: int = 200, max_workers: int = 4):
    """
    Store documents into Pinecone using parallel threads.
    """
    doc_batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(store_documents_in_pinecone, batch, batch_size) for batch in doc_batches]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"[ERROR] Failed to store batch: {e}")


def run_rag_pipeline():
    """
    Main RAG setup pipeline:
    - Loads web data
    - Cleans & chunks
    - Embeds
    - Stores in Pinecone (parallelized)
    """
    print("[RAG] Loading scraped data...")
    pages = load_scraped_data(SCRAPED_DATA_PATH)

    print(f"[RAG] Loaded {len(pages)} pages. Cleaning & chunking...")
    documents = prepare_documents(pages)

    print(f"[RAG] Prepared {len(documents)} text chunks. Initializing Pinecone...")
    init_pinecone_index()

    print(f"[RAG] Storing chunks into Pinecone in parallel...")
    parallel_store_in_pinecone(documents, batch_size=200, max_workers=4)

    print("[RAG] ✅ Pipeline completed successfully.")


if __name__ == "__main__":
    run_rag_pipeline()
