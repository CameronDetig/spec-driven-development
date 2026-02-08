import importlib

import pytest


@pytest.mark.smoke
def test_streamlit_app_module_imports():
    """
    Verify that the Streamlit UI module can be imported without errors.
    
    Spec: streamlit-ui.md
    Acceptance Criteria: "UI runs locally against the API in default mock mode"
    Note: This is a smoke test to ensure the UI module exists and has no import errors.
    """
    pytest.importorskip("streamlit")
    module = importlib.import_module("ui.streamlit_app")
    assert module is not None
