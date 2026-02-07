# Feature Spec: Streamlit UI

## Goal
- Provide a simple local UI to interact with the RAG FAQ API for manual testing and demonstration.

## Scope
- In:
    - A single-page Streamlit application.
    - A Streamlit app with question input and `top_k` control.
    - Submit workflow that calls `POST /ask`.
    - Rendering of answer, sources, and retrieval metadata.
    - User-visible handling for API validation and runtime errors.
- Out:
    - Authentication and user accounts.
    - Multi-page navigation.
    - Advanced visual design or theming system.
    - Streaming token-by-token generation output.

## Requirements
- UI MUST run locally with Streamlit and no API keys.
- UI MUST be a single-page interface.
- UI MUST NOT implement authentication, authorization, or user accounts.
- UI MUST include:
    - Question text input.
    - `top_k` control constrained to `1..5` with default `3`.
    - Submit action to call API endpoint `POST /ask`.
- On success (`200`), UI MUST display:
    - `answer`
    - `sources` list with `title`, `snippet`, and `score`
    - `retrieval.top_k` and `retrieval.matched`
- On fallback responses (`sources=[]`), UI MUST clearly indicate no matching sources were found.
- On API validation errors (`400`), UI MUST show clear, non-crashing feedback to user.
- UI MUST not require optional LLM mode; default mock mode must be fully supported.
- UI MUST not embed secrets or credentials in code.

## Acceptance Criteria
- [ ] User can enter a valid question, submit, and view answer output.
- [ ] User can change `top_k` and see reflected retrieval metadata.
- [ ] Source citations are rendered when present.
- [ ] Fallback path is visible and understandable when no matches exist.
- [ ] Validation errors are shown in the UI without app crash.
- [ ] UI runs locally against the API in default mock mode.
- [ ] UI is implemented as a single page.
- [ ] UI is accessible without authentication or account flows.
