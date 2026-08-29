import json
from pathlib import Path

from agent.memory import LocalMemory
from agent.models import ChatMessage
from computer.tools import DesktopTools

BASE = Path(__file__).resolve().parents[1]

def test_config_is_valid():
    data = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
    assert data["ollama"]["base_url"].startswith("http")
    assert data["agent"]["max_steps"] > 0

def test_memory_roundtrip(tmp_path):
    memory = LocalMemory(tmp_path)
    memory.add(ChatMessage("user", "hola"))
    loaded = LocalMemory(tmp_path)
    assert loaded.messages[0].content == "hola"

def test_tool_catalog_and_safe_path(tmp_path):
    tools = DesktopTools({"security": {}}, tmp_path)
    assert tools.exists("screenshot")
    assert "write_file" in tools.catalog()
