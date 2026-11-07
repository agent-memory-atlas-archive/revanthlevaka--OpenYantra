"""
crewai.py -- OpenYantra CrewAI Memory Adapter v6.0
Provides long-term memory persistence and contextual recall for multi-agent CrewAI teams.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class OpenYantraCrewMemory:
    """
    CrewAI Long-Term & Short-Term Memory Integration.
    Routes agent thoughts, task outputs, and decisions into OpenYantra's Chitrapat sheets.
    """

    def __init__(self, oy: Any, agent_name: str = "CrewAIAgent"):
        self.oy = oy
        self.agent_name = agent_name

    def save(self, value: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Saves an item produced by a CrewAI agent into OpenYantra.
        Routes intelligently based on metadata tags or content.
        """
        meta = metadata or {}
        kind = meta.get("type", "").lower()

        if kind == "task":
            return self.oy.add_task(
                task=value,
                project=meta.get("project", ""),
                priority=meta.get("priority", "Medium")
            )
        elif kind in ("loop", "open_loop"):
            return self.oy.flush_open_loop(
                topic=value,
                context=meta.get("context", "Created by CrewAI Agent"),
                priority=meta.get("priority", "Medium")
            )
        elif kind == "project":
            return self.oy.add_project(
                project=value,
                domain=meta.get("domain", ""),
                status=meta.get("status", "Active")
            )
        elif kind == "person":
            return self.oy.add_person(
                name=value,
                relationship=meta.get("relationship", ""),
                context=meta.get("context", "")
            )
        else:
            # Default: route as session decision or inbox item
            if meta.get("inbox", False):
                return self.oy.inbox(value, source="Agent-observed")
            return self.oy.log_session(
                topics=[meta.get("task", f"CrewAI: {self.agent_name}")],
                decisions=[value],
                notes=f"Agent: {self.agent_name}"
            )

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches OpenYantra memory for relevant context for CrewAI agents.
        """
        try:
            results = self.oy.search(query=query, top_k=limit)
            return [
                {
                    "content": r.get("text") or r.get("content") or str(r.get("fields", {})),
                    "sheet": r.get("sheet", ""),
                    "score": r.get("score", 0.0),
                    "metadata": r.get("fields", {})
                }
                for r in results
            ]
        except Exception:
            return []
