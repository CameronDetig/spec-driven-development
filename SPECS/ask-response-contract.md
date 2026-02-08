# Feature Spec: Ask Response Contract

## Goal
- Guarantee a stable JSON response contract from `POST /ask` across success and fallback paths.

## Scope
- In:
    - Response schema for status `200`.
    - Source object field contract.
    - Retrieval metadata contract.
- Out:
    - HTTP error schema details outside `POST /ask` success response.

## Requirements
- `POST /ask` successful response MUST include keys:
    - `answer`
    - `sources`
    - `retrieval`
- `answer` MUST be a non-empty string.
- `sources` MUST be an array (possibly empty).
- Each `sources` item MUST include:
    - `id` (non-empty string)
    - `title` (non-empty string)
    - `snippet` (non-empty string)
    - `score` (number)
- `retrieval` MUST include:
    - `top_k` (integer)
    - `matched` (integer)
- Contract MUST remain stable for:
    - Matched retrieval response.
    - Fallback response (no sources).
- In fallback response:
    - `sources` MUST equal `[]`.
    - `retrieval.matched` MUST equal `0`.

## Related Specifications
- `ask-endpoint-validation.md` - Defines request validation before response generation
- `retrieval-pipeline.md` - Provides source data for response
- `generation-mock.md` - Generates answer content for response

## Acceptance Criteria
- [x] Contract test validates required top-level keys exist on every 200 response. (test_contract.py::test_ask_response_contract_contains_required_top_level_keys)
- [x] Contract test validates source item field presence and scalar types. (test_contract.py::test_ask_response_sources_have_required_fields_when_present)
- [x] Contract test validates `answer`, `id`, `title`, and `snippet` are non-empty strings. (test_contract.py::test_ask_response_sources_have_required_fields_when_present)
- [x] Fallback path preserves full schema and uses empty `sources`. (test_contract.py::test_ask_fallback_keeps_stable_schema)
- [x] Retrieval metadata fields are always present and consistent with payload. (test_contract.py::test_ask_response_retrieval_metadata_has_required_fields)
