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
- LLM mode MUST be opt-in via:
- `RAG_GENERATOR=distilgpt2`
- Default mode MUST remain `mock`.
- LLM mode MUST not be required to start or test default application workflow.
- If LLM mode is selected and model assets are unavailable:
- System MUST fail clearly with actionable local setup guidance.
- No secrets or API keys may be required for LLM mode.
- Repository MUST NOT commit model weight files.
- README MUST clearly state:
- LLM mode is optional.
- First-run download size/cost is local disk/network only.
- Tests run without LLM mode.

## Acceptance Criteria
- [ ] With default environment, app uses mock generator.
- [ ] With `RAG_GENERATOR=distilgpt2`, app routes generation through LLM adapter.
- [ ] Test suite does not depend on `distilgpt2`.
- [ ] Documentation explains optional setup and non-requirement for tests.

