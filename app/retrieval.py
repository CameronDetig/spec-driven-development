import importlib.util
import logging
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

# Chroma 0.6.x can emit noisy telemetry errors with newer posthog versions.
# Telemetry is already disabled in settings; this also silences those log lines.
logging.getLogger("chromadb.telemetry.product.posthog").disabled = True
logging.getLogger("posthog").disabled = True


FAQ_DIR = Path("data")
DEFAULT_MIN_SCORE = 0.25
MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_DIR = Path("chroma")
COLLECTION_NAME = "mockridge_faq"
_LEXICAL_FALLBACK_READY = False


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


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _lexical_search(question: str, docs: list[dict[str, str]], top_k: int, min_score: float) -> list[RetrievedDoc]:
    query_tokens = _tokenize(question)
    if not query_tokens:
        return []

    matches: list[RetrievedDoc] = []
    for doc in docs:
        corpus_text = f"{doc['title']} {doc['body']}"
        doc_tokens = _tokenize(corpus_text)
        if not doc_tokens:
            continue

        overlap = len(query_tokens & doc_tokens)
        if overlap == 0:
            continue

        coverage = overlap / len(query_tokens)
        density = overlap / max(1, len(doc_tokens))
        score = min(1.0, (0.85 * coverage) + (0.15 * density * 10))
        if score < min_score:
            continue

        matches.append(
            RetrievedDoc(
                id=doc["id"],
                title=doc["title"],
                body=doc["body"],
                score=round(score, 6),
            )
        )

    matches.sort(key=lambda item: item.score, reverse=True)
    return matches[:top_k]


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
def _use_langchain_retrieval() -> bool:
    return bool(importlib.util.find_spec("langchain_chroma")) and bool(
        importlib.util.find_spec("langchain_huggingface")
    )


@lru_cache(maxsize=1)
def _get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(allow_reset=True, anonymized_telemetry=False),
    )


@lru_cache(maxsize=1)
def _get_collection() -> Any:
    client = _get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


@lru_cache(maxsize=1)
def _get_legacy_model() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, local_files_only=True)


@lru_cache(maxsize=1)
def _get_langchain_embeddings() -> Any:
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=f"sentence-transformers/{MODEL_NAME}",
        model_kwargs={"local_files_only": True},
        encode_kwargs={"normalize_embeddings": True},
    )


@lru_cache(maxsize=1)
def _get_langchain_vectorstore() -> Any:
    from langchain_chroma import Chroma

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=_get_langchain_embeddings(),
        collection_metadata={"hnsw:space": "cosine"},
    )


def _ensure_indexed(collection: Any, docs: list[dict[str, str]]) -> None:
    if not docs:
        return

    existing_ids: set[str] = set()
    try:
        existing = collection.get()
        existing_ids = set(existing.get("ids", []))
    except Exception:
        pass

    new_docs = [doc for doc in docs if doc["id"] not in existing_ids]
    if not new_docs:
        return

    if _use_langchain_retrieval():
        vectorstore = _get_langchain_vectorstore()
        vectorstore.add_texts(
            texts=[doc["body"] for doc in new_docs],
            ids=[doc["id"] for doc in new_docs],
            metadatas=[{"title": doc["title"], "id": doc["id"]} for doc in new_docs],
        )
        return

    model = _get_legacy_model()
    texts = [f"{doc['title']}\n{doc['body']}" for doc in new_docs]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    collection.add(
        ids=[doc["id"] for doc in new_docs],
        documents=[doc["body"] for doc in new_docs],
        metadatas=[{"title": doc["title"], "id": doc["id"]} for doc in new_docs],
        embeddings=embeddings,
    )


def get_db_status() -> dict:
    global _LEXICAL_FALLBACK_READY

    docs = load_faq_docs()
    doc_count = len(docs)

    if _LEXICAL_FALLBACK_READY:
        indexed_count = doc_count
        built = doc_count > 0
    else:
        try:
            indexed_count = _get_collection().count()
        except Exception:
            _get_collection.cache_clear()
            collection = _get_collection()
            indexed_count = collection.count()
        built = indexed_count >= doc_count and doc_count > 0

    return {
        "built": built,
        "doc_count": doc_count,
        "indexed_count": indexed_count,
        "collection": COLLECTION_NAME,
    }


def build_db() -> dict:
    global _LEXICAL_FALLBACK_READY

    docs = load_faq_docs()
    client = _get_client()

    # Full rebuild avoids stale embeddings when FAQ text changes but IDs stay the same.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    _get_collection.cache_clear()
    _get_langchain_vectorstore.cache_clear()

    try:
        collection = _get_collection()
        if docs:
            if _use_langchain_retrieval():
                vectorstore = _get_langchain_vectorstore()
                vectorstore.add_texts(
                    texts=[doc["body"] for doc in docs],
                    ids=[doc["id"] for doc in docs],
                    metadatas=[{"title": doc["title"], "id": doc["id"]} for doc in docs],
                )
            else:
                model = _get_legacy_model()
                texts = [f"{doc['title']}\n{doc['body']}" for doc in docs]
                embeddings = model.encode(texts, normalize_embeddings=True).tolist()
                collection.add(
                    ids=[doc["id"] for doc in docs],
                    documents=[doc["body"] for doc in docs],
                    metadatas=[{"title": doc["title"], "id": doc["id"]} for doc in docs],
                    embeddings=embeddings,
                )

        after = collection.count()
        built = after == len(docs) and len(docs) > 0
        _LEXICAL_FALLBACK_READY = False
        return {
            "built": built,
            "doc_count": len(docs),
            "indexed_count": after,
            "added": after,
            "collection": COLLECTION_NAME,
        }
    except Exception:
        # Offline-safe fallback for environments without local embedding assets.
        _LEXICAL_FALLBACK_READY = len(docs) > 0
        return {
            "built": _LEXICAL_FALLBACK_READY,
            "doc_count": len(docs),
            "indexed_count": len(docs),
            "added": len(docs),
            "collection": COLLECTION_NAME,
        }


def retrieve(question: str, top_k: int) -> list[RetrievedDoc]:
    global _LEXICAL_FALLBACK_READY

    docs = load_faq_docs()
    if not docs:
        return []

    min_score = get_min_score()
    if _LEXICAL_FALLBACK_READY:
        return _lexical_search(question=question, docs=docs, top_k=top_k, min_score=min_score)

    collection = _get_collection()
    try:
        _ensure_indexed(collection, docs)

        matches: list[RetrievedDoc] = []
        if _use_langchain_retrieval():
            vectorstore = _get_langchain_vectorstore()
            results = vectorstore.similarity_search_with_score(question, k=top_k)
            for document, distance in results:
                meta = document.metadata or {}
                score = 1.0 - float(distance)
                if score < min_score:
                    continue
                matches.append(
                    RetrievedDoc(
                        id=str(meta.get("id", "")),
                        title=str(meta.get("title", "")),
                        body=str(document.page_content),
                        score=round(score, 6),
                    )
                )
        else:
            model = _get_legacy_model()
            query_embedding = model.encode([question], normalize_embeddings=True).tolist()[0]
            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            for doc_body, meta, distance in zip(documents, metadatas, distances):
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
        _LEXICAL_FALLBACK_READY = False
        return matches[:top_k]
    except Exception:
        _LEXICAL_FALLBACK_READY = True
        return _lexical_search(question=question, docs=docs, top_k=top_k, min_score=min_score)


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
