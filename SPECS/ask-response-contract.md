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
- `answer` MUST be a string.
- `sources` MUST be an array (possibly empty).
- Each `sources` item MUST include:
    - `id` (string)
    - `title` (string)
    - `snippet` (string)
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

## Acceptance Criteria
- [ ] Contract test validates required top-level keys exist on every 200 response.
- [ ] Contract test validates source item field presence and scalar types.
- [ ] Fallback path preserves full schema and uses empty `sources`.
- [ ] Retrieval metadata fields are always present and consistent with payload.
