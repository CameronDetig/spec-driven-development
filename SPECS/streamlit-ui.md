# Feature Spec: Customer FAQ Assistant UI (Streamlit)

## Goal
- Provide a simple local UI to interact with the Customer FAQ Assistant for manual testing and demonstration.

## Scope
- In:
    - Single-page Streamlit application.
    - Question input and `top_k` control.
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
    - Scrollable chat-style message window.
    - Chat bubble layout with assistant messages left-aligned and user messages right-aligned.
    - Initial assistant welcome message on load.
    - Minimal DB status indicator showing only `built` and `doc_count` from `GET /db/status`.
    - Build DB action button that calls `POST /db/build`.
    - Question text input.
    - `top_k` control constrained to `1..5` with default `3`, displayed inline with generator selection.
    - Generator selector with `mock` (default) and `flan-t5` options, displayed inline with `top_k`.
    - Three clickable example query buttons below the message input.
    - `Clear Chat` button and `Submit` button positioned directly below message input.
    - `Clear Chat` button visible only after at least one user message exists.
    - Submit action to call API endpoint `POST /ask`.
    - On submit, UI MUST immediately append the user message to the chat window and clear the input before backend processing completes.
- On success (`200`), UI MUST display:
    - `answer`
    - `sources` list with `title`, `snippet`, and `score`
    - `retrieval.top_k` and `retrieval.matched`
- On fallback responses (`sources=[]`), UI MUST clearly indicate no matching sources were found.
- On API validation errors (`400`), UI MUST show clear, non-crashing feedback to user.
- If DB status is not built, question input and submit controls MUST be disabled until build succeeds.
- If `flan-t5` is selected and model assets are missing, UI MUST instruct the user to run `python run.py setup --with-llm`.
- UI MUST not require optional LLM mode; default mock mode must be fully supported.
- UI MUST not embed secrets or credentials in code.

## Related Specifications
- `ask-endpoint-validation.md` - Defines validation rules that UI must handle
- `ask-response-contract.md` - Defines response schema that UI must render
- `generation-mock.md` - Default generator that UI relies on

## Acceptance Criteria
- [ ] User can enter a valid question, submit, and view answer output. (manual acceptance)
- [ ] User can change `top_k` and see reflected retrieval metadata. (manual acceptance)
- [ ] User can switch generator between `mock` and `flan-t5` from the same control row as `top_k`. (manual acceptance)
- [ ] Source citations are rendered when present. (manual acceptance)
- [ ] Fallback path is visible and understandable when no matches exist. (manual acceptance)
- [ ] Validation errors are shown in the UI without app crash. (manual acceptance)
- [x] UI runs locally against the API in default mock mode. (test_streamlit_smoke.py::test_streamlit_app_module_imports)
- [x] DB status payload is normalized to `built` and `doc_count` for UI consumption. (tests/test_streamlit_ui_logic.py::test_get_db_status_normalizes_payload)
- [x] DB status helper surfaces HTTP failures without crashing the UI flow. (tests/test_streamlit_ui_logic.py::test_get_db_status_handles_non_200)
- [ ] UI is implemented as a single page. (manual acceptance)
- [ ] UI is accessible without authentication or account flows. (manual acceptance)
