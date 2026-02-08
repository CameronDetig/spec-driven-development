#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
SUPPORTED_MIN = (3, 10)
SUPPORTED_MAX_EXCLUSIVE = (3, 13)


def _venv_python() -> str:
    if sys.platform.startswith("win"):
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def _run(cmd: list[str], cwd: Path | None = None, check: bool = False) -> int:
    proc = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def _is_supported_version(version: tuple[int, int]) -> bool:
    return SUPPORTED_MIN <= version < SUPPORTED_MAX_EXCLUSIVE


def _version_text(version: tuple[int, int]) -> str:
    return f"{version[0]}.{version[1]}"


def _probe_python_version(cmd_prefix: list[str]) -> tuple[int, int] | None:
    try:
        proc = subprocess.run(
            cmd_prefix + ["-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    raw = proc.stdout.strip()
    parts = raw.split(".")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def _candidate_python_commands() -> list[list[str]]:
    candidates: list[list[str]] = []
    if sys.platform.startswith("win"):
        if shutil.which("py"):
            candidates.extend([["py", "-3.12"], ["py", "-3.11"], ["py", "-3.10"]])
        if shutil.which("python"):
            candidates.append(["python"])
        return candidates

    for command in ["python3.12", "python3.11", "python3.10", "python3", "python"]:
        if shutil.which(command):
            candidates.append([command])
    return candidates


def _select_supported_python_command(override: str | None = None) -> list[str] | None:
    if override:
        override_cmd = [override]
        version = _probe_python_version(override_cmd)
        if version is None:
            print(f"Could not execute Python override: {override}")
            return None
        if not _is_supported_version(version):
            print(
                "Unsupported Python override version: "
                f"{_version_text(version)}. Supported range is >=3.10 and <3.13."
            )
            return None
        return override_cmd

    for cmd in _candidate_python_commands():
        version = _probe_python_version(cmd)
        if version and _is_supported_version(version):
            print(f"Using Python {_version_text(version)} via: {' '.join(cmd)}")
            return cmd
    return None


def _attempt_python_install() -> int:
    print("Attempting to install Python 3.12 with an available package manager...")
    installers: list[list[str]] = []

    if sys.platform.startswith("win"):
        if shutil.which("winget"):
            installers.append(["winget", "install", "-e", "--id", "Python.Python.3.12"])
        if shutil.which("choco"):
            installers.append(["choco", "install", "python312", "-y"])
    elif sys.platform == "darwin":
        if shutil.which("brew"):
            installers.append(["brew", "install", "python@3.12"])
    else:
        if shutil.which("apt-get"):
            installers.append(["apt-get", "update"])
            installers.append(["apt-get", "install", "-y", "python3.12", "python3.12-venv"])
        elif shutil.which("dnf"):
            installers.append(["dnf", "install", "-y", "python3.12"])
        elif shutil.which("yum"):
            installers.append(["yum", "install", "-y", "python3.12"])

    # Fallback attempts for package managers that expose only 3.11 packages.
    if not installers:
        if sys.platform.startswith("win") and shutil.which("choco"):
            installers.append(["choco", "install", "python311", "-y"])
        elif sys.platform == "darwin" and shutil.which("brew"):
            installers.append(["brew", "install", "python@3.11"])
        elif shutil.which("apt-get"):
            installers.append(["apt-get", "update"])
            installers.append(["apt-get", "install", "-y", "python3.11", "python3.11-venv"])
        elif shutil.which("dnf"):
            installers.append(["dnf", "install", "-y", "python3.11"])
        elif shutil.which("yum"):
            installers.append(["yum", "install", "-y", "python3.11"])

    if not installers:
        print("No supported package manager detected for automatic Python install.")
        return 2

    for command in installers:
        print(f"Running: {' '.join(command)}")
        exit_code = _run(command)
        if exit_code != 0:
            print("Install command failed.")
            return exit_code
    return 0


def _ensure_venv(python_cmd: list[str]) -> str:
    if not VENV_DIR.exists():
        print("Creating virtual environment at .venv")
        _run(python_cmd + ["-m", "venv", str(VENV_DIR)], check=True)
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
        print("Usage: python run.py setup [--no-venv] [--with-llm] [--python <path-or-command>] [--install-python]")
        return 0

    use_venv = "--no-venv" not in args
    install_python = "--install-python" in args

    python_override: str | None = None
    for idx, arg in enumerate(args):
        if arg.startswith("--python="):
            python_override = arg.split("=", 1)[1].strip()
        elif arg == "--python" and idx + 1 < len(args):
            python_override = args[idx + 1].strip()

    if use_venv:
        selected_python = _select_supported_python_command(override=python_override)
        if selected_python is None and install_python:
            install_result = _attempt_python_install()
            if install_result != 0:
                print("Automatic Python install failed.")
                return install_result
            selected_python = _select_supported_python_command(override=python_override)

        if selected_python is None:
            print(
                "No supported Python interpreter found for venv creation.\n"
                "Supported range is >=3.10 and <3.13.\n"
                "Install Python 3.10, 3.11, or 3.12, then rerun setup.\n"
                "Optional: run 'python run.py setup --install-python' to attempt automated install."
            )
            return 2
        python_bin = _ensure_venv(selected_python)
    else:
        current_version = sys.version_info[:2]
        if not _is_supported_version(current_version):
            print(
                "Warning: Current Python "
                f"{_version_text((current_version[0], current_version[1]))} is outside the recommended range "
                "(>=3.10 and <3.13). Some dependencies may fail."
            )
        python_bin = sys.executable

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


def cmd_test_matrix(args: list[str]) -> int:
    if "--help" in args:
        print("Usage: python run.py test-matrix [-- <tox args>]")
        return 0

    python_bin = _venv_python() if VENV_DIR.exists() else sys.executable
    if os.getenv("PYTEST_CURRENT_TEST"):
        print("Detected pytest context; skipping nested tox execution.")
        return 0

    has_tox_in_python = _run(
        [python_bin, "-c", "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('tox') else 1)"]
    ) == 0

    print("Running tox test matrix")
    if has_tox_in_python:
        return _run([python_bin, "-m", "tox", *args])

    if shutil.which("tox"):
        return _run(["tox", *args])

    print(
        "tox is not installed in the active environment.\n"
        "Install it with one of:\n"
        f"  {python_bin} -m pip install tox\n"
        "  python -m pip install tox"
    )
    return 2


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

  python run.py setup [--no-venv] [--with-llm] [--python <exe>] [--install-python]
                                                 Install dependencies
  python run.py api                             Start FastAPI backend
  python run.py ui                              Start Streamlit UI
  python run.py fullstack                       Start API + UI together
  python run.py test                            Run pytest
  python run.py test-matrix                     Run tox matrix (py310/py311/py312)
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
        "test-matrix": cmd_test_matrix,
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
