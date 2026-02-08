# Customer FAQ Assistant (Mockridge Bank)

[![CI](https://github.com/CameronDetig/spec-driven-development/actions/workflows/ci.yml/badge.svg?branch=feature/customer-faq-assistant-cameron-d)](https://github.com/CameronDetig/spec-driven-development/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)

Spec-driven local RAG assistant built with FastAPI + Streamlit.

## What It Does
- Answers customer questions relating to products and services for a fictional bank (Mockridge Bank) 
- Available through API or Streamlit UI
- Retrieves relevant local FAQ documents from ChromaDB
- Generates answers with:
  - `mock` deterministic mode (default, test-friendly)
  - `flan-t5` optional mode (small locally running instruction-tuned LLM, no API key required)
- Returns answer + cited sources

## Tech Stack
- Python 3.10, 3.11, or 3.12
- FastAPI
- Streamlit
- ChromaDB
- LangChain (`langchain`, `langchain-huggingface`, `langchain-chroma`)
- pytest

## Preview

<img src="images/streamlit_ui.png" alt="Streamlit UI" width="600">

## Quick Start

### 1) Setup
```bash
python run.py setup
```

What setup does:
- creates/uses `.venv` (unless `--no-venv`)
- installs dependencies
- builds retrieval DB

If you want to be able to use the LLM option, run setup with this command. It will download the flan-t5 model (~300MB):
```bash
python run.py setup --with-llm
```

### 2) Run Full Stack
```bash
python run.py fullstack
```

Endpoints:
- API: `http://127.0.0.1:8000`
- UI: `http://127.0.0.1:8501`

### API Documentation
When the API is running, interactive documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Run Commands

```bash
python run.py help
python run.py api
python run.py ui
python run.py fullstack
python run.py test
python run.py test-matrix
```

`test-matrix` runs tox environments for available interpreters (`py310`, `py311`, `py312`).

## Testing

Single environment:
```bash
python run.py test
```

Multi-python matrix:
```bash
python run.py test-matrix
```

Direct:
```bash
python -m pytest -q
tox
```

## CI (GitHub Actions)

Workflow: `.github/workflows/ci.yml`

Triggers:
- push to:
  - `main`
  - `feature/customer-faq-assistant-cameron-d`
- pull_request to:
  - `main`
  - `feature/customer-faq-assistant-cameron-d`
- manual (`workflow_dispatch`)

CI job:
- Python matrix: 3.10 / 3.11 / 3.12
- installs `requirements.txt`
- runs `pytest -q`

## API Overview

- `GET /health`
- `GET /db/status`
- `POST /db/build`
- `POST /ask`

Example request:
```json
{
  "question": "What can I do with the mobile app?",
  "top_k": 3,
  "generator": "mock"
}
```

## Environment Variables

- `RAG_MIN_SCORE` (minimum similarity score for retrieved documents. default: `0.25`)
- `API_URL` (used by Streamlit UI; default `http://127.0.0.1:8000`)

## Project Structure

- `app/main.py` API routes
- `app/retrieval.py` RAG retrieval/indexing logic
- `app/generation.py` generator selection and LLM adapter
- `app/rag_chain.py` LangChain prompt/chain
- `ui/streamlit_app.py` UI
- `SPECS/` authoritative feature specs
- `tests/` test suite
- `run.py` project entrypoint

## Notes
- Default mode is deterministic and intended for local testing/CI.
- Optional `flan-t5` mode uses Google's Flan-T5-small (80M params) for local experimentation and requires model assets (~308MB download via `python run.py setup --with-llm`).
- Project uses CPU-only PyTorch for faster setup and smaller footprint (~200MB vs ~2.5GB). GPU acceleration is unnecessary for the small models used in this project.