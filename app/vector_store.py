from typing import List
import hashlib
from pinecone import Pinecone, ServerlessSpec
from app.embeddings import embed_texts, get_gemini_embedding
from app.config import config
from langchain.schema import Document


pc = Pinecone(api_key=config.PINECONE_API_KEY)
EMBEDDING_DIM = 768


def init_pinecone_index() -> None:
    """
    Ensure the Pinecone index exists. If not, create it.
    """
    existing_indexes = [index.name for index in pc.list_indexes()]
    if config.PINECONE_INDEX not in existing_indexes:
        print(f"[Pinecone] Creating index: {config.PINECONE_INDEX}")
        pc.create_index(
            name=config.PINECONE_INDEX,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=config.PINECONE_ENV),
        )
    else:
        print(f"[Pinecone] Index '{config.PINECONE_INDEX}' already exists.")


def generate_id(text: str) -> str:
    """
    Create a deterministic hash ID from chunk text.
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def store_documents_in_pinecone(docs: List[Document], batch_size: int = 32) -> None:
    """
    Embed and upsert unique Document chunks into Pinecone.
    Skips chunks already uploaded using deterministic hashing.
    """
    index = pc.Index(config.PINECONE_INDEX)

    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    ids = [generate_id(text) for text in texts]

    # Query existing IDs to avoid duplicates
    existing_ids = set()
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        results = index.fetch(ids=batch_ids)
        existing_ids.update(results.vectors.keys())

    print(f"[Pinecone] Found {len(existing_ids)} duplicate chunks. Skipping them...")

    # Filter out already existing chunks
    filtered = [
        (id_, text, metadata)
        for id_, text, metadata in zip(ids, texts, metadatas)
        if id_ not in existing_ids
    ]

    if not filtered:
        print("[Pinecone] No new documents to upsert.")
        return

    # Embed only the filtered chunks
    new_texts = [text for (_, text, _) in filtered]
    new_ids = [id_ for (id_, _, _) in filtered]
    new_metadatas = [meta for (_, _, meta) in filtered]

    embeddings = embed_texts(new_texts)

    # Upsert in batches
    to_upsert = [
        (id_, vector, {"text": text, **(meta or {})})
        for id_, vector, text, meta in zip(new_ids, embeddings, new_texts, new_metadatas)
    ]

    for i in range(0, len(to_upsert), batch_size):
        batch = to_upsert[i:i+batch_size]
        index.upsert(vectors=batch)

    print(f"[Pinecone] ✅ Upserted {len(to_upsert)} new document chunks.")


def retrieve_relevant_docs(query: str, top_k: int = 5) -> List[str]:
    """
    Perform similarity search and return relevant document texts.
    """
    query_vector = get_gemini_embedding(query).tolist()
    pinecone_index = pc.Index(config.PINECONE_INDEX)

    results = pinecone_index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    matches = results.get("matches", [])

    return [
        match["metadata"]["text"]
        for match in matches
        if "metadata" in match and "text" in match["metadata"]
    ]
