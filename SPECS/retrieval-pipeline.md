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

## Acceptance Criteria
- [ ] A known banking query retrieves an expected FAQ document as top result.
- [ ] Changing `top_k` changes the maximum returned source count accordingly.
- [ ] Source list is sorted by score descending.
- [ ] Unknown/out-of-domain query triggers unmatched retrieval path.
- [ ] Retrieval metadata reports `top_k` and `matched` accurately.
