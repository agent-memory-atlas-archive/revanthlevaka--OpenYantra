"""
Tests verifying the fixes for defects uncovered by Simon Strandgaard's Agent Memory Atlas audit:
1. Word-boundary noise admission filtering (prevents 'ensure' from being dropped by 'sure').
2. WriteQueue acknowledgment on commit (prevents double-writes on OpenYantra instantiation).
3. Long inbox item routing (> 50 chars) without truncation or orphan row generation.
"""

import pytest
from openyantra.core import OpenYantra, _is_worth_remembering, SHEET_TASKS


def test_noise_admission_word_boundary():
    # 'Ensure' should NOT trigger 'sure'
    admit, reason = _is_worth_remembering({"Task": "Ensure the backup runs nightly", "Importance": 7}, SHEET_TASKS)
    assert admit is True, f"Failed: {reason}"

    # 'Assure' should NOT trigger 'sure'
    admit, reason = _is_worth_remembering({"Task": "Assure compliance with SOC2 standards", "Importance": 7}, SHEET_TASKS)
    assert admit is True, f"Failed: {reason}"

    # Exact noise word 'sure' SHOULD be dropped
    admit, reason = _is_worth_remembering({"Task": "Sure thing boss", "Importance": 3}, SHEET_TASKS)
    assert admit is False
    assert "noise pattern: 'sure'" in reason

    # 'User said thanks' SHOULD be dropped
    admit, reason = _is_worth_remembering({"Task": "User said thanks for the help", "Importance": 3}, SHEET_TASKS)
    assert admit is False
    assert "noise pattern: 'user said thanks'" in reason


def test_write_queue_acknowledgment_and_no_double_replay(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="Audit Tester", occupation="Engineer")

    # Queue should be empty after bootstrap writes commit
    assert oy._queue.is_empty()

    # Add a task
    oy.add_task(task="Ship atlas bugfixes", project="OpenYantra", priority="High")
    
    # Verify queue is empty because write was acknowledged
    assert oy._queue.is_empty()

    tasks_initial = oy.get_sheet("tasks")
    assert len(tasks_initial) == 1
    assert tasks_initial[0].get("Task") == "Ship atlas bugfixes"

    # Instantiate a second OpenYantra on the same workbook (simulates process restart / CLI command)
    oy2 = OpenYantra(oy_file)
    tasks_after_restart = oy2.get_sheet("tasks")
    
    # Must NOT have duplicated the task
    assert len(tasks_after_restart) == 1
    assert tasks_after_restart[0].get("Task") == "Ship atlas bugfixes"


def test_route_inbox_long_content(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="Audit Tester", occupation="Engineer")

    long_content = "Need to conduct a comprehensive security review and architectural assessment of all microservices before Q4 launch"
    assert len(long_content) > 50

    oy.inbox(text=long_content)
    inbox_before = oy.get_sheet("inbox")
    assert len(inbox_before) == 1
    assert inbox_before[0].get("Routed?") == "No"

    # Route inbox
    decisions = oy.route_inbox()
    assert len(decisions) >= 1

    inbox_after = oy.get_sheet("inbox")
    # Must not have created an orphan junk row
    assert len(inbox_after) == 1
    assert inbox_after[0].get("Routed?") == "Yes"
    assert inbox_after[0].get("Content") == long_content
