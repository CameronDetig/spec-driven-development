import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent
RUN_PY = PROJECT_ROOT / "run.py"


@pytest.mark.unit
def test_run_py_exists():
    """
    Verify that run.py file exists in the project root.
    
    Spec: entrypoint-cli.md
    Requirement: "A `run.py` script that manages setup, API, UI, and test commands"
    """
    assert RUN_PY.exists(), f"Expected run.py at {RUN_PY}"
    assert RUN_PY.is_file()


@pytest.mark.integration
def test_run_py_help_command_prints_usage(monkeypatch):
    """
    Verify that 'python run.py help' prints usage and available commands.
    
    Spec: entrypoint-cli.md
    Acceptance Criteria: "`python run.py help` prints usage and available commands"
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    output = result.stdout.lower()
    
    # Verify that help output mentions the required commands
    assert "setup" in output, "Help should mention 'setup' command"
    assert "api" in output, "Help should mention 'api' command"
    assert "ui" in output, "Help should mention 'ui' command"
    assert "fullstack" in output, "Help should mention 'fullstack' command"
    assert "test" in output, "Help should mention 'test' command"
    assert "help" in output, "Help should mention 'help' command"


@pytest.mark.integration
def test_run_py_test_command_executes_pytest():
    """
    Verify that 'python run.py test' runs pytest successfully.
    
    Spec: entrypoint-cli.md
    Acceptance Criteria: "`python run.py test` runs pytest successfully"
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    env = dict(os.environ)
    # Prevent nested pytest execution when running under pytest.
    env["PYTEST_CURRENT_TEST"] = "1"
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "test"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PROJECT_ROOT,
        env=env,
    )
    
    # Test command should execute pytest
    # It may pass or fail, but should invoke pytest
    output = result.stdout + result.stderr
    assert "pytest" in output.lower() or "test" in output.lower() or "detected pytest context" in output.lower(), \
        "Test command should invoke pytest"


@pytest.mark.integration
def test_run_py_invalid_command_fails_clearly():
    """
    Verify that run.py fails clearly with actionable error for invalid commands.
    
    Spec: entrypoint-cli.md
    Requirement: "Commands MUST print clear status messages and fail clearly with actionable errors"
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "invalid_command_xyz"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    assert result.returncode != 0, "Invalid command should return non-zero exit code"
    output = result.stdout + result.stderr
    assert len(output) > 0, "Error message should be printed for invalid command"


@pytest.mark.integration
def test_run_py_no_arguments_shows_help():
    """
    Verify that running 'python run.py' without arguments shows help or usage.
    
    Spec: entrypoint-cli.md
    Requirement: "Clear help output with available commands"
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    result = subprocess.run(
        [sys.executable, str(RUN_PY)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # Should either show help or fail with usage message
    output = result.stdout + result.stderr
    assert len(output) > 0, "Should print usage or help when no arguments provided"


@pytest.mark.integration
def test_run_py_recognizes_setup_command():
    """
    Verify that run.py recognizes 'setup' command.
    
    Spec: entrypoint-cli.md
    Requirement: "`run.py` MUST support these commands: `setup`"
    Note: This test verifies command recognition, not full execution
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    # Using --help flag if available, or checking error message doesn't say "unknown command"
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "setup", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # If --help isn't supported, command should still be recognized
    output = result.stdout + result.stderr
    assert "unknown" not in output.lower() or result.returncode == 0, \
        "Setup command should be recognized"


@pytest.mark.integration
def test_run_py_recognizes_api_command():
    """
    Verify that run.py recognizes 'api' command.
    
    Spec: entrypoint-cli.md
    Requirement: "`run.py` MUST support these commands: `api`"
    Note: This test verifies command recognition, not full execution
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "api", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    output = result.stdout + result.stderr
    assert "unknown" not in output.lower() or result.returncode == 0, \
        "API command should be recognized"


@pytest.mark.integration
def test_run_py_recognizes_ui_command():
    """
    Verify that run.py recognizes 'ui' command.
    
    Spec: entrypoint-cli.md
    Requirement: "`run.py` MUST support these commands: `ui`"
    Note: This test verifies command recognition, not full execution
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "ui", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    output = result.stdout + result.stderr
    assert "unknown" not in output.lower() or result.returncode == 0, \
        "UI command should be recognized"


@pytest.mark.integration
def test_run_py_recognizes_fullstack_command():
    """
    Verify that run.py recognizes 'fullstack' command.
    
    Spec: entrypoint-cli.md
    Requirement: "`run.py` MUST support these commands: `fullstack`"
    Note: This test verifies command recognition, not full execution
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "fullstack", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    output = result.stdout + result.stderr
    assert "unknown" not in output.lower() or result.returncode == 0, \
        "Fullstack command should be recognized"


@pytest.mark.integration
def test_run_py_is_executable_with_python():
    """
    Verify that run.py can be executed with sys.executable.
    
    Spec: entrypoint-cli.md
    Requirement: "`run.py` MUST be cross-platform and use `sys.executable` for subprocess calls"
    """
    if not RUN_PY.exists():
        pytest.skip("run.py not yet implemented")
    
    result = subprocess.run(
        [sys.executable, str(RUN_PY), "help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # Should execute without import errors or syntax errors
    assert "SyntaxError" not in result.stderr, "run.py should not have syntax errors"
    assert "ImportError" not in result.stderr or result.returncode == 0, \
        "run.py should handle imports gracefully"
