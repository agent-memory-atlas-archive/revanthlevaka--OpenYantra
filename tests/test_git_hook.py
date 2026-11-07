"""
Unit tests for OpenYantra Git Auto-Ingest Hook (v6.1.0).
"""

import os
import subprocess
import pytest
from openyantra.core import OpenYantra
from openyantra.yantra_git import find_git_root, install_git_hook, ingest_last_commit


@pytest.fixture
def temp_git_repo(tmp_path):
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Committer"], cwd=str(repo_dir), check=True)
    subprocess.run(["git", "config", "user.email", "committer@example.com"], cwd=str(repo_dir), check=True)

    # Make an initial commit
    dummy_file = repo_dir / "app.py"
    dummy_file.write_text("print('hello world')", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=str(repo_dir), check=True)
    subprocess.run(["git", "commit", "-m", "feat: initial commit for testing"], cwd=str(repo_dir), check=True)
    return repo_dir


@pytest.fixture
def mock_oy(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="Dev Tester", occupation="Engineer")
    return oy


def test_find_git_root(temp_git_repo):
    root = find_git_root(temp_git_repo)
    assert root == temp_git_repo


def test_install_git_hook(temp_git_repo):
    res = install_git_hook(temp_git_repo)
    assert res["status"] == "success"
    hook_file = temp_git_repo / ".git" / "hooks" / "post-commit"
    assert hook_file.exists()
    if os.name != "nt":
        assert os.access(hook_file, os.X_OK)


def test_ingest_last_commit(temp_git_repo, mock_oy):
    res = ingest_last_commit(temp_git_repo, oy=mock_oy)
    assert res["status"] == "ingested"
    assert res["subject"] == "feat: initial commit for testing"
    assert res["repo"] == "test_repo"

    # Verify session log in sheet
    sessions = mock_oy.get_sheet("Session Log")
    assert any("Git Activity: test_repo" in str(s.get("Topics Discussed", "")) for s in sessions)
