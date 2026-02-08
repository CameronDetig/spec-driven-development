# Project Constitution — Customer FAQ Assistant (Mockridge Bank)

## 1) Purpose and Scope
This constitution defines the engineering intent for this repository.
It is the decision baseline for humans and AI contributors.

Source of truth order:
1. `SPECS/` (feature behavior and acceptance criteria)
2. `tests/` (executable verification)
3. `constitution.md` (engineering principles and quality gates)
4. implementation code

If implementation changes behavior, specs/tests must be updated in the same change set.

## 2) Product and Runtime Constraints
- Local-first system. No paid APIs or secrets required for default workflows.
- Python support range for project setup/runtime: `>=3.10`, `<3.13` (3.10/3.11/3.12).
- Default test workflow must run without network dependency on external hosted services.
- Optional LLM mode is allowed but must remain opt-in and non-blocking for tests.

## 3) Core Architectural Intent

### 3.1 Simplicity Over Cleverness
- Prefer direct, readable code paths over abstraction layers.
- Introduce abstraction only when at least two concrete use cases require it.
- Minimize hidden behavior and magic configuration.

### 3.2 Modularity and Boundaries
- API layer (`app/main.py`) handles HTTP contracts and validation flow.
- Retrieval layer (`app/retrieval.py`) owns indexing/query logic and score filtering.
- Generation layer (`app/generation.py`, `app/rag_chain.py`) owns answer production.
- UI layer (`ui/streamlit_app.py`) owns presentation and user interaction only.
- Do not mix UI concerns into API/retrieval/generation modules.

### 3.3 Determinism by Default
- Default generation mode must remain deterministic (`mock`).
- Retrieval must be deterministic for identical corpus and inputs.
- Optional stochastic behavior must be explicitly opt-in.

### 3.4 Observability and Operability
- Every major workflow must be runnable from `run.py`.
- Required commands include setup, test, and matrix testing:
  - `python run.py setup`
  - `python run.py test`
  - `python run.py test-matrix`
- Runtime errors must be actionable and user-readable.

## 4) Dependency and Integration Policy
- Prefer stable, mainstream libraries with clear maintenance.
- LangChain integration is allowed for orchestration; local Chroma remains required for persistence.
- New dependencies must have a clear justification in PR description.
- Avoid adding dependencies for trivial utility behavior.
- Tooling dependencies (e.g., `tox`, `nox`) are development concerns and should not be required for production runtime.

## 5) Testing and Quality Standards

### 5.1 Test Expectations
- Any behavior change must include or update tests.
- API contract fields and error semantics are backward-compatible unless a spec explicitly changes.
- New features should include at least one integration-path verification.

### 5.2 Quality Gates
- Must pass before merge:
  - `python -m pytest -q` (or `python run.py test`)
  - `python run.py test-matrix` for available local interpreters
- For behavior-affecting changes:
  - relevant spec files in `SPECS/` updated
  - traceability preserved (spec -> tests -> implementation)

### 5.3 Error Handling
- Fail clearly with actionable messages.
- Avoid silent fallthroughs that hide failures.
- Keep fallback behavior explicit and deterministic when used.

## 6) Naming and Code Conventions
- Use clear, domain-oriented names (`retrieve`, `build_db`, `get_db_status`).
- Avoid ambiguous abbreviations in public interfaces.
- Keep module responsibilities single-purpose and explicit.

## 7) Change Management (Living Document)
- This file is version-controlled and must evolve with architectural decisions.
- Update this constitution when:
  - supported Python range changes
  - core architectural boundaries shift
  - quality gates or required tooling change
- Constitution updates should explain intent, not low-level implementation detail.

## 8) Collaboration Model
- Architecture decisions should be reviewable in writing (PR description/spec updates).
- Major direction changes should be agreed by project stakeholders (engineering + product owner).
- Do not rely on private chat context as the only rationale for repository-wide decisions.

## 9) Validation Checklists

### 9.1 Before Implementation
- [ ] Relevant spec exists or is updated
- [ ] Module boundary for change is clear
- [ ] Dependency impact is understood

### 9.2 Before Merge
- [ ] Tests pass locally (`pytest`)
- [ ] Matrix check run (`test-matrix`) for available interpreters
- [ ] Specs updated for behavior changes
- [ ] Error messages are actionable
- [ ] No secrets or external paid API requirements introduced

### 9.3 After Merge (if applicable)
- [ ] Follow-up docs updated (`constitution.md`, `SPECS/`, project brief files)
- [ ] Any deferred risks tracked explicitly
