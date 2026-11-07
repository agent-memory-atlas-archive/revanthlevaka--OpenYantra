"""
Unit tests for OpenYantra Cyberpunk Terminal TUI (v6.1.0).
"""

import pytest
from pathlib import Path
from openyantra.core import OpenYantra
from openyantra.yantra_tui import render_tui


@pytest.fixture
def mock_oy(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="TUI Tester", occupation="Hacker")
    return oy


def test_render_tui(mock_oy):
    mock_oy.add_project("CyberDeck", domain="Hardware", status="Active")
    mock_oy.flush_open_loop("Solder GPIO headers", context="Hardware test")

    output = render_tui(mock_oy)
    assert "OPENYANTRA" in output
    assert "OPEN LOOPS" in output
    assert "ACTIVE PROJECTS" in output
    assert "CyberDeck" in output
    assert "Solder GPIO headers" in output
