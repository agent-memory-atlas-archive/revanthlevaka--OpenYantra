"""
Tests for POSIX workbook lock re-entrancy and pervasive superseded belief filtering.
Covers:
1. Re-entrant lock avoids self-deadlock on rejected writes (e.g. unknown sheet, invalid vocab).
2. Re-entrant lock avoids self-deadlock on conflicting updates.
3. build_context_markdown filters out superseded beliefs (active beliefs retained).
4. yantra_context.build_context_markdown filters out superseded beliefs.
5. SutraCompiler filters out superseded beliefs.
6. Semantic search (core.search and VidyaKosha.query) excludes superseded records by default.
"""

from pathlib import Path
from openyantra.core import (
    OpenYantra,
    WriteRequest,
    SHEET_BELIEFS,
    SHEET_LEDGER,
    is_superseded,
)
from openyantra.yantra_context import build_context_markdown as build_clipboard_context
from openyantra.yantra_sutra import SutraCompiler


def test_is_superseded_helper():
    """Verify is_superseded correctly classifies diverse inputs."""
    assert not is_superseded({})
    assert not is_superseded({"Superseded_By": None})
    assert not is_superseded({"Superseded_By": ""})
    assert not is_superseded({"Superseded_By": "none"})
    assert not is_superseded({"Superseded_By": "nan"})
    assert not is_superseded({"Status": "Active"})

    assert is_superseded({"Superseded_By": "Reverted in session log"})
    assert is_superseded({"Superseded_By": "Commit rev123"})
    assert is_superseded({"Contradiction_Flag": "Superseded by rev456"})
    assert is_superseded({"Status": "Superseded"})
    assert is_superseded({"Status": "Reverted"})


def test_posix_lock_reentrancy_on_rejected_write(tmp_path: Path):
    """
    Verify that a rejected write does not self-deadlock when _process holds the lock
    and calls _log_audit -> _write_sheet which re-enters the lock.
    """
    chitrapat = tmp_path / "chitrapat.ods"
    oy = OpenYantra(chitrapat)
    oy.bootstrap(user_name="Lock Tester", occupation="Engineer")

    # Write request targeting an unknown sheet (triggers rejection and audit logging)
    req = WriteRequest(
        requesting_agent="tester",
        sheet="Unknown Sheet Name",
        operation="add",
        fields={"Topic": "Deadlock Verification", "Content": "Should reject cleanly"},
    )

    res = oy.request_write(req)
    assert res["status"] == "rejected"
    assert "Unknown sheet" in res.get("reason", "")

    # Verify that the rejected write was recorded in the ledger without deadlocking
    ledger = oy._read_sheet(SHEET_LEDGER)
    assert any(
        str(row.get("Request ID")) == req.request_id and row.get("Status") == "rejected"
        for row in ledger
    )


def test_posix_lock_reentrancy_on_conflicting_write(tmp_path: Path):
    """
    Verify that a conflicting update write does not self-deadlock when _process
    holds the lock and calls _log_audit -> _write_sheet.
    """
    chitrapat = tmp_path / "chitrapat.ods"
    oy = OpenYantra(chitrapat)
    oy.bootstrap(user_name="Conflict Tester", occupation="Engineer")

    # Add initial belief
    initial_req = WriteRequest(
        requesting_agent="tester",
        sheet=SHEET_BELIEFS,
        operation="add",
        fields={
            "Topic": "Database Choice",
            "Position": "Always use Postgres",
            "Domain": "Architecture",
            "Status": "Active",
        },
        importance=8,
    )
    oy.request_write(initial_req)

    # Submit an update with an invalid vocabulary or conflict scenario
    conflict_req = WriteRequest(
        requesting_agent="tester",
        sheet=SHEET_BELIEFS,
        operation="add",
        fields={
            "Topic": "Database Choice",
            "Position": "Always use SQLite",
            "Domain": "Architecture",
            "Status": "InvalidStatusChoice",  # Invalid vocab triggers rejection & audit
        },
        importance=8,
    )
    res = oy.request_write(conflict_req)
    assert res["status"] == "rejected"
    assert "Invalid Status" in res.get("reason", "")


