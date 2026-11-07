import json
import os
import tempfile
from pathlib import Path
import pytest

from openyantra.mcp_setup import setup_mcp_config, detect_client_configs

def test_setup_mcp_config_creates_new():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Path(tmpdir) / "claude_desktop_config.json"
        res = setup_mcp_config(
            config_path=cfg,
            python_path="/mock/bin/python",
            oy_file="/mock/chitrapat.ods"
        )
        assert res["status"] == "created"
        assert cfg.exists()
        
        with open(cfg, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        assert "mcpServers" in data
        assert "openyantra" in data["mcpServers"]
        server = data["mcpServers"]["openyantra"]
        assert server["command"] == "/mock/bin/python"
        assert "--file" in server["args"]
        assert "/mock/chitrapat.ods" in server["args"]

def test_setup_mcp_config_preserves_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Path(tmpdir) / "claude_desktop_config.json"
        initial = {
            "mcpServers": {
                "sqlite": {
                    "command": "uvx",
                    "args": ["mcp-server-sqlite"]
                }
            }
        }
        with open(cfg, "w", encoding="utf-8") as f:
            json.dump(initial, f)
            
        res = setup_mcp_config(
            config_path=cfg,
            python_path="/mock/bin/python",
            oy_file="/mock/chitrapat.ods"
        )
        assert res["status"] == "updated"
        
        # Verify backup was created
        bak = cfg.with_suffix(".json.bak")
        assert bak.exists()
        
        with open(cfg, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        assert "sqlite" in data["mcpServers"]
        assert "openyantra" in data["mcpServers"]

def test_detect_client_configs():
    configs = detect_client_configs()
    assert isinstance(configs, dict)
    assert "claude" in configs
    assert "cursor" in configs
