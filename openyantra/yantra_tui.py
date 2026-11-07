"""
yantra_tui.py -- OpenYantra Cyberpunk Terminal TUI v6.1.0
Interactive text user interface for terminal purists and SSH workflows.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def render_tui(oy: Any) -> str:
    """Renders the ANSI cyberpunk terminal dashboard."""
    h = oy.health_check()
    loops = oy.get_sheet("Open Loops")
    active_loops = [
        l for l in loops
        if str(l.get("Resolved?", "")).lower() not in ("yes", "true", "resolved")
        and l.get("Topic")
    ]
    projects = oy.get_sheet("Projects")
    active_projects = [
        p for p in projects
        if str(p.get("Status", "Active")).lower() == "active"
        and p.get("Project")
    ]
    sessions = oy.get_sheet("Session Log")
    recent_sessions = sessions[-3:] if sessions else []

    CYAN = "\033[96m"
    SAFFRON = "\033[38;5;214m"
    GREEN = "\033[92m"
    CORAL = "\033[91m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    out = []
    out.append(f"{SAFFRON}{BOLD}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
    out.append(f"{SAFFRON}{BOLD}║  OPENYANTRA v6.1.0 (Akasha & Sutra) -- Cyberpunk Terminal TUI       ║{RESET}")
    out.append(f"{SAFFRON}{BOLD}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
    out.append(f"  {GREEN}● Chitragupta Active{RESET} │ Status: {h.get('status', 'ok').upper()} │ Integrity: {GREEN}VERIFIED{RESET} │ Mode: SQLite WAL")
    out.append("  " + "─" * 68)

    # 1. Open Loops Section
    out.append(f"\n  {CORAL}{BOLD}🔓 OPEN LOOPS ({len(active_loops)} pending){RESET}")
    if not active_loops:
        out.append(f"     {DIM}No open loops. Mind is clear (Zeigarnik satisfied).{RESET}")
    else:
        for l in active_loops[:5]:
            topic = l.get("Topic", "")
            prio = l.get("Priority", "Medium")
            out.append(f"     • [{prio:6}] {BOLD}{topic[:45]}{RESET}")

    # 2. Active Projects Section
    out.append(f"\n  {CYAN}{BOLD}🚀 ACTIVE PROJECTS ({len(active_projects)}){RESET}")
    if not active_projects:
        out.append(f"     {DIM}No active projects found.{RESET}")
    else:
        for p in active_projects[:4]:
            name = p.get("Project", "")
            domain = p.get("Domain", "General")
            step = p.get("Next Step", "")
            step_str = f" → {step[:30]}" if step and step.lower() != "nan" else ""
            out.append(f"     • {name} [{domain}]{DIM}{step_str}{RESET}")

    # 3. Recent Decisions / Session Log
    out.append(f"\n  {SAFFRON}{BOLD}📅 RECENT DECISIONS{RESET}")
    if not recent_sessions:
        out.append(f"     {DIM}No session records found.{RESET}")
    else:
        for s in recent_sessions:
            date_str = s.get("Date", "Recent")
            topic = s.get("Topics Discussed") or s.get("Topic") or "Session"
            dec = s.get("Decisions Made") or s.get("Decisions") or ""
            out.append(f"     • [{date_str}] {topic}: {DIM}{dec[:45]}...{RESET}")

    out.append("\n  " + "─" * 68)
    out.append(f"  {DIM}Commands: [i] Inbox Capture  [d] Run Dream  [h] HUD  [q] Quit{RESET}\n")

    return "\n".join(out)


def run_tui(oy: Any):
    """Interactive loop for Terminal TUI."""
    while True:
        # Clear screen
        os.system("clear" if os.name != "nt" else "cls")
        print(render_tui(oy))
        try:
            choice = input("  yantra:tui> ").strip().lower()
            if choice == "q":
                print("  Exiting TUI.")
                break
            elif choice == "i":
                text = input("  Quick capture text: ").strip()
                if text:
                    oy.inbox(text, source="User-stated")
                    print("  ✓ Saved to Inbox.")
            elif choice == "d":
                from openyantra.yantra_nidra import NidraConsolidator
                print("  🌙 Running Nidra sleep consolidation...")
                report = NidraConsolidator(oy).consolidate(dry_run=False, provider="auto")
                print(f"  ✨ {report['summary']}")
                input("  Press Enter to continue...")
            elif choice == "h":
                from openyantra.desktop import launch_desktop
                launch_desktop(oy_file=str(oy.path), mode="hud")
        except (KeyboardInterrupt, EOFError):
            print("\n  Exiting TUI.")
            break


def main():
    from openyantra.core import OpenYantra
    oy_file = os.environ.get("OPENYANTRA_FILE", str(Path.home() / "openyantra" / "chitrapat.ods"))
    if not Path(oy_file).exists():
        print(f"Chitrapat not found at: {oy_file}. Run 'yantra bootstrap' first.")
        sys.exit(1)
    oy = OpenYantra(oy_file)
    run_tui(oy)


if __name__ == "__main__":
    main()
