import importlib

import pytest


@pytest.mark.smoke
def test_streamlit_app_module_imports():
    pytest.importorskip("streamlit")
    module = importlib.import_module("ui.streamlit_app")
    assert module is not None
