import json
import re
from pathlib import Path

import pytest


FAQ_DIR = Path("data")


def _extract_markdown_fields(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    id_match = re.search(r"(?im)^\s*id:\s*(.+)\s*$", text)
    title_match = re.search(r"(?im)^\s*title:\s*(.+)\s*$", text)
    doc_id = id_match.group(1).strip() if id_match else ""
    title = title_match.group(1).strip() if title_match else ""
    body = text
    return {"id": doc_id, "title": title, "body": body}


def _extract_json_fields(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "id": str(payload.get("id", "")).strip(),
        "title": str(payload.get("title", "")).strip(),
        "body": str(payload.get("body", "")).strip(),
    }


def _load_docs():
    files = list(FAQ_DIR.glob("*.md")) + list(FAQ_DIR.glob("*.json"))
    docs = []
    for file_path in files:
        if file_path.suffix == ".md":
            docs.append(_extract_markdown_fields(file_path))
        else:
            docs.append(_extract_json_fields(file_path))
    return docs


@pytest.mark.unit
def test_faq_directory_exists():
    """
    Verify that the FAQ corpus directory exists at data/.
    
    Spec: faq-data.md
    Requirement: "Corpus MUST be local and committed to repository"
    """
    assert FAQ_DIR.exists(), "Expected FAQ directory at data"
    assert FAQ_DIR.is_dir()


@pytest.mark.unit
@pytest.mark.requires_data
def test_faq_corpus_size_within_expected_range():
    """
    Verify that FAQ corpus contains between 8 and 15 documents.
    
    Spec: faq-data.md
    Requirement: "Corpus MUST contain between 8 and 15 documents"
    Acceptance Criteria: "Corpus size is within defined range (8-15)"
    """
    docs = _load_docs()
    assert 8 <= len(docs) <= 15


@pytest.mark.unit
@pytest.mark.requires_data
def test_faq_docs_have_required_fields_and_non_empty_values():
    """
    Verify that all FAQ documents have required fields (id, title, body) with non-empty values.
    
    Spec: faq-data.md
    Requirement: "Each document MUST include: `id`, `title`, `body`"
    Acceptance Criteria: "Data loader can parse all corpus files without runtime errors"
    """
    docs = _load_docs()
    assert docs, "No FAQ docs found in data"

    for doc in docs:
        assert set(doc.keys()) == {"id", "title", "body"}
        assert isinstance(doc["id"], str) and doc["id"] != ""
        assert isinstance(doc["title"], str) and doc["title"] != ""
        assert isinstance(doc["body"], str) and doc["body"] != ""


@pytest.mark.unit
@pytest.mark.requires_data
def test_faq_document_ids_are_unique():
    """
    Verify that all FAQ document IDs are unique across the corpus.
    
    Spec: faq-data.md
    Requirement: "IDs MUST be unique across corpus"
    Acceptance Criteria: "Document IDs are unique and non-empty"
    """
    docs = _load_docs()
    ids = [doc["id"] for doc in docs]
    assert len(ids) == len(set(ids))
