#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"


def _venv_python() -> str:
    if sys.platform.startswith("win"):
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def _run(cmd: list[str], cwd: Path | None = None, check: bool = False) -> int:
    proc = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def _ensure_venv() -> str:
    if not VENV_DIR.exists():
        print("Creating virtual environment at .venv")
        _run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    return _venv_python()


def _has_docker() -> bool:
    return shutil.which("docker") is not None


def _download_llm_assets(python_bin: str) -> int:
    print("Downloading distilgpt2 model assets...")
    return _run(
        [
            python_bin,
            "-c",
            (
                "from transformers import pipeline; "
                "pipeline('text-generation', model='distilgpt2', tokenizer='distilgpt2')"
            ),
        ]
    )


def cmd_setup(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py setup [--no-venv] [--with-llm]")
        return 0

    use_venv = "--no-venv" not in args
    python_bin = _ensure_venv() if use_venv else sys.executable

    print("Installing dependencies from requirements.txt")
    result = _run([python_bin, "-m", "pip", "install", "-r", "requirements.txt"])
    if result != 0:
        return result

    if "--with-llm" in args:
        return _download_llm_assets(python_bin)

    return 0


def cmd_api(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py api")
        return 0

    python_bin = _venv_python() if VENV_DIR.exists() else sys.executable
    return _run([python_bin, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"])


def cmd_ui(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py ui")
        return 0

    python_bin = _venv_python() if VENV_DIR.exists() else sys.executable
    return _run([python_bin, "-m", "streamlit", "run", "ui/streamlit_app.py", "--server.port", "8501"])


def cmd_test(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py test")
        return 0

    python_bin = _venv_python() if VENV_DIR.exists() else sys.executable
    print("Running pytest")
    if os.getenv("PYTEST_CURRENT_TEST"):
        # Prevent recursive pytest invocation when run.py is tested by pytest.
        print("Detected pytest context; skipping nested pytest execution.")
        return 0
    return _run([python_bin, "-m", "pytest", "-q"])


def cmd_fullstack(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py fullstack")
        return 0

    python_bin = _venv_python() if VENV_DIR.exists() else sys.executable
    processes: list[subprocess.Popen] = []
    try:
        api_proc = subprocess.Popen(
            [python_bin, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
            cwd=PROJECT_ROOT,
        )
        processes.append(api_proc)
        time.sleep(1.5)

        ui_proc = subprocess.Popen(
            [python_bin, "-m", "streamlit", "run", "ui/streamlit_app.py", "--server.port", "8501"],
            cwd=PROJECT_ROOT,
        )
        processes.append(ui_proc)
        print("API: http://127.0.0.1:8000")
        print("UI:  http://127.0.0.1:8501")

        ui_proc.wait()
        return ui_proc.returncode or 0
    except KeyboardInterrupt:
        return 0
    finally:
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


def _docker_unavailable() -> int:
    print("Docker is not installed or not on PATH. Use local commands instead (setup/api/ui/fullstack/test).")
    return 2


def cmd_docker_build(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py docker-build")
        return 0
    if not _has_docker():
        return _docker_unavailable()
    return _run(["docker", "compose", "build"])


def cmd_docker_api(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py docker-api")
        return 0
    if not _has_docker():
        return _docker_unavailable()
    return _run(["docker", "compose", "up", "api"])


def cmd_docker_fullstack(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py docker-fullstack")
        return 0
    if not _has_docker():
        return _docker_unavailable()
    return _run(["docker", "compose", "up", "api", "ui"])


def cmd_docker_down(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py docker-down")
        return 0
    if not _has_docker():
        return _docker_unavailable()
    return _run(["docker", "compose", "down"])


def show_help() -> int:
    print(
        """
Customer FAQ Assistant - Commands

  python run.py setup [--no-venv] [--with-llm]  Install dependencies
  python run.py api                             Start FastAPI backend
  python run.py ui                              Start Streamlit UI
  python run.py fullstack                       Start API + UI together
  python run.py test                            Run pytest
  python run.py help                            Show this help

Optional Docker helpers:
  python run.py docker-build
  python run.py docker-api
  python run.py docker-fullstack
  python run.py docker-down
""".strip()
    )
    return 0


def main() -> int:
    os.chdir(PROJECT_ROOT)

    if len(sys.argv) < 2:
        return show_help()

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        "setup": cmd_setup,
        "api": cmd_api,
        "ui": cmd_ui,
        "fullstack": cmd_fullstack,
        "test": cmd_test,
        "help": lambda _args: show_help(),
        "docker-build": cmd_docker_build,
        "docker-api": cmd_docker_api,
        "docker-fullstack": cmd_docker_fullstack,
        "docker-down": cmd_docker_down,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        show_help()
        return 1

    return commands[command](args)


if __name__ == "__main__":
    raise SystemExit(main())
