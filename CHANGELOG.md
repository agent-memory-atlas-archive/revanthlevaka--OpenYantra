# OpenYantra Changelog

All notable changes documented here. Follows semantic versioning.

---

## [6.2.0] -- 2026-11-07 ("Design System & Living Brain Comparison")

### Added
- **Design System Asset Modernization**:
  - Root `assets/brand/` with sacred geometric vector brandmarks and horizontal logo marks (`logo-horizontal.svg`, `banner-github.svg`).
  - High-resolution SVG screenshot suites in `assets/screenshots/` showcasing the Today command centre, Web UI, Cyberpunk Terminal TUI, and Open Loops.
- **Living Brain (`livingbrain.com`) Architectural Comparison**:
  - Added comprehensive comparison across data sovereignty, human editability, open formats, offline readiness, and desktop HUD ergonomics.
- **Version Bump**:
  - Bumped to `v6.2.0` across all libraries, CLI entry points, web UI, installers, and test fixtures.

## [6.1.0] -- 2026-11-07 ("Akasha & Sutra")

### Added
- **OpenYantra Desktop App v1.0.0** (`openyantra/desktop.py`):
  - Ultra-lightweight native OS window launcher using `pywebview` (< 15MB binary, zero Electron bloat).
  - Floating Raycast/Spotlight-style HUD palette (`UI/v4/hud.html`) triggered via `Cmd+Shift+Y` (macOS) / `Ctrl+Shift+Y` (Windows/Linux) directly over Cursor and VS Code.
  - Quick-capture with auto-routing prefixes (`#project`, `@person`, `!urgent`), live semantic recall search, and 1-click sleep consolidation.
- **Git Commit Auto-Ingest Hook** (`openyantra/yantra_git.py`):
  - `yantra hook install [repo]`: Installs a git post-commit hook that automatically indexes commits, branches, messages, and diff file lists into `Session Log`.
  - `yantra hook run`: Ingests the latest commit on demand.
- **Cyberpunk Terminal TUI** (`openyantra/yantra_tui.py`):
  - Interactive terminal dashboard (`yantra tui`) with ANSI styling, live loop tracking, active projects, recent decisions, and hotkeys.
- **Expanded Test Suite**:
  - 68 automated unit and integration tests passing with 100% success rate across 15 test files.

## [6.0.0] -- 2026-11-07 ("Sutra & Nidra")

### Added
- **Raksha Secret & Credential Redactor Guard** (`openyantra/yantra_security.py`):
  - Automatically intercepts writes to the Chitrapat ledger and redacts Anthropic, OpenAI, AWS, GitHub, Google API keys, Slack tokens, and private keys.
- **1-Click MCP Auto-Configurator** (`openyantra/mcp_setup.py`):
  - `yantra mcp setup [--client all|claude|cursor]`: Safely configures Claude Desktop and Cursor JSON configs with automatic backups.
- **Nidra: Autonomous Sleep & Memory Consolidation Engine** (`openyantra/yantra_nidra.py`):
  - `yantra dream` / `yantra consolidate`: Clusters episodic session logs, resolves expired and fulfilled open loops, and promotes repeated user preferences into `Beliefs & Principles`.
  - Integrates with local Ollama (`http://localhost:11434`) with deterministic heuristic fallbacks.
- **Bi-Directional Obsidian Markdown Vault Sync** (`openyantra/yantra_vault.py`):
  - `yantra vault export [dir]`: Converts Chitrapat into structured Markdown with YAML frontmatter and wikilinks.
  - `yantra vault import [dir]`: Ingests user-checked boxes (`- [x]`) and inbox notes from Obsidian back into OpenYantra.
  - `yantra vault sync [dir]`: Bi-directional synchronization.
- **Drop-in Framework Adapters** (`openyantra/adapters/`):
  - `OpenYantraChatMessageHistory` and `OpenYantraRetriever` for LangChain and LangGraph.
  - `OpenYantraCrewMemory` for multi-agent CrewAI teams.
- **FastAPI UI & Dashboard v6 Enhancements**:
  - Resolved Python 3.9 type evaluation crashes.
  - Added 1-click `🌙 Dream` and `📓 Sync Vault` buttons directly to dashboard header.
  - Fixed stat card routing (`goTo()`), enter-key submission on inbox input, and canvas fallback geometry.

