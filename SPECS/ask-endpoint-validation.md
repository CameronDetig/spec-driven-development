# Feature Spec: Ask Endpoint Validation

## Goal
- Enforce strict, predictable request validation for `POST /ask` so API behavior is safe and testable.

## Scope
- In:
    - Validate request body fields `question` and `top_k`.
    - Return consistent 400 errors for invalid input.
- Out:
    - Retrieval ranking behavior.
    - Answer generation quality.

## Requirements
- Endpoint:
    - `POST /ask`
- Request schema:
    - `question` is required string with length `5..300`.
    - `top_k` is optional integer with default `3` and valid range `1..5`.
    - `generator` is optional string with allowed values `mock` or `flan-t5`.
- Validation failures MUST return HTTP 400.
- Validation failures include:
    - Missing `question`.
    - `question` length below 5.
    - `question` length above 300.
    - `top_k` below 1.
    - `top_k` above 5.
    - `generator` not in allowed values.
- Error responses MUST be JSON and machine-parseable.
- Error responses MUST include a top-level `detail` field suitable for user-facing validation feedback.
- Validation MUST run before retrieval or generation logic executes.
- If DB is not built, endpoint MUST return `503` with actionable guidance to build DB first.

## Related Specifications
- `ask-response-contract.md` - Defines success response schema for valid requests
- `retrieval-pipeline.md` - Processes validated requests

## Acceptance Criteria
- [x] Missing `question` returns `400`. (test_validation.py::test_ask_missing_question_returns_400)
- [x] `question` shorter than 5 characters returns `400`. (test_validation.py::test_ask_question_too_short_returns_400)
- [x] `question` longer than 300 characters returns `400`. (test_validation.py::test_ask_question_too_long_returns_400)
- [x] `top_k = 0` returns `400`. (test_validation.py::test_ask_top_k_zero_returns_400)
- [x] `top_k > 5` returns `400`. (test_validation.py::test_ask_top_k_above_range_returns_400)
- [x] Omitted `top_k` is accepted and treated as `3`. (test_validation.py::test_ask_omitted_top_k_uses_default)
