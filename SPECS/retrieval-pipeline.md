# Feature Spec: Retrieval Pipeline

## Goal
- Retrieve the most relevant local FAQ documents for a customer question using embeddings and ChromaDB.

## Scope
- In:
    - Embed incoming question with `all-MiniLM-L6-v2`.
    - Query local persisted ChromaDB for top-k matches.
    - Return scored, sorted source candidates.
    - Apply minimum relevance threshold rule.
- Out:
    - Final answer wording strategy.
    - External document ingestion services.

## Requirements
- Retrieval MUST use local FAQ corpus data only.
- Retrieval MUST use local ChromaDB persistence (no remote vector DB).
- Query flow:
    - Embed question with `all-MiniLM-L6-v2` via SentenceTransformers.
    - Query ChromaDB using `top_k`.
    - Map results to source items with `id`, `title`, `snippet`, `score`.
- Sources MUST be sorted by descending relevance score.
- If no document satisfies relevance threshold:
    - Retrieval result MUST be treated as unmatched.
    - Downstream response MUST use fallback behavior.
- Relevance threshold MUST be configurable via environment variable:
    - `RAG_MIN_SCORE`
    - Default value: `0.25`
- Retrieval metadata MUST include:
    - `top_k` as the effective query size.
    - `matched` as number of documents included in `sources`.
- Retrieval behavior MUST be deterministic for the same corpus and input.

## Related Specifications
- `faq-data.md` - Defines corpus structure that retrieval depends on
- `ask-endpoint-validation.md` - Validates request before retrieval
- `generation-mock.md` - Consumes retrieval results to generate answers

## Acceptance Criteria
- [x] A known banking query retrieves an expected FAQ document as top result. (test_retrieval.py::test_known_query_returns_expected_top_document)
- [x] Changing `top_k` changes the maximum returned source count accordingly. (test_retrieval.py::test_top_k_controls_maximum_number_of_sources)
- [x] Source list is sorted by score descending. (test_retrieval.py::test_sources_are_sorted_by_descending_score)
- [x] Unknown/out-of-domain query triggers unmatched retrieval path. (test_retrieval.py::test_unknown_query_returns_fallback_with_empty_sources)
- [x] Retrieval metadata reports `top_k` and `matched` accurately. (test_contract.py::test_ask_response_retrieval_metadata_has_required_fields)