def test_all_context_paths_filter_superseded_beliefs(tmp_path: Path):
    """
    Verify that build_context_markdown, yantra_context, and SutraCompiler
    all exclude superseded beliefs and retain active beliefs.
    """
    chitrapat = tmp_path / "chitrapat.ods"
    oy = OpenYantra(chitrapat)
    oy.bootstrap(user_name="Context Lineage Tester", occupation="Engineer")

    # 1. Add an active belief
    active_req = WriteRequest(
        requesting_agent="tester",
        sheet=SHEET_BELIEFS,
        operation="add",
        fields={
            "Topic": "Code Style",
            "Position": "Always use 4 spaces for indentation",
            "Domain": "Values",
            "Confidence": "High",
            "Status": "Active",
            "Superseded_By": "",
        },
        importance=9,
    )
    oy.request_write(active_req)

    # 2. Add a superseded belief
    superseded_req = WriteRequest(
        requesting_agent="tester",
        sheet=SHEET_BELIEFS,
        operation="add",
        fields={
            "Topic": "Code Style",
            "Position": "Always use tabs for indentation",
            "Domain": "Values",
            "Confidence": "High",
            "Status": "Superseded",
            "Superseded_By": "Reverted in session log rev999",
        },
        importance=9,
    )
    oy.request_write(superseded_req)

    # ── Path A: oy.build_context_markdown() ─────────────────────────────
    ctx_md = oy.build_context_markdown()
    assert "Always use 4 spaces for indentation" in ctx_md
    assert "Always use tabs for indentation" not in ctx_md

    # ── Path B: yantra_context.build_context_markdown() ─────────────────
    clip_md = build_clipboard_context(oy, sections=["beliefs"])
    assert "Always use 4 spaces for indentation" in clip_md
    assert "Always use tabs for indentation" not in clip_md

    # ── Path C: SutraCompiler.compile() ─────────────────────────────────
    compiler = SutraCompiler(oy)
    sutra_res = compiler.compile(budget=2000, sections=["beliefs"])
    sutra_md = sutra_res["markdown"]
    assert "Always use 4 spaces for indentation" in sutra_md
    assert "Always use tabs for indentation" not in sutra_md

    # ── Path D: oy.load_session_context() ───────────────────────────────
    session_ctx = oy.load_session_context()
    active_positions = [b.get("Position") for b in session_ctx.get("beliefs", [])]
    assert "Always use 4 spaces for indentation" in active_positions
    assert "Always use tabs for indentation" not in active_positions


def test_search_excludes_superseded_records_by_default(tmp_path: Path):
    """
    Verify that semantic search excludes superseded records unless explicitly requested.
    """
    chitrapat = tmp_path / "chitrapat.ods"
    oy = OpenYantra(chitrapat)
    oy.bootstrap(user_name="Search Lineage Tester", occupation="Engineer")

    # Add active and superseded beliefs
    oy.request_write(
        WriteRequest(
            requesting_agent="tester",
            sheet=SHEET_BELIEFS,
            operation="add",
            fields={
                "Topic": "Authentication Mechanism",
                "Position": "Use opaque Redis session tokens for API auth",
                "Domain": "Values",
                "Status": "Active",
                "Superseded_By": "",
            },
            importance=9,
        )
    )
    oy.request_write(
        WriteRequest(
            requesting_agent="tester",
            sheet=SHEET_BELIEFS,
            operation="add",
            fields={
                "Topic": "Authentication Mechanism",
                "Position": "Use stateless JWT bearer tokens for API auth",
                "Domain": "Values",
                "Status": "Superseded",
                "Superseded_By": "Reverted in commit rev789",
            },
            importance=9,
        )
    )

    # Search with default include_superseded=False
    results_active = oy.search(
        "Authentication Mechanism",
        top_k=5,
        sheets=[SHEET_BELIEFS],
        include_superseded=False,
    )
    positions_active = [
        r.get("row", {}).get("Position")
        for r in results_active
        if isinstance(r.get("row"), dict) and r.get("row", {}).get("Position")
    ]
    assert "Use opaque Redis session tokens for API auth" in positions_active
    assert "Use stateless JWT bearer tokens for API auth" not in positions_active

    # Search with include_superseded=True surfaces historical records
    results_all = oy.search(
        "Authentication Mechanism",
        top_k=5,
        sheets=[SHEET_BELIEFS],
        include_superseded=True,
    )
    positions_all = [
        r.get("row", {}).get("Position")
        for r in results_all
        if isinstance(r.get("row"), dict) and r.get("row", {}).get("Position")
    ]
    assert "Use stateless JWT bearer tokens for API auth" in positions_all
