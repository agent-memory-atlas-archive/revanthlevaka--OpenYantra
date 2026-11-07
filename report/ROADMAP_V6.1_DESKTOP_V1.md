# OpenYantra v6.1 & Desktop App v1.0 — Master Specification & Phased Plan

**Date:** November 7, 2026  
**Status:** In Execution  
**Targets:**  
- **OpenYantra Engine / CLI:** Version 6.1.0 ("Akasha & Sutra")  
- **OpenYantra Desktop App:** Version 1.0.0 ("Yantra HUD & Tray")  
- **Cursor & VS Code Extension:** Version 1.0.0  

---

## 1. Executive Summary

This plan outlines the evolution of OpenYantra from a CLI/browser-based system into an **omnipresent, keyboard-driven native HUD** that lives directly over Cursor, VS Code, and terminal workflows.

### Core Deliverables:
1. **OpenYantra Core v6.1.0 ("Akasha & Sutra"):**
   - Git commit post-hook auto-ingest (`yantra hook install`).
   - Local offline Whisper voice capture (`yantra whisper`).
   - Cyberpunk terminal TUI (`yantra tui`).
2. **OpenYantra Desktop v1.0.0 ("Yantra HUD & Tray"):**
   - Ultra-lightweight native OS Webview (< 15MB binary, zero Electron bloat).
   - Global Hotkey Floating HUD (`Cmd+Shift+Y` / `Ctrl+Shift+Y`).
   - System Tray / Menu Bar status daemon with discrete indicators.
3. **Cursor & VS Code Extension v1.0.0:**
   - Sidebar panel for loops, projects, and beliefs.
   - 1-click context injection into Cursor Composer and Copilot.

---

## 2. Phased Roadmap

| Phase | Milestone | Key Deliverables |
| :--- | :--- | :--- |
| **Phase 1** | **OpenYantra Core v6.1.0** | Git post-commit hook, local Whisper audio transcribe, terminal TUI mode. |
| **Phase 2** | **Desktop v1.0 (Native Python + Webview)** | `yantra desktop` command, `pystray` menu bar, `Cmd+Shift+Y` floating HUD modal. |
| **Phase 3** | **Desktop v1.0 (Tauri Standalone)** | Standalone `.dmg`, `.msi`, `.AppImage` packaging with instant startup. |
| **Phase 4** | **IDE Integration** | VS Code / Cursor marketplace extension for sidebar recall and Composer injection. |