---

## [5.0.0] -- 2026-05-22

### Added
- **Sutradhar Graph Layer** (`yantra_sqlite.py`): SQLite-backed relationship edges with `edges` table, bidirectional indexes, and recursive CTE traversal up to 6 hops with cycle guards
- `SyncEngine.traverse(source_type, source_id, max_hops)`: Bidirectional BFS using recursive CTE with path cycle detection
- `SyncEngine.add_edge()`, `delete_edge()`, `get_edges()`: Full CRUD for relationship edges
- `SyncEngine.infer_edges()`: Auto-edge inference on writes -- tasks linked to projects, @Name mentions linked to people
- Graph API endpoints in `yantra_ui.py`: `GET /api/graph/edges`, `POST /api/graph/edge`, `DELETE /api/graph/edge/{id}`, `GET /api/graph/traverse`
- `graph_traverse` MCP tool in `cognitive_mcp.py` for agentic graph queries
- **Sutra Context Pruning Engine** (`yantra_sutra.py`): Token-budget-aware context compiler with weighted scoring (semantic similarity, recency, importance, relation proximity)
- Context compile/preview endpoints: `POST /api/context/compile`, `GET /api/context/preview`
- Context tab in dashboard with mode presets (default, creative, analytical, conversational)
- **Setu Sync Durability**: `_sync_state` table for crash-safe reconciliation, LibreOffice lockfile detection, ODS header validation
- 1MB clipboard guard in `yantra_context.py`
- `db_engine` (SyncEngine) instantiated in `OpenYantra.__init__` for SQLite graph access

### Changed
- Dashboard read endpoints (`/api/sheet/{name}`) now prefer SQLite via `SyncEngine.read()` for 2ms query times, with ODS fallback
- Graph tab upgraded to **Sutradhar Relationship Graph** showing real edges from SQLite alongside cognitive memory connections
- Force-directed graph now renders entity-type-specific colors (Projects=teal, Tasks=purple, People=pink) with glow effects
- Version bumped to `5.0.0` across all modules: `__init__.py`, `pyproject.toml`, `core.py`, `yantra_sqlite.py`, `yantra_context.py`, `yantra_morning.py`, `yantra_ui.py`, `cognitive_mcp.py`

### Architecture
- SyncEngine extended with graph capabilities (Sutradhar): edges table with uniqueness constraints and bidirectional indexes
- Recursive CTE traversal supports forward and reverse edge walking with `instr()` cycle guard
- Auto-edge inference runs on every write via `OpenYantra.request_write()` hook

## [4.1.0] -- 2026-05-20

### Added
- Google and Apple Passkey (WebAuthn) authentication support to protect local memory dashboard
- Dense embeddings support using `sentence-transformers` for VidyaKosha hybrid semantic search
- ISO-timestamp-based `start_date` and `end_date` filtering for cognitive memories and MCP search
- Safe CLI commands: `yantra stop` and `yantra kill` to stop background processes cleanly
- Safety options to reset or clean up half-finished bootstrap runs
- Manual UI Lock button and session lock overlay screen in Web UI

### Changed
- Incremented version to v4.1.0 across codebase, website, and visual manuals
- Web UI updated with Date Range picker inputs in Memory Explorer and embedder selector dropdown in settings


---

## [4.0.0] -- 2026-05-20

### Added
- Native MCP Server Support integrating top 20 apps including OpenRouter and Gemini Spark
- ChitraGupta Agent integration with local and remote AI APIs
- Settings Dashboard in Web UI to manage AI models, API keys, OAuth, and font sizes
- Dynamic Font Scaling across all Web UI tabs
- Command-line interface availability via `openyantra.cli` entry points
- Complete codebase restructure to python standard `openyantra` package and pyproject.toml
- Revamped GitHub repository layout moving web files to `website/` for Cloudflare deployment
- Added automated SEO elements: sitemap.xml, robots.txt, manifest.json

### Changed
- Moved v3.x legacy codebase to `v3.0.1` branch. Main branch now defaults to v4.0.0
- Web UI updated with new capabilities and seamless AI Model settings
- Installation scripts updated to utilize modern CLI module

---



## [3.0.0] -- 2026-03-21

