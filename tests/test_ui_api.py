"""
Unit tests for OpenYantra Dashboard FastAPI Endpoints (v6.0).
"""

import pytest
from starlette.testclient import TestClient
from openyantra.core import OpenYantra
from openyantra.yantra_ui import app, set_oy


@pytest.fixture
def mock_oy(tmp_path, monkeypatch):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="UI Tester", occupation="Engineer")
    set_oy(oy)
    monkeypatch.setenv("OPENYANTRA_FILE", str(oy_file))
    return oy


def test_ui_root(mock_oy):
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert "OpenYantra" in res.text
    assert "v6.2.0" in res.text


def test_ui_health_and_stats(mock_oy):
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert "status" in res.json()

    res = client.get("/api/stats")
    assert res.status_code == 200
    assert "chitrapat_size_kb" in res.json()


def test_ui_inbox_and_loops(mock_oy):
    client = TestClient(app)
    res = client.post("/api/inbox", json={"text": "Review architecture deck"})
    assert res.status_code == 200

    # Add and resolve loop
    mock_oy.flush_open_loop("Resolve SSL certificates", context="Renew certs")
    res = client.post("/api/loops/Resolve SSL certificates/resolve", json={"resolution": "Done in UI"})
    assert res.status_code == 200


def test_ui_nidra_consolidate(mock_oy):
    mock_oy.log_session(topics=["Refactoring"], decisions=["Cleaned modules"])
    client = TestClient(app)
    res = client.post("/api/nidra/consolidate", json={"dry_run": True, "provider": "heuristic"})
    assert res.status_code == 200
    data = res.json()
    assert data["dry_run"] is True
    assert "summary" in data


def test_ui_vault_sync(mock_oy, tmp_path, monkeypatch):
    vault_dir = tmp_path / "ui_vault"
    monkeypatch.setenv("OPENYANTRA_VAULT_DIR", str(vault_dir))
    client = TestClient(app)
    res = client.post("/api/vault/sync", json={"path": "/etc"})  # request path is ignored
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert (vault_dir / "Identity.md").exists()
