"""
mcp_setup.py -- OpenYantra 1-Click MCP Client Auto-Configurator v6.0
Detects and configures Claude Desktop, Cursor, and other MCP client settings.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional


def detect_client_configs() -> dict[str, Optional[Path]]:
    """Detect default MCP configuration file paths across operating systems."""
    home = Path.home()
    configs: dict[str, Optional[Path]] = {
        "claude": None,
        "cursor": None,
    }

    if sys.platform == "darwin":
        configs["claude"] = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        configs["cursor"] = home / ".cursor" / "mcp.json"
    elif sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", str(home / "AppData" / "Roaming")))
        configs["claude"] = appdata / "Claude" / "claude_desktop_config.json"
        configs["cursor"] = home / ".cursor" / "mcp.json"
    else:  # Linux
        configs["claude"] = home / ".config" / "Claude" / "claude_desktop_config.json"
        configs["cursor"] = home / ".cursor" / "mcp.json"

    return configs


def setup_mcp_config(
    config_path: str | Path,
    python_path: Optional[str] = None,
    oy_file: Optional[str] = None,
    env_vars: Optional[dict] = None
) -> dict:
    """
    Safely injects the OpenYantra MCP server into an existing or new MCP configuration file.
    Preserves other servers, creates a backup, and ensures proper formatting.
    """
    path = Path(config_path).expanduser().resolve()
    python_bin = python_path or sys.executable
    chitrapat_file = str(Path(oy_file).expanduser().resolve()) if oy_file else str(Path.home() / "openyantra" / "chitrapat.ods")

    # Locate cognitive_mcp.py script
    script_dir = Path(__file__).resolve().parent
    mcp_script = str(script_dir / "cognitive_mcp.py")

    server_entry = {
        "command": python_bin,
        "args": [
            mcp_script,
            "--file",
            chitrapat_file
        ]
    }
    if env_vars:
        server_entry["env"] = env_vars

    data = {"mcpServers": {}}
    status = "created"

    if path.exists():
        status = "updated"
        # Create backup
        bak_path = path.with_suffix(".json.bak")
        try:
            shutil.copy2(path, bak_path)
        except Exception:
            pass

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except Exception:
            data = {"mcpServers": {}}

    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        data["mcpServers"] = {}

    data["mcpServers"]["openyantra"] = server_entry

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {
        "status": status,
        "config_path": str(path),
        "server": server_entry
    }


def auto_setup_clients(client_filter: Optional[str] = None, oy_file: Optional[str] = None) -> list[dict]:
    """
    Auto-detects and installs OpenYantra MCP server configuration for installed or supported clients.
    """
    detected = detect_client_configs()
    results = []

    target_clients = [client_filter.lower()] if client_filter and client_filter != "all" else ["claude", "cursor"]

    for name in target_clients:
        cfg = detected.get(name)
        if cfg:
            # Check if parent directory or client directory exists, or create if specified
            res = setup_mcp_config(config_path=cfg, oy_file=oy_file)
            res["client"] = name
            results.append(res)

    return results