### Breaking changes
- SQLite WAL is now the operational source of truth. ODS file is the human-readable export.
- `chitrapat.ods` is no longer written on every Chitragupta commit. It is exported atomically after each write (async, off hot path).
- Direct ODS editing via LibreOffice now requires `yantra sync` to import changes back into SQLite.
- **Sort Catastrophe warning:** Sorting a single column in LibreOffice scrambles all row data. Never sort -- use `yantra open` + `yantra sync` for manual edits only.

### Added
- `yantra_sqlite.py` -- SyncEngine: SQLite WAL backend with atomic ODS export
  - 2ms writes at any row count (vs 2012ms at 5000 rows in v2.x)
  - Write idempotency via `request_id` dedup check
  - Atomic ODS export: write to `.tmp`, fsync, verify row counts against SQLite, `os.replace()`
  - `PRAGMA wal_checkpoint(TRUNCATE)` after each ODS export
  - portalocker integration: prevents concurrent file corruption
  - `import_ods()`: ingest user edits from LibreOffice back into SQLite (Dharma-Adesh flow)
- `yantra_morning.py` -- Morning Briefing
  - Surfaces open loops (importance >= 7, sorted by TTL urgency)
  - Stale project detection (no update in 7+ days)
  - Proactive suggestion: cross-references inbox items with open loops
  - Streak counter: consecutive days with at least one write
  - Past memory: random goal or belief for reflection
  - Auto-runs on first `yantra` command of the day
- `yantra_context.py` -- Copy Context
  - Formats full memory as clean Markdown block
  - Copies to clipboard automatically (pbcopy / xclip / clip)
  - Works with any web AI: Claude.ai, ChatGPT, Gemini, etc.
  - Selective section export via `--sections` flag
- `yantra sync` CLI command -- import ODS edits back to SQLite
- `yantra corrections` CLI command -- list and apply pending agent corrections
- `yantra morning` CLI command -- run morning brief on demand
- `yantra context` CLI command -- copy context to clipboard

### Changed
- `openyantra.py` VERSION: `2.8` -> `3.0.0`
- All version strings updated throughout codebase
- `build_context_markdown()` method added to `OpenYantra` class
- `morning_brief()` method added to `OpenYantra` class

### Fixed
- All em dashes removed from documentation (v2.13.0 regression cleanup)
- `--ink` token corrected to `#0a0a0b` in all screenshot HTML files
- `--dim` token corrected to `#242228` in all screenshot HTML files
- `docs/docs/visual-guide.html` broken path fixed to `visual-guide.html` in README
- Version badge corrected to current version in README, index.html, SKILL.md
- Domain count corrected to 14 in all public-facing documents
- Removed phantom commands `yantra oracle`, `yantra export` from README
- Duplicate version history entries in README removed
- `index.html` nav Docs link now points to `visual-guide.html`
- `index.html` nav now links to `openyantra-brand-manual.html`

### Architecture (Round 5 stress test, 7 models)
- 7/7 consensus: SQLite WAL as operational backend (ODS as export)
- 7/7 consensus: formal SyncEngine with Vivada conflict rules
- 7/7 consensus: write idempotency via request_id
- 6/7: atomic ODS export pattern
- 5/7: portalocker as core dependency
- 1/1 (GLM5): Sort Catastrophe warning -- critical safety note
- 1/1 (Grok): dashboard reads must come from SQLite, not ODS
- 1/1 (DeepSeek + Grok): VidyaKosha incremental_update reads from SQLite

---

## [2.13.0] -- 2026-03-21

### Added
- `visual-guide.html` -- interactive architecture diagram (dark/light mode)
- `openyantra-brand-manual.html` -- full brand identity and design system
- `assets/brand/` -- SVG logo mark, horizontal logo, minimal mark, favicon
- `assets/screenshots/` -- screenshot HTML files for web UI, CLI, banner

### Fixed
- Token alignment: `--ink #0b0b0c` -> `#0a0a0b`, `--dim #252328` -> `#242228` in index.html
- Em dashes removed from index.html (18), brand-manual.html (41), visual-guide.html (21)
- Version badge in index.html updated to v2.13.0

---

## [2.12.0] -- 2026-03-20

