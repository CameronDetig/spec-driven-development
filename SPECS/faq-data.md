# Feature Spec: FAQ Corpus Data

## Goal
- Define a small, local, version-controlled FAQ corpus that powers retrieval tests and API behavior.

## Scope
- In:
    - Local FAQ files under `data/faq/`.
    - Required document fields and minimum corpus breadth.
    - Deterministic, test-friendly content expectations.
- Out:
    - External content sources or dynamic ingestion pipelines.

## Requirements
- Corpus MUST contain between 8 and 15 documents.
- Corpus content MUST represent the fictitious institution name as `Mockridge Bank`.
- Each document MUST include:
    - `id` (unique identifier)
    - `title` (document title)
    - `body` (document content)
- For markdown documents, required fields MUST be explicitly present as:
    - `id: <value>`
    - `title: <value>`
- Corpus MUST represent core Mockridge Bank topics, including:
    - Checking accounts
    - Savings accounts
    - Auto loans
    - Credit cards
    - Overdraft fees
    - Fraud/disputes
    - Mobile app
    - Support hours
- Document content MUST be stable and human-readable.
- Corpus format MAY be markdown or JSON, but parser behavior MUST be documented.
- Document IDs MUST be unique across corpus.
- Corpus MUST be local and committed to repository.
- Corpus MUST NOT include sensitive data, credentials, or personal information.

## Related Specifications
- `retrieval-pipeline.md` - Consumes FAQ corpus for semantic search

## Acceptance Criteria
- [x] Data loader can parse all corpus files without runtime errors. (test_data_loader.py::test_faq_docs_have_required_fields_and_non_empty_values)
- [x] Document IDs are unique and non-empty. (test_data_loader.py::test_faq_document_ids_are_unique)
- [x] At least one retrieval test depends on known corpus content and passes. (test_retrieval.py::test_known_query_returns_expected_top_document)
- [x] Corpus size is within defined range (8-15). (test_data_loader.py::test_faq_corpus_size_within_expected_range)
