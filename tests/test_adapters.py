"""
Unit tests for OpenYantra Framework Adapters (LangChain, CrewAI) v6.0.
"""

import pytest
from pathlib import Path
from openyantra.core import OpenYantra
from openyantra.adapters.langchain import (
    OpenYantraChatMessageHistory,
    OpenYantraRetriever,
    HumanMessage,
    AIMessage,
)
from openyantra.adapters.crewai import OpenYantraCrewMemory
from openyantra.adapters.openclaw import (
    session_start_hook,
    pre_compact_hook,
    post_compact_hook,
    session_end_hook,
)


@pytest.fixture
def mock_oy(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file)
    oy.bootstrap(user_name="Dev Tester", occupation="Engineer")
    return oy


def test_langchain_chat_history(mock_oy):
    history = OpenYantraChatMessageHistory(mock_oy, session_id="test_sess_001")
    history.add_user_message("Hello, how can I configure OpenYantra?")
    history.add_ai_message("You can run `yantra ui` or use the CLI commands.")
    history.add_message({"role": "user", "content": "Tell me more about Nidra."})

    assert len(history.messages) == 3
    assert isinstance(history.messages[0], HumanMessage)
    assert isinstance(history.messages[1], AIMessage)
    assert history.messages[0].content == "Hello, how can I configure OpenYantra?"

    # Flush to Chitrapat session log
    flush_res = history.flush_to_session_log()
    assert flush_res["status"] == "flushed"
    assert flush_res["turns"] == 3

    # Check session log in sheet
    sessions = mock_oy.get_sheet("Session Log")
    assert any("LangChain Dialogue: test_sess_001" in str(s.get("Topics Discussed", "")) for s in sessions)

    # Test clear
    history.clear()
    assert len(history.messages) == 0


def test_langchain_retriever(mock_oy):
    mock_oy.add_project(project="AeroX", domain="Aerospace", status="Active")
    retriever = OpenYantraRetriever(mock_oy, top_k=3)
    docs = retriever.invoke("AeroX")
    assert isinstance(docs, list)


def test_crewai_memory_save_and_route(mock_oy):
    crew_mem = OpenYantraCrewMemory(mock_oy, agent_name="ResearchAgent")

    # Save a task
    t_res = crew_mem.save("Audit database query plans", metadata={"type": "task", "project": "OpenYantra"})
    assert t_res.get("status") in ("written", "committed", "queued")

    # Save an open loop
    l_res = crew_mem.save("Review API rate limiting options", metadata={"type": "loop", "priority": "High"})
    assert l_res.get("status") in ("written", "committed", "queued")

    # Save a project
    p_res = crew_mem.save("QuantumSync", metadata={"type": "project", "domain": "Distributed Systems"})
    assert p_res.get("status") in ("written", "committed", "queued")

    # Check sheets
    tasks = mock_oy.get_sheet("Tasks")
    assert any("Audit database query plans" in str(t.get("Task", "")) for t in tasks)

    loops = mock_oy.get_sheet("Open Loops")
    assert any("Review API rate limiting options" in str(l.get("Topic", "")) for l in loops)

    projects = mock_oy.get_sheet("Projects")
    assert any("QuantumSync" in str(p.get("Project", "")) for p in projects)


def test_openclaw_adapter_lifecycle(tmp_path):
    oy_file = tmp_path / "chitrapat.ods"
    oy = OpenYantra(oy_file, agent_name="OpenClaw")
    oy.bootstrap(user_name="Agent Tester", occupation="Bot")
    oy.flush_open_loop(topic="Pending deployment", context="Needs CI/CD", priority="High")

    # 1. session_start_hook
    start_payload = {"system_prompt": "Base agent instructions."}
    res_start = session_start_hook(start_payload, file_path=oy_file)
    assert "[OPENYANTRA CONTEXT" in res_start["system_prompt"]
    assert "Base agent instructions." in res_start["system_prompt"]

    # 2. pre_compact_hook
    pre_payload = {"conversation": ["msg1", "msg2"]}
    res_pre = pre_compact_hook(pre_payload, file_path=oy_file)
    assert res_pre == pre_payload

    # 3. post_compact_hook (restores open loops)
    post_payload = {"new_context": "Compacted history summary"}
    res_post = post_compact_hook(post_payload, file_path=oy_file)
    assert "Anishtha restored after compaction" in res_post["new_context"]
    assert "Pending deployment" in res_post["new_context"]

    # 4. session_end_hook
    end_payload = {"topics": ["Deployment"], "decisions": ["Approved v6.2.0"], "new_memory": []}
    res_end = session_end_hook(end_payload, file_path=oy_file)
    assert res_end == end_payload