### Added
- `yantra_morning.py` -- Morning Briefing (stub)
- Daily Insight card at top of browser dashboard Today tab
- Streak counter
- iOS Shortcut server (`yantra shortcut`, port 7332)
- Email-to-Inbox SMTP server (`yantra mail`, port 2525)
- `yantra migrate` -- schema migration tool
- `yantra schedule` -- schedule daily digest via cron/launchd
- `yantra context` -- copy context to clipboard (stub)

---

## [2.9.0] -- 2026-03-15

### Added
- Agrasandhanī integrity check (`yantra integrity`)
- Session log archival (`yantra archive`)
- Stats tab in browser dashboard
- 7 UI screenshots

---

## [2.8.0] -- 2026-03-10

### Added
- Incremental VidyaKosha sync (O(1) per write)
- Importance-weighted retrieval (relevance x importance x recency)
- `yantra stats` command
- Admission rule refinement

---

## [2.7.0] -- 2026-03-05

### Added
- Importance-weighted retrieval in VidyaKosha
- `yantra stats` memory growth analytics

---

## [2.6.0] -- 2026-03-01

### Added
- 12-question Bootstrap interview (`yantra bootstrap`)
- First-launch onboarding tour in browser dashboard
- Brand assets rebuilt

---

## [2.5.0] -- 2026-02-20

### Added
- Today tab with one-click actions
- Timeline tab (chronological activity feed)
- Conflict Resolver tab (visual diff)
- Floating capture button (keyboard shortcut `i`)
- Mobile-responsive CSS

---

## [2.4.0] -- 2026-02-10

### Added
- Raksha security engine (`yantra_security.py`)
- Prompt injection scanner (confirmed patterns blocked)
- Agent trust tiers 0-5
- Mudra signature verification
- Quarantine sheet for blocked writes
- VidyaKosha poisoning detection
- `yantra security` command

---

## [2.3.0] -- 2026-02-01

### Added
- Self-contained installer (`install.sh` / `install.ps1`)
  - Auto-installs Python, LibreOffice, all deps
  - Creates venv, CLI, desktop shortcut
- Telegram bot (`telegram_bot.py`)
- Daily digest (`yantra_digest.py`)
- `yantra doctor` system health check

---

## [2.2.0] -- 2026-01-25

### Added
- Complete repo restored: all docs, openclaw/, examples/, references/
- `docs/DEPLOYMENT.md` -- framework integration guide
- LangChain adapter (`examples/langchain_adapter.py`)

---

## [2.1.0] -- 2026-01-15

### Added
- `📥 Inbox` sheet (Avagraha) -- quick capture without categorisation
- `✏️ Corrections` sheet (Sanshodhan) -- agent-proposed edits
- Importance column (1-10) on all sheets
- TTL_Days column on Open Loops
- Admission rules (filter noise writes)
- Belief diffing (contradiction detection)
- `memory_correction()` -- agent proposes, user approves
- Dead man's switch -- alert if Chitragupta silent > N minutes
- `route_inbox()` -- keyword-based routing
- Browser dashboard (`yantra ui`)
- Bootstrap interview (6 questions)

---

## [2.0.0] -- 2026-01-01

### Added
- VidyaKosha sidecar semantic index
- BM25 keyword index
- TF-IDF + SVD embedder (zero extra deps)
- FAISS vector index
- Hybrid retrieval: alpha x vector + (1-alpha) x BM25
- Pratibimba per-agent frozen snapshots
- `oy.search()`, `oy.search_open_loops()`, `oy.search_projects()`, `oy.search_people()`
- `oy.take_pratibimba()`, `oy.release_pratibimba()`

---

## [1.0.0] -- 2025-12-01

### Added
- Core Chitragupta pattern: single-writer LedgerAgent
- Agrasandhanī audit trail (SHA-256 signed, append-only)
- 12-sheet schema: Identity, Goals, Projects, People, Preferences, Beliefs, Tasks, Open Loops, Session Log, Agent Config, Ledger, INDEX
- WriteRequest (Karma-Lekha)
- WriteQueue / Sanchitta (crash-safe JSON queue)
- Vivada conflict detection and escalation
- Dharma-Adesh: user edits always win
- Controlled vocabulary enforcement
- `build_system_prompt_block()` -- Smarana session load
- `flush_open_loop()` -- Zeigarnik Effect implementation
- MYTHOLOGY.md, WHITEPAPER.md, PROTOCOL.md, SKILL.md
- MIT + CC0 dual license
