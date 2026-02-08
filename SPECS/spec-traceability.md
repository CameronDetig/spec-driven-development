# Feature Spec: Spec Traceability Matrix

## Goal
- Provide explicit traceability between specifications, tests, and implementation modules.

## Scope
- In:
    - Mapping of each spec to planned test files.
    - Mapping of each spec to planned application modules.
- Out:
    - Detailed test-case code.
    - Release management process.

## Requirements
- Every feature spec in `SPECS/` MUST map to at least one test file.
- Every feature spec in `SPECS/` MUST map to at least one implementation module.
- Traceability document MUST be updated when adding/changing feature specs.

## Acceptance Criteria
- [x] Matrix includes each current spec file in `SPECS/`.
- [x] Matrix lists at least one test target per spec.
- [x] Matrix lists at least one implementation target per spec.

## Mapping
- `SPECS/health-endpoint.md`
    - Tests: `tests/test_health.py`
    - Implementation: `app/main.py`
- `SPECS/ask-endpoint-validation.md`
    - Tests: `tests/test_validation.py`
    - Implementation: `app/models.py`, `app/main.py`
- `SPECS/retrieval-pipeline.md`
    - Tests: `tests/test_retrieval.py`
    - Implementation: `app/retrieval.py`
- `SPECS/generation-mock.md`
    - Tests: `tests/test_determinism.py`, `tests/test_retrieval.py`, `tests/test_contract.py`
    - Implementation: `app/generation.py`
- `SPECS/generation-optional-llm.md`
    - Tests: `tests/test_generator_config.py` (optional/non-blocking), existing suite in mock mode
    - Implementation: `app/generation.py`, `app/main.py`
- `SPECS/ask-response-contract.md`
    - Tests: `tests/test_contract.py`
    - Implementation: `app/models.py`, `app/main.py`
- `SPECS/faq-data.md`
    - Tests: `tests/test_data_loader.py`, `tests/test_retrieval.py`
    - Implementation: `app/retrieval.py`, `data/faq/*`
- `SPECS/streamlit-ui.md`
    - Tests: `tests/test_streamlit_smoke.py` (optional smoke), manual acceptance checks
    - Implementation: `ui/streamlit_app.py`
- `SPECS/entrypoint-cli.md`
    - Tests: `tests/test_cli.py`, manual acceptance checks
    - Implementation: `run.py`
