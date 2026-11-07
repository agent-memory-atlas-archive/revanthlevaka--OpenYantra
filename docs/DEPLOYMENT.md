# OpenYantra Deployment Guide -- v6.1.0

> OpenYantra Engine · Desktop HUD · MCP Server · Obsidian Vault · LangChain · CrewAI · SQLite WAL · Passkey Lock

## 1. Installation

```bash
# macOS / Linux (Self-contained)
curl -sSL https://raw.githubusercontent.com/revanthlevaka/OpenYantra/main/install.sh | bash

# Windows (PowerShell)
irm https://raw.githubusercontent.com/revanthlevaka/OpenYantra/main/install.ps1 | iex

# Manual pip install
git clone https://github.com/revanthlevaka/OpenYantra.git
cd OpenYantra
pip install -e ".[full]"
```

---

## 2. Desktop App & Floating HUD (`Cmd+Shift+Y`)

Launch the native desktop window or Raycast/Spotlight-style floating palette:

```bash
# Launch floating HUD palette
yantra desktop
# or alias
yantra hud

# Launch full native window
yantra desktop --mode dashboard
```

- **Global Hotkey:** `Cmd+Shift+Y` (macOS) or `Ctrl+Shift+Y` (Windows/Linux) slides the HUD open over whichever IDE (Cursor, VS Code) or terminal you have active.
- **Shortcuts:** `Enter` to save capture or copy selected search item, `Tab` to switch views, `Escape` to close.

---

## 3. 1-Click MCP Setup for Claude & Cursor

Automatically configure Claude Desktop and Cursor without editing JSON files manually:

```bash
# Auto-detect and configure all installed clients
yantra mcp setup

# Or target specific client
yantra mcp setup --client claude
yantra mcp setup --client cursor
```

After running, restart Claude Desktop or Cursor to immediately access OpenYantra memory tools (`yantra_search`, `yantra_get_sheet`, `yantra_request_write`, etc.).

---

## 4. Autonomous Sleep & Memory Consolidation (Nidra)

Run the cognitive consolidation daemon locally:

```bash
# Live consolidation
yantra dream

# Or simulation pass
yantra dream --dry-run
```

- Connects to local Ollama (`http://localhost:11434`) if active (e.g., `llama3`, `mistral`, `phi3`).
- Deterministic heuristic fallback if Ollama is not running.
- Clusters episodic logs, resolves completed loops, and promotes user preferences to `Beliefs & Principles`.

---

## 5. Bi-Directional Obsidian Vault Sync

Keep your Obsidian notes and OpenYantra ledger in sync:

```bash
# Bi-directional sync (imports checkbox changes, re-exports notes)
yantra vault sync ~/my_vault

# Export only
yantra vault export ~/my_vault

# Import only (detects checked - [x] tasks and resolves them in OpenYantra)
yantra vault import ~/my_vault
```

---

## 6. Git Commit Auto-Ingest Hook

Automatically index git commits across your projects:

```bash
# Install post-commit hook in current repository
yantra hook install

# Ingest last commit manually
yantra hook run
```

---

## 7. Cyberpunk Terminal TUI

For SSH sessions and terminal purists:

```bash
yantra tui
```

Interactive keyboard shortcuts: `[i]` Quick Capture, `[d]` Run Dream, `[h]` Launch HUD, `[q]` Quit.

---

## 8. Framework Adapters (LangChain & CrewAI)

### LangChain Integration:
```python
from openyantra import OpenYantra
from openyantra.adapters.langchain import OpenYantraChatMessageHistory, OpenYantraRetriever

oy = OpenYantra("~/openyantra/chitrapat.ods")

# Chat History
history = OpenYantraChatMessageHistory(oy, session_id="session_42")
history.add_user_message("Let's refactor the database schema")
history.add_ai_message("I suggest enabling WAL mode")
history.flush_to_session_log()

# Semantic Retriever
retriever = OpenYantraRetriever(oy, top_k=5)
docs = retriever.invoke("What are my core architectural beliefs?")
```

### CrewAI Multi-Agent Memory:
```python
from openyantra import OpenYantra
from openyantra.adapters.crewai import OpenYantraCrewMemory

oy = OpenYantra("~/openyantra/chitrapat.ods")
memory = OpenYantraCrewMemory(oy, agent_name="ResearchAnalyst")

# Agent saves discovery directly into OpenYantra
memory.save("QuantumSync reached 99.9% fault tolerance", metadata={"type": "project", "domain": "Core"})
```

---

## 9. Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **"Chitrapat not found"** | Run `yantra bootstrap` to create your initial memory vault. |
| **"pywebview not found"** | Run `pip install pywebview` for native borderless desktop windows. |
| **"Port 7331 in use"** | Specify an alternative port: `yantra ui --port 7335` or `yantra desktop --port 7335`. |
| **"MCP server not responding"** | Run `yantra doctor` to verify environment and test with `yantra mcp serve`. |
