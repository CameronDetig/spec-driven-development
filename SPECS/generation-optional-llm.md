# Feature Spec: Optional Flan-T5 Generation

## Goal
- Enable an optional local LLM generation mode for runtime experimentation without affecting baseline determinism or test portability.

## Scope
- In:
    - Support `generator=flan-t5` request option.
    - Implement a separate generator path backed by Hugging Face `transformers`, with LangChain pipeline integration when available.
    - Document runtime behavior and first-run model download expectations.
- Out:
    - CI dependency on LLM mode.
    - Any requirement for LLM mode during tests.

## Requirements
- LLM mode MUST be opt-in via request field:
    - `generator=flan-t5`
- Default mode MUST remain `mock`.
- LLM mode MUST NOT be required to start or test default application workflow.
- When LangChain Hugging Face integration is available, `flan-t5` mode SHOULD execute through the LangChain adapter path.
- If LLM mode is selected and model assets are unavailable:
    - System MUST fail clearly with actionable local setup guidance.
    - UI MUST instruct user to run `python run.py setup --with-llm`.
- LLM mode MUST NOT require secrets or API keys.
- Repository MUST NOT commit model weight files.
- Documentation MUST clearly state:
    - LLM mode is optional.
    - First-run download size/cost is local disk/network only.
    - Tests run without LLM mode.
    - How to install LLM assets via `python run.py setup --with-llm`.

## Related Specifications
- `generation-mock.md` - Default deterministic generator (required for tests)
- `retrieval-pipeline.md` - Provides source documents for LLM context

## Acceptance Criteria
- [x] With default environment, app uses mock generator. (test_generator_config.py::test_default_generator_mode_is_mock_deterministic)
- [x] With `generator=flan-t5`, app routes generation through LLM adapter. (test_generator_config.py::test_flan_t5_mode_is_opt_in_and_fails_clearly_when_unavailable)
- [x] Test suite does not depend on `flan-t5`. (conftest.py::default_generator_env)
- [ ] Documentation explains optional setup and non-requirement for tests.
