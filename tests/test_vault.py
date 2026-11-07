"""
Unit tests for OpenYantra Obsidian Vault Sync (v6.0).
"""

import pytest
from openyantra.core import OpenYantra
from openyantra.yantra_vault import VaultSync


@pytest.fixture
def mock_oy(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="Dev Tester", occupation="Engineer")
    return oy


def test_vault_export(mock_oy, tmp_path):
    vault_dir = tmp_path / "test_vault"
    mock_oy.add_project(project="HyperDrive", domain="Core", status="Active")
    mock_oy.add_person(name="Ada Lovelace", relationship="Collaborator")
    mock_oy.flush_open_loop(topic="Calibrate plasma drive", context="Check telemetry")

    sync = VaultSync(mock_oy, vault_dir)
    res = sync.export_vault()

    assert res["status"] == "success"
    assert (vault_dir / "Identity.md").exists()
    assert (vault_dir / "Beliefs.md").exists()
    assert (vault_dir / "Open Loops.md").exists()
    assert (vault_dir / "Projects" / "HyperDrive.md").exists()
    assert (vault_dir / "People" / "Ada Lovelace.md").exists()

    # Verify frontmatter in project file
    content = (vault_dir / "Projects" / "HyperDrive.md").read_text(encoding="utf-8")
    assert "type: project" in content
    assert "HyperDrive" in content


def test_vault_import_resolves_loops(mock_oy, tmp_path):
    vault_dir = tmp_path / "test_vault"
    mock_oy.flush_open_loop(topic="Fix memory leak", context="Check heap profiling")

    sync = VaultSync(mock_oy, vault_dir)
    sync.export_vault()

    loops_file = vault_dir / "Open Loops.md"
    assert loops_file.exists()

    # Simulate user checking the box in Obsidian
    content = loops_file.read_text(encoding="utf-8")
    updated_content = content.replace("- [ ] **Fix memory leak**", "- [x] **Fix memory leak**")
    loops_file.write_text(updated_content, encoding="utf-8")

    # Import back
    import_res = sync.import_vault()
    assert "Fix memory leak" in import_res["loops_resolved"]

    # Verify in OpenYantra
    loops = mock_oy.get_sheet("Open Loops")
    target = next((l for l in loops if l.get("Topic") == "Fix memory leak"), None)
    assert target is not None
    assert str(target.get("Resolved?", "")).lower() == "yes"


def test_vault_import_new_item_and_inbox(mock_oy, tmp_path):
    vault_dir = tmp_path / "test_vault"
    sync = VaultSync(mock_oy, vault_dir)
    sync.export_vault()

    # Append a new loop
    loops_file = vault_dir / "Open Loops.md"
    with open(loops_file, "a", encoding="utf-8") as f:
        f.write("\n- [ ] **Research Quantum Annealing**\n")

    # Create an Inbox.md
    inbox_file = vault_dir / "Inbox.md"
    inbox_file.write_text("Call dentist at 3pm tomorrow\nRead new paper on RAG", encoding="utf-8")

    import_res = sync.import_vault()
    assert "Research Quantum Annealing" in import_res["new_loops_created"]
    assert len(import_res["inbox_items_imported"]) == 2

    # Verify new loop exists in sheet
    loops = mock_oy.get_sheet("Open Loops")
    assert any("Research Quantum Annealing" in str(l.get("Topic", "")) for l in loops)
