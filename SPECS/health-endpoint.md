# Feature Spec: Health Endpoint

## Goal
- Provide a stable service-health signal for local development, CI checks, and smoke tests.

## Scope
- In:
    - Implement `GET /health`.
    - Return a deterministic JSON body and HTTP 200.
- Out:
    - Metrics, dependency health checks, authentication, and readiness/liveness split.

## Requirements
- `GET /health` MUST return HTTP 200.
- Response body MUST be exactly:
    - `{ "status": "ok" }`
- Response content type MUST be JSON.
- Endpoint behavior MUST be deterministic and independent of retrieval/generation subsystems.

## Related Specifications
- None - Health endpoint is independent of other features

## Acceptance Criteria
- [x] Calling `GET /health` returns status code `200`. (test_health.py::test_health_returns_ok)
- [x] Response JSON includes key `status` with value `ok`. (test_health.py::test_health_returns_ok)
- [x] No API keys, external services, or model downloads are required. (test_health.py::test_health_returns_ok)
