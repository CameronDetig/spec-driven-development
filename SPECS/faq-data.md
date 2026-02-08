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
    - `id`
    - `title`
    - `body`
- For markdown documents, required fields MUST be explicitly present as:
    - `id: <value>`
    - `title: <value>`
- Corpus MUST represent core Mockridge Bank topics, including:
    - checking accounts
    - savings accounts
    - auto loans
    - credit cards
    - overdraft fees
    - fraud/disputes
    - mobile app
    - support hours
- Document content MUST be stable and human-readable.
- Corpus format MAY be markdown or JSON, but parser behavior MUST be documented.
- IDs MUST be unique across corpus.
- Corpus MUST be local and committed to repository.
- Corpus MUST not include sensitive data, credentials, or personal information.

## Acceptance Criteria
- [ ] Data loader can parse all corpus files without runtime errors.
- [ ] Document IDs are unique and non-empty.
- [ ] At least one retrieval test depends on known corpus content and passes.
- [ ] Corpus size is within defined range (8-15).
