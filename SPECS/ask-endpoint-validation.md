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
- Validation failures MUST return HTTP 400.
- Validation failures include:
- Missing `question`.
- `question` length below 5.
- `question` length above 300.
- `top_k` below 1.
- `top_k` above 5.
- Error responses MUST be JSON and machine-parseable.
- Validation MUST run before retrieval or generation logic executes.

## Acceptance Criteria
- [ ] Missing `question` returns `400`.
- [ ] `question` shorter than 5 characters returns `400`.
- [ ] `question` longer than 300 characters returns `400`.
- [ ] `top_k = 0` returns `400`.
- [ ] `top_k > 5` returns `400`.
- [ ] Omitted `top_k` is accepted and treated as `3`.

