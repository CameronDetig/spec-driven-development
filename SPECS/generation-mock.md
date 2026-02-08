# Feature Spec: Deterministic Mock Generation

## Goal
- Provide a default answer generator that is deterministic, locally runnable, and independent of external model downloads.

## Scope
- In:
    - Implement a mock/extractive generator as the default generation path.
    - Build answer text from retrieved FAQ snippets.
    - Define fallback answer behavior for unmatched retrieval.
- Out:
    - Human-like conversational quality optimization.
    - Probabilistic/creative generation behavior.

## Requirements
- Default generator MUST be selected when `RAG_GENERATOR` is unset or set to `mock`.
- Generator MUST not require network access, API keys, or model downloads.
- For matched retrieval:
    - Answer MUST be constructed from retrieved content deterministically.
    - Same input and same retrieval set MUST produce identical output.
- For unmatched retrieval:
    - Return a safe fallback answer.
    - `sources` MUST be empty in API response.
- Generator interface MUST be cleanly swappable with optional LLM generator.

## Related Specifications
- `generation-optional-llm.md` - Alternative LLM-based generator (opt-in)
- `retrieval-pipeline.md` - Provides source documents for answer generation
- `ask-response-contract.md` - Defines answer field in response schema

## Acceptance Criteria
- [x] Tests run fully with `RAG_GENERATOR=mock` and no model downloads. (conftest.py::default_generator_env)
- [x] Repeated identical requests produce identical answers. (test_determinism.py::test_same_input_produces_same_output)
- [x] Matched retrieval path returns a non-empty answer derived from source content. (test_contract.py::test_ask_response_contract_contains_required_top_level_keys)
- [x] Unmatched retrieval path returns fallback answer and empty sources. (test_retrieval.py::test_unknown_query_returns_fallback_with_empty_sources)
