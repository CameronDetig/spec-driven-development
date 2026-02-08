# Feature Spec: Entrypoint CLI (run.py)

## Goal
- Provide a single cross-platform entry point for setup, running services, and tests.

## Scope
- In:
    - A `run.py` script that manages setup, API, UI, and test commands.
    - Cross-platform support for macOS, Linux, and Windows.
    - Clear help output with available commands.
- Out:
    - Full environment management beyond project dependencies.
    - Complex process supervision or daemonization.

## Requirements
- `run.py` MUST support these commands:
    - `setup`: Install dependencies.
    - `setup --with-llm`: Install dependencies and download LLM assets.
    - `api`: Run the FastAPI backend.
    - `ui`: Run the Streamlit UI.
    - `fullstack`: Run API and UI concurrently.
    - `test`: Run pytest.
    - `test-matrix`: Run tox-based multi-Python test matrix.
    - `help`: Show available commands and examples.
- `run.py` SHOULD support optional Docker helper commands:
    - `docker-build`: Build container images.
    - `docker-api`: Run API container.
    - `docker-fullstack`: Run API and UI containers together.
    - `docker-down`: Stop/remove running Docker Compose services.
- `run.py` MUST be cross-platform and use `sys.executable` for subprocess calls.
- `run.py` MUST default to creating and using a local `.venv` for setup.
- `run.py` MUST support a `--no-venv` option to install into the current environment instead.
- `run.py setup` MUST detect and prefer a supported Python interpreter for virtual environment creation.
- Supported interpreter range for full project setup MUST be:
    - `>=3.10`
    - `<3.13`
- `run.py setup` SHOULD prefer `3.12`, then `3.11`, then `3.10`, before fallback.
- `run.py setup` MUST support overriding interpreter selection via `--python <path-or-command>`.
- If no supported interpreter is found, `run.py setup` MUST fail with actionable guidance.
- `run.py setup` SHOULD support optional automated Python installation via `--install-python` and fail clearly if package-manager installation is unavailable.
- `fullstack` command MUST start API and UI on their default ports and shut down cleanly on Ctrl+C.
- Commands MUST print clear status messages and fail clearly with actionable errors.
- Docker helper commands MUST fail clearly when Docker is unavailable and MUST keep local non-Docker commands fully usable.

## Acceptance Criteria
- [ ] `python run.py help` prints usage and available commands. (test_cli.py - to be implemented)
- [ ] `python run.py setup` installs dependencies without requiring manual venv steps. (manual acceptance)
- [ ] `python run.py setup --with-llm` downloads LLM assets for distilgpt2. (manual acceptance)
- [ ] `python run.py setup --no-venv` installs dependencies into the current environment. (manual acceptance)
- [ ] `python run.py setup` automatically selects a supported interpreter (`3.12`/`3.11`/`3.10`) for `.venv` creation when available. (manual acceptance)
- [ ] `python run.py setup --python <interpreter>` uses the specified interpreter when supported. (manual acceptance)
- [ ] `python run.py setup` fails with clear guidance when no supported interpreter is available. (manual acceptance)
- [ ] `python run.py setup --install-python` attempts package-manager Python installation and then continues setup when possible. (manual acceptance)
- [ ] `python run.py api` starts the backend. (manual acceptance)
- [ ] `python run.py ui` starts the Streamlit UI. (manual acceptance)
- [ ] `python run.py fullstack` starts API and UI together and stops them on Ctrl+C. (manual acceptance)
- [ ] `python run.py test` runs pytest successfully. (test_cli.py - to be implemented)
- [ ] `python run.py test-matrix` runs tox matrix environments (for available local interpreters). (manual acceptance)
- [ ] `python run.py docker-build`, `python run.py docker-api`, `python run.py docker-fullstack`, and `python run.py docker-down` work when Docker is installed and fail with clear guidance when Docker is unavailable. (manual acceptance)
