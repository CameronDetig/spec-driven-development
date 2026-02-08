# Feature Spec: Optional DistilGPT2 Generation

## Goal
- Enable an optional local LLM generation mode for runtime experimentation without affecting baseline determinism or test portability.

## Scope
- In:
    - Support `RAG_GENERATOR=distilgpt2`.
    - Implement a separate generator path backed by Hugging Face `transformers`.
    - Document runtime behavior and first-run model download expectations.
- Out:
    - CI dependency on LLM mode.
    - Any requirement for LLM mode during tests.

## Requirements
- LLM mode MUST be opt-in via environment variable:
    - `RAG_GENERATOR=distilgpt2`
- Default mode MUST remain `mock`.
- LLM mode MUST NOT be required to start or test default application workflow.
- If LLM mode is selected and model assets are unavailable:
    - System MUST fail clearly with actionable local setup guidance.
- LLM mode MUST NOT require secrets or API keys.
- Repository MUST NOT commit model weight files.
- Documentation MUST clearly state:
    - LLM mode is optional.
    - First-run download size/cost is local disk/network only.
    - Tests run without LLM mode.

## Related Specifications
- `generation-mock.md` - Default deterministic generator (required for tests)
- `retrieval-pipeline.md` - Provides source documents for LLM context

## Acceptance Criteria
- [x] With default environment, app uses mock generator. (test_generator_config.py::test_default_generator_mode_is_mock_deterministic)
- [x] With `RAG_GENERATOR=distilgpt2`, app routes generation through LLM adapter. (test_generator_config.py::test_distilgpt2_mode_is_opt_in_and_fails_clearly_when_unavailable)
- [x] Test suite does not depend on `distilgpt2`. (conftest.py::default_generator_env)
- [ ] Documentation explains optional setup and non-requirement for tests.
