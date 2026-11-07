"""
yantra_git.py -- OpenYantra Git Post-Commit Auto-Ingest Hook (v6.1.0)
Automatically indexes git commits, branch names, and file diffs into
OpenYantra's episodic Session Log and Task tracking without breaking workflow.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def find_git_root(path: Optional[str | Path] = None) -> Optional[Path]:
    """Finds the root directory of a git repository starting from path or cwd."""
    start = Path(path).resolve() if path else Path.cwd()
    curr = start
    while curr != curr.parent:
        if (curr / ".git").is_dir():
            return curr
        curr = curr.parent
    return None


def install_git_hook(repo_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """
    Installs a post-commit hook in the target git repository.
    """
    git_root = find_git_root(repo_path)
    if not git_root:
        return {"status": "error", "message": "No git repository found"}

    hooks_dir = git_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "post-commit"

    python_bin = sys.executable

    hook_script = f"""#!/usr/bin/env bash
# OpenYantra Git Post-Commit Auto-Ingest Hook v6.1
if command -v "{python_bin}" >/dev/null 2>&1; then
    "{python_bin}" -m openyantra.cli hook run >/dev/null 2>&1 &
fi
"""

    with open(hook_file, "w", encoding="utf-8") as f:
        f.write(hook_script)

    # Make executable
    st = os.stat(hook_file)
    os.chmod(hook_file, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    return {
        "status": "success",
        "hook_path": str(hook_file),
        "repo": str(git_root)
    }


def ingest_last_commit(repo_path: Optional[str | Path] = None, oy: Any = None) -> Dict[str, Any]:
    """
    Extracts the latest commit information from git log and ingests it into OpenYantra's Session Log.
    """
    git_root = find_git_root(repo_path)
    if not git_root:
        return {"status": "error", "message": "No git repository found"}

    try:
        # Get commit hash, author, subject, body
        log_proc = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%h%x1f%an%x1f%s%x1f%b"],
            cwd=str(git_root),
            capture_output=True,
            text=True,
            check=True
        )
        parts = log_proc.stdout.strip().split("\x1f")
        commit_hash = parts[0] if len(parts) > 0 else "unknown"
        author = parts[1] if len(parts) > 1 else "unknown"
        subject = parts[2] if len(parts) > 2 else "Git commit"
        body = parts[3].strip() if len(parts) > 3 else ""

        # Get branch
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(git_root),
            capture_output=True,
            text=True
        )
        branch = branch_proc.stdout.strip() or "main"

        # Get changed files
        files_proc = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            cwd=str(git_root),
            capture_output=True,
            text=True
        )
        changed_files = [f.strip() for f in files_proc.stdout.strip().split("\n") if f.strip()]

        project_name = git_root.name

        if oy:
            from datetime import date
            notes = f"Repo: {project_name} | Branch: {branch} | Hash: {commit_hash}"
            if changed_files:
                notes += f" | Files: {', '.join(changed_files[:5])}"

            decisions = [f"Commit [{commit_hash}]: {subject}"]
            if body:
                decisions.append(f"Details: {body[:150]}")

            oy.log_session(
                topics=[f"Git Activity: {project_name}"],
                decisions=decisions,
                notes=notes
            )

        return {
            "status": "ingested",
            "repo": project_name,
            "branch": branch,
            "commit": commit_hash,
            "author": author,
            "subject": subject,
            "files_changed_count": len(changed_files)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
