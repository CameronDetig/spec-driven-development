import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings


FAQ_DIR = Path("data")
DEFAULT_MIN_SCORE = 0.25
MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_DIR = Path("chroma")
COLLECTION_NAME = "mockridge_faq"


@dataclass
class RetrievedDoc:
    id: str
    title: str
    body: str
    score: float


def _extract_field(text: str, field: str) -> str:
    match = re.search(rf"(?im)^\s*{re.escape(field)}:\s*(.+)\s*$", text)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_body(text: str) -> str:
    marker = "body: |"
    idx = text.find(marker)
    if idx == -1:
        return ""

    body_lines = text[idx + len(marker) :].splitlines()
    cleaned = []
    for line in body_lines:
        if line.startswith("  "):
            cleaned.append(line[2:])
        else:
            cleaned.append(line.lstrip())
    return "\n".join(cleaned).strip()


def _snippet(body: str, limit: int = 220) -> str:
    body = body.strip().replace("\n", " ")
    if len(body) <= limit:
        return body
    return body[: limit - 3].rstrip() + "..."


def load_faq_docs() -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    if not FAQ_DIR.exists():
        return docs

    for path in sorted(FAQ_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        doc_id = _extract_field(text, "id")
        title = _extract_field(text, "title")
        body = _extract_body(text)
        if doc_id and title and body:
            docs.append({"id": doc_id, "title": title, "body": body})

    return docs


def get_min_score() -> float:
    raw = os.getenv("RAG_MIN_SCORE", str(DEFAULT_MIN_SCORE))
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_MIN_SCORE


@lru_cache(maxsize=1)
def _get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(allow_reset=True, anonymized_telemetry=False),
    )


@lru_cache(maxsize=1)
def _get_collection() -> chromadb.Collection:
    client = _get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


@lru_cache(maxsize=1)
def _get_model() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def _ensure_indexed(collection: chromadb.Collection, docs: list[dict[str, str]], model: Any):
    if not docs:
        return

    existing_ids = set()
    try:
        existing = collection.get(include=["ids"])
        existing_ids = set(existing.get("ids", []))
    except Exception:
        existing_ids = set()

    new_docs = [doc for doc in docs if doc["id"] not in existing_ids]
    if not new_docs:
        return

    texts = [f"{doc['title']}\n{doc['body']}" for doc in new_docs]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    collection.add(
        ids=[doc["id"] for doc in new_docs],
        documents=[doc["body"] for doc in new_docs],
        metadatas=[{"title": doc["title"], "id": doc["id"]} for doc in new_docs],
        embeddings=embeddings,
    )


def get_db_status() -> dict:
    docs = load_faq_docs()
    collection = _get_collection()
    indexed_count = collection.count()
    doc_count = len(docs)
    built = indexed_count >= doc_count and doc_count > 0
    return {
        "built": built,
        "doc_count": doc_count,
        "indexed_count": indexed_count,
        "collection": COLLECTION_NAME,
    }


def build_db() -> dict:
    docs = load_faq_docs()
    client = _get_client()

    # Full rebuild avoids stale embeddings when FAQ text changes but IDs stay the same.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    _get_collection.cache_clear()
    collection = _get_collection()
    model = _get_model()
    texts = [f"{doc['title']}\n{doc['body']}" for doc in docs]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist() if docs else []

    if docs:
        collection.add(
            ids=[doc["id"] for doc in docs],
            documents=[doc["body"] for doc in docs],
            metadatas=[{"title": doc["title"], "id": doc["id"]} for doc in docs],
            embeddings=embeddings,
        )

    after = collection.count()
    built = after == len(docs) and len(docs) > 0
    return {
        "built": built,
        "doc_count": len(docs),
        "indexed_count": after,
        "added": after,
        "collection": COLLECTION_NAME,
    }


def retrieve(question: str, top_k: int) -> list[RetrievedDoc]:
    docs = load_faq_docs()
    if not docs:
        return []

    collection = _get_collection()
    model = _get_model()

    _ensure_indexed(collection, docs, model)

    query_embedding = model.encode([question], normalize_embeddings=True).tolist()[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    min_score = get_min_score()
    matches: list[RetrievedDoc] = []

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for doc_body, meta, distance in zip(documents, metadatas, distances):
        # Convert distance to similarity score (1 - distance) for cosine distance.
        score = 1.0 - float(distance)
        if score < min_score:
            continue
        matches.append(
            RetrievedDoc(
                id=str(meta.get("id", "")),
                title=str(meta.get("title", "")),
                body=str(doc_body),
                score=round(score, 6),
            )
        )

    matches.sort(key=lambda item: item.score, reverse=True)
    return matches[:top_k]


def to_source_payload(docs: list[RetrievedDoc]) -> list[dict]:
    payload = []
    for doc in docs:
        payload.append(
            {
                "id": doc.id,
                "title": doc.title,
                "snippet": _snippet(doc.body),
                "score": doc.score,
            }
        )
    return payload
