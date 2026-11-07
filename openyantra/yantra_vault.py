"""
yantra_vault.py -- Bi-Directional Obsidian Markdown Vault Synchronizer v6.0
Exports OpenYantra memory sheets into an elegant Obsidian vault with YAML frontmatter,
wikilinks, and task checklists; parses changes made in Obsidian and syncs them back.
"""

from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class VaultSync:
    """
    Manages bi-directional synchronization between OpenYantra (Chitrapat) and an Obsidian Vault.
    """

    def __init__(self, oy: Any, vault_dir: str | Path):
        self.oy = oy
        self.vault_dir = self._checked_dir(vault_dir)

    @staticmethod
    def _checked_dir(vault_dir: str | Path) -> Path:
        """Resolve the vault path and keep it inside an allowed root.

        Allowed roots: the user's home, the system temp dir, and any path listed
        in OPENYANTRA_VAULT_ROOT (os.pathsep separated). Stops a request from
        pointing the vault at system or other users' directories.
        """
        target = Path(vault_dir).expanduser().resolve()
        roots = [Path.home().resolve(), Path(tempfile.gettempdir()).resolve()]
        for extra in os.environ.get("OPENYANTRA_VAULT_ROOT", "").split(os.pathsep):
            if extra.strip():
                roots.append(Path(extra).expanduser().resolve())
        for root in roots:
            try:
                target.relative_to(root)
                return target
            except ValueError:
                continue
        raise ValueError("vault path must be inside your home directory "
                         "(or a root listed in OPENYANTRA_VAULT_ROOT)")

    def export_vault(self) -> Dict[str, Any]:
        """
        Exports all key knowledge domains into structured Markdown files with YAML frontmatter.
        """
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        (self.vault_dir / "Projects").mkdir(exist_ok=True)
        (self.vault_dir / "People").mkdir(exist_ok=True)
        (self.vault_dir / "Sessions").mkdir(exist_ok=True)

        exported_files = []

        # 1. Identity.md
        identity_rows = self.oy.get_sheet("Identity")
        id_lines = ["---", "type: identity", f"exported_at: {datetime.now(timezone.utc).isoformat()}", "---", "# Identity & Core Persona\n"]
        for row in identity_rows:
            attr = row.get("Attribute") or row.get("Key") or ""
            val = row.get("Value") or ""
            if attr:
                id_lines.append(f"- **{attr}**: {val}")
        id_path = self.vault_dir / "Identity.md"
        with open(id_path, "w", encoding="utf-8") as f:
            f.write("\n".join(id_lines) + "\n")
        exported_files.append(str(id_path))

        # 2. Beliefs.md
        beliefs_rows = self.oy.get_sheet("Beliefs & Principles")
        b_lines = ["---", "type: beliefs", f"exported_at: {datetime.now(timezone.utc).isoformat()}", "---", "# Beliefs & Principles\n"]
        for b in beliefs_rows:
            stmt = b.get("Belief / Principle") or ""
            if not stmt or str(stmt).lower() == "nan":
                continue
            domain = b.get("Domain", "General")
            conf = b.get("Confidence", "High")
            notes = b.get("Notes", "")
            b_lines.append(f"### {stmt}")
            b_lines.append(f"- **Domain**: {domain} | **Confidence**: {conf}")
            if notes and str(notes).lower() != "nan":
                b_lines.append(f"- *Notes*: {notes}")
            b_lines.append("")
        b_path = self.vault_dir / "Beliefs.md"
        with open(b_path, "w", encoding="utf-8") as f:
            f.write("\n".join(b_lines) + "\n")
        exported_files.append(str(b_path))

        # 3. Open Loops.md
        loops_rows = self.oy.get_sheet("Open Loops")
        l_lines = ["---", "type: open_loops", f"exported_at: {datetime.now(timezone.utc).isoformat()}", "---", "# Open Loops & Pending Queries\n"]
        l_lines.append("> Check off any item (`- [x]`) in Obsidian and run `yantra vault import` to resolve it automatically.\n")
        for loop in loops_rows:
            topic = str(loop.get("Topic", "")).strip()
            if not topic or topic.lower() == "nan":
                continue
            is_resolved = str(loop.get("Resolved?", "")).strip().lower() in ("yes", "true")
            mark = "x" if is_resolved else " "
            prio = loop.get("Priority", "Medium")
            ctx = loop.get("Context / What's Unresolved", "")
            proj = loop.get("Related Project", "")
            proj_link = f" [[Projects/{proj}]]" if proj and str(proj).lower() != "nan" else ""
            l_lines.append(f"- [{mark}] **{topic}** (Priority: {prio}){proj_link}")
            if ctx and str(ctx).lower() != "nan":
                l_lines.append(f"  - Context: {ctx}")
        l_path = self.vault_dir / "Open Loops.md"
        with open(l_path, "w", encoding="utf-8") as f:
            f.write("\n".join(l_lines) + "\n")
        exported_files.append(str(l_path))

        # 4. Projects/*.md
        proj_rows = self.oy.get_sheet("Projects")
        for proj in proj_rows:
            name = str(proj.get("Project", "")).strip()
            if not name or name.lower() == "nan":
                continue
            safe_name = re.sub(r'[\/:*?"<>|]', "_", name)
            status = proj.get("Status", "Active")
            domain = proj.get("Domain", "")
            summary = proj.get("Summary", "")
            p_lines = [
                "---",
                "type: project",
                f"project: \"{name}\"",
                f"status: \"{status}\"",
                f"domain: \"{domain}\"",
                "---",
                f"# Project: {name}\n",
                f"**Status**: `{status}` | **Domain**: {domain}\n",
                f"## Overview\n{summary}\n" if summary else "",
                "## Related Notes\n- See also: [[Open Loops]], [[Identity]]\n"
            ]
            proj_file = self.vault_dir / "Projects" / f"{safe_name}.md"
            with open(proj_file, "w", encoding="utf-8") as f:
                f.write("\n".join(p_lines) + "\n")
            exported_files.append(str(proj_file))

        # 5. People/*.md
        people_rows = self.oy.get_sheet("People")
        for p in people_rows:
            name = str(p.get("Name", "")).strip()
            if not name or name.lower() == "nan":
                continue
            safe_name = re.sub(r'[\/:*?"<>|]', "_", name)
            rel = p.get("Relationship", "")
            ctx = p.get("Context", "")
            notes = p.get("Notes", "")
            p_lines = [
                "---",
                "type: person",
                f"name: \"{name}\"",
                f"relationship: \"{rel}\"",
                "---",
                f"# Person: {name}\n",
                f"**Relationship**: {rel}\n",
                f"## Context\n{ctx}\n" if ctx else "",
                f"## Notes\n{notes}\n" if notes else ""
            ]
            person_file = self.vault_dir / "People" / f"{safe_name}.md"
            with open(person_file, "w", encoding="utf-8") as f:
                f.write("\n".join(p_lines) + "\n")
            exported_files.append(str(person_file))

        return {
            "status": "success",
            "vault_dir": str(self.vault_dir),
            "files_exported": len(exported_files)
        }

    def import_vault(self) -> Dict[str, Any]:
        """
        Parses modified Markdown files in the Obsidian vault and syncs updates back to OpenYantra.
        Specifically handles:
        - Resolving checked open loops (`- [x] **Topic**`)
        - Ingesting newly added unchecked open loops (`- [ ] New loop`)
        """
        if not self.vault_dir.exists():
            return {"status": "error", "message": f"Vault dir {self.vault_dir} not found"}

        loops_resolved = []
        new_loops_created = []

        # 1. Parse Open Loops.md
        loops_path = self.vault_dir / "Open Loops.md"
        if loops_path.exists():
            with open(loops_path, "r", encoding="utf-8") as f:
                content = f.read()

            existing_loops = self.oy.get_sheet("Open Loops")
            loop_map = {
                str(l.get("Topic", "")).strip().lower(): l
                for l in existing_loops if l.get("Topic")
            }

            # Find all checklist items: - [x] **Topic** or - [ ] Topic
            pattern = re.compile(r"^\s*-\s*\[([ xX])\]\s+(?:\*\*(.*?)\*\*|(.*?))(?:\s+\(Priority:.*?\))?(?:\s+\[\[.*?\]\])?\s*$", re.MULTILINE)
            for match in pattern.finditer(content):
                checked = match.group(1).lower() == "x"
                topic = (match.group(2) or match.group(3) or "").strip()
                if not topic or topic.lower() == "nan":
                    continue

                topic_key = topic.lower()
                if topic_key in loop_map:
                    sheet_resolved = str(loop_map[topic_key].get("Resolved?", "")).strip().lower() in ("yes", "true")
                    if checked and not sheet_resolved:
                        # User checked it off in Obsidian -> resolve in OpenYantra
                        try:
                            self.oy.resolve_open_loop(topic, resolution="Checked off in Obsidian Vault")
                            loops_resolved.append(topic)
                        except Exception:
                            pass
                elif not checked:
                    # New unchecked item added by user in Obsidian
                    try:
                        self.oy.flush_open_loop(topic=topic, context="Imported from Obsidian Vault Open Loops.md")
                        new_loops_created.append(topic)
                    except Exception:
                        pass

        # 2. Check for an optional Inbox.md in the vault
        inbox_imported = []
        inbox_path = self.vault_dir / "Inbox.md"
        if inbox_path.exists():
            with open(inbox_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                clean_line = line.strip().lstrip("-* ").strip()
                if clean_line and not clean_line.startswith("#") and not clean_line.startswith("---"):
                    try:
                        self.oy.inbox(clean_line, source="User-stated")
                        inbox_imported.append(clean_line)
                    except Exception:
                        pass


        return {
            "status": "success",
            "vault_dir": str(self.vault_dir),
            "loops_resolved": loops_resolved,
            "new_loops_created": new_loops_created,
            "inbox_items_imported": inbox_imported
        }
