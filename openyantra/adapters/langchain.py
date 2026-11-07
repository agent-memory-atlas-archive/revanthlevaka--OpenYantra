"""
langchain.py -- OpenYantra LangChain Adapter v6.0
Provides drop-in memory history and semantic retrieval for LangChain and LangGraph.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.documents import Document
    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False

    class BaseChatMessageHistory:  # type: ignore[no-redef]
        """Fallback base message history class."""
        pass

    class BaseRetriever:  # type: ignore[no-redef]
        """Fallback base retriever class."""
        pass

    class BaseMessage:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class HumanMessage(BaseMessage):
        type: str = "human"

    class AIMessage(BaseMessage):
        type: str = "ai"

    class Document:  # type: ignore[no-redef]
        def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
            self.page_content = page_content
            self.metadata = metadata or {}

        def __repr__(self) -> str:
            return f"Document(page_content='{self.page_content}', metadata={self.metadata})"


class OpenYantraChatMessageHistory(BaseChatMessageHistory):
    """
    OpenYantra Chat Message History for LangChain.
    Stores episodic conversations in memory and can automatically flush them
    to OpenYantra's Chitrapat Session Log.
    """

    def __init__(self, oy: Any, session_id: str = "default_session", agent_name: str = "LangChainAgent"):
        self.oy = oy
        self.session_id = session_id
        self.agent_name = agent_name
        self._messages: List[BaseMessage] = []

    @property
    def messages(self) -> List[BaseMessage]:
        return self._messages

    def add_message(self, message: Any) -> None:
        if isinstance(message, BaseMessage):
            self._messages.append(message)
        elif isinstance(message, str):
            self._messages.append(HumanMessage(content=message))
        elif isinstance(message, dict):
            role = message.get("role", "human")
            content = message.get("content", "")
            if role in ("user", "human"):
                self._messages.append(HumanMessage(content=content))
            else:
                self._messages.append(AIMessage(content=content))

    def add_user_message(self, message: str) -> None:
        self._messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self._messages.append(AIMessage(content=message))

    def clear(self) -> None:
        self._messages.clear()

    def flush_to_session_log(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Commits conversation summary into OpenYantra's Session Log.
        """
        if not self._messages:
            return {"status": "empty"}

        [m.content for m in self._messages if isinstance(m, HumanMessage)]
        ai_msgs = [m.content for m in self._messages if isinstance(m, AIMessage)]

        decisions = [f"Assistant response: {ai[:100]}..." for ai in ai_msgs[:3]]
        notes = f"Session {self.session_id} with {len(self._messages)} turns."

        res = self.oy.log_session(
            topics=[topic or f"LangChain Dialogue: {self.session_id}"],
            decisions=decisions,
            notes=notes
        )
        return {"status": "flushed", "turns": len(self._messages), "write_result": res}


class OpenYantraRetriever(BaseRetriever):
    """
    OpenYantra Semantic Knowledge Retriever for LangChain.
    Queries VidyaKosha hybrid vector/lexical index and returns LangChain Documents.
    """

    oy: Any = None
    top_k: int = 5
    sheets: Optional[List[str]] = None

    def __init__(self, oy: Any, top_k: int = 5, sheets: Optional[List[str]] = None, **kwargs: Any):
        if _HAS_LANGCHAIN:
            super().__init__(**kwargs)
        self.oy = oy
        self.top_k = top_k
        self.sheets = sheets

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant memory records from OpenYantra."""
        results = self.oy.search(query=query, top_k=self.top_k, sheets=self.sheets)
        docs: List[Document] = []
        for r in results:
            content = r.get("text") or r.get("content") or str(r.get("fields", {}))
            meta = {
                "sheet": r.get("sheet", ""),
                "score": r.get("score", 0.0),
                "source": "OpenYantra",
            }
            if "fields" in r and isinstance(r["fields"], dict):
                meta.update(r["fields"])
            docs.append(Document(page_content=content, metadata=meta))
        return docs

    def _get_relevant_documents(self, query: str, **kwargs: Any) -> List[Document]:
        return self.get_relevant_documents(query)

    def invoke(self, input: str, **kwargs: Any) -> List[Document]:
        return self.get_relevant_documents(input)
