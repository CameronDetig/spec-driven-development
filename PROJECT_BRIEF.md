# Project Brief — Customer FAQ Assistant (Mockridge Bank)

## Purpose of This File

This document is a concise onboarding brief for code generation tools.
It orients a new tool to the project goals, constraints, specs, tests, and
implementation order without replacing the authoritative specs.

Source-of-truth hierarchy:
- Specs in `SPECS/` define behavior and acceptance criteria.
- Tests in `tests/` encode those specs.
- Implementation exists to satisfy the tests.

Note: Per project rules, do not use `README.md` as context for the LLM/tool.

---

## Project Overview

Build a spec-driven, testable RAG-style Customer FAQ Assistant
for a fictional bank named "Mockridge Bank".

The system:
- Accepts customer questions about bank products and services.
- Retrieves relevant FAQ documents using vector similarity search.
- Generates an answer based on retrieved documents.
- Returns the answer with cited sources.
- Runs locally without API keys or secrets.
- Needs to work consistently across platforms (Windows, Mac, Linux)

Primary goals:
- Demonstrate AI system testing and spec-driven development.
- Provide deterministic, CI-friendly behavior.
- Cleanly separate retrieval and generation.

Non-goal:
- High-quality or creative LLM output. (This requires API keys or large model downloads, which we want to avoid)

---

## Core Principles

- Specs define behavior, tests enforce it, code satisfies tests.
- Determinism is required by default.
- AI components must be testable and mockable.
- Reviewer setup friction must be minimal.

---

## Key Constraints

- No paid APIs and no API keys required for tests.
- No model weights committed to the repository.
- No GPU required.
- No external network calls during tests.
- `pytest` must run successfully by default.
- Optional LLM usage must be clearly documented and opt-in.

---

## Tech Stack

- Language: Python 3.10+
- API: FastAPI
- Vector store: ChromaDB (local, persisted)
- Embeddings: `all-MiniLM-L6-v2` via SentenceTransformers
- Optional LLM: `distilgpt2` via Hugging Face `transformers`
- UI: Streamlit (single-page)
- Tests: pytest

---

## Functional Requirements (High-Level)

The API exposes endpoints for question answering and health checks. Detailed
request/response shapes, validation rules, and error cases are defined in `SPECS/`
and enforced by `tests/`.

---

## Data Requirements

Local FAQ corpus for Mockridge Bank:
- Location: `data/`
- Format: Markdown or JSON
- Size: 8–15 documents
- Each document must include `id`, `title`, `body`
- Markdown files must explicitly include:
  - `id: <value>`
  - `title: <value>`

Example topics:
- checking accounts
- savings accounts
- auto loans
- credit cards
- overdraft fees
- fraud/disputes
- mobile app
- support hours

---

## RAG Pipeline (Logical Flow)

1. Validate request.
2. Embed the question.
3. Retrieve relevant documents from the local vector store.
4. Apply a relevance threshold and return a fallback response if no matches.
5. Generate an answer from retrieved content.
6. Return answer plus cited sources and metadata.

---

## Generation Strategy

Default generator (used in tests):
- Deterministic mock/extractive generator.
- Builds answers from retrieved text.
- No model downloads or external calls.

Optional generator (runtime only):
- `distilgpt2` via `transformers`.
- Selected per request (UI dropdown or `generator=distilgpt2`).
- Model assets are installed via `python run.py setup --with-llm`.
- Must not be required for tests.
- If unavailable, fail clearly with actionable guidance.

---

## Testing Requirements

All tests use pytest and run without network, API keys, or LLM downloads.
Coverage is defined by the specs in `SPECS/` and implemented in `tests/`.

---

## Project Structure

- `app/main.py` FastAPI app and routes
- `app/models.py` Pydantic schemas
- `app/retrieval.py` ChromaDB + embeddings
- `app/generation.py` mock + optional LLM generator
- `run.py` cross-platform entry point for setup, run, and test commands
- `data/*` local FAQ corpus
- `ui/streamlit_app.py` single-page Streamlit UI
- `tests/` pytest suite
- `pytest.ini` test configuration
- `SPECS/` authoritative feature specs

---

## Environment Variables

Optional only. Defaults are applied when unset. Reviewers should not need to set any values.
An example file is provided at `.env.example`.

- `RAG_MIN_SCORE=0.25` (default relevance threshold)
- `API_URL` (optional override for Streamlit to reach API)

---

## Explicit Non-Goals

- High-quality natural language generation
- Authentication or authorization
- External APIs
- GPU acceleration
- Production scaling or deployment

---

## Implementation Order (Spec-Driven)

1. Create file structure.
2. Implement Pydantic models and validation.
3. Implement API routes based on specs.
4. Implement data loader and retrieval pipeline.
5. Implement deterministic mock generator.
6. Add optional `distilgpt2` generator behind env flag.
7. Add Streamlit UI.
8. Keep tests green at every step.
