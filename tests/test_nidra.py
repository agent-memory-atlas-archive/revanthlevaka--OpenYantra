"""
Unit tests for OpenYantra Nidra Consolidation Engine (v6.0).
"""

import pytest
from openyantra.core import OpenYantra
from openyantra.yantra_nidra import NidraConsolidator


@pytest.fixture
def mock_oy(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="Dev Tester", occupation="Engineer")
    return oy


def test_nidra_cluster_sessions(mock_oy):
    # Log a few sessions
    mock_oy.log_session(
        topics=["Database schema migration"],
        decisions=["Switched to SQLite WAL mode", "User prefers SQLite over Postgres for local dev"],
        notes="Project: OpenYantra"
    )
    mock_oy.log_session(
        topics=["FastAPI UI fixes"],
        decisions=["Resolved broken navigation cards"],
        notes="Project: OpenYantra"
    )

    nidra = NidraConsolidator(mock_oy)
    cluster = nidra.cluster_sessions()
    assert cluster["count"] >= 2
    assert "Database schema migration" in cluster["topics"]


def test_nidra_detect_and_promote_preferences(mock_oy):
    mock_oy.log_session(
        topics=["Architecture"],
        decisions=["User prefers dark mode across all interfaces", "rule: always write python unit tests"]
    )
    # Log a reverted decision that should NOT be promoted
    mock_oy.log_session(
        topics=["Reverted Database Experiment"],
        decisions=["Reverted / Superseded Decision: user prefers Postgres over SQLite"],
        notes="Status: REVERTED"
    )
    nidra = NidraConsolidator(mock_oy)
    candidates = nidra.detect_promotable_preferences()
    assert len(candidates) >= 1
    found_dark_mode = any("dark mode" in c["Belief / Principle"].lower() for c in candidates)
    assert found_dark_mode
    found_reverted = any("postgres" in c["Belief / Principle"].lower() for c in candidates)
    assert not found_reverted, "Reverted decision should not be promoted into beliefs"



def test_nidra_prune_and_resolve_loops(mock_oy):
    # Add an open loop
    mock_oy.flush_open_loop(
        topic="Optimize database queries",
        context="Need to check index performance",
        priority="High"
    )

    # Now log a session that resolves it
    mock_oy.log_session(
        topics=["Database optimization"],
        decisions=["Optimize database queries completed with 10x speedup"]
    )

    nidra = NidraConsolidator(mock_oy)
    resolved = nidra.prune_and_resolve_loops(dry_run=False)
    assert len(resolved) >= 1
    assert any("Optimize database queries" in r["topic"] for r in resolved)

    # Verify loop is resolved in sheet
    loops = mock_oy.get_sheet("Open Loops")
    target = next((l for l in loops if l.get("Topic") == "Optimize database queries"), None)
    assert target is not None
    assert str(target.get("Resolved?", "")).lower() == "yes"


def test_nidra_full_consolidation_heuristic(mock_oy):
    mock_oy.log_session(
        topics=["Initial setup"],
        decisions=["User prefers clean code", "Configured environment"]
    )

    nidra = NidraConsolidator(mock_oy)
    result = nidra.consolidate(dry_run=False, provider="heuristic")

    assert result["dry_run"] is False
    assert result["provider_used"] == "heuristic"
    assert result["sessions_clustered"] >= 1
    assert len(result["summary"]) > 0
    assert len(result["promoted_preferences"]) >= 1
    
    # Verify the belief actually landed in the sheet
    beliefs = mock_oy.get_sheet("beliefs")
    assert any("clean code" in str(b.get("Position", "")).lower() for b in beliefs)
