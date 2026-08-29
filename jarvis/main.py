from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from agent.core import AgentEngine
from agent.memory import LocalMemory
from agent.ollama import OllamaClient
from computer.tools import DesktopTools
from ui.main_window import FirstRunDialog, MainWindow
from voice.voice import VoiceService

BASE = Path(__file__).resolve().parent
CONFIG_PATH = BASE / "config.json"

def load_config() -> dict:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config.setdefault("agent", {})["workspace_root"] = config["agent"].get("workspace_root") or str(BASE)
    return config

def main() -> int:
    config = load_config()
    app = QApplication(sys.argv)
    app.setApplicationName(config.get("assistant_name", "JARVIS"))
    if not config.get("user_name"):
        dialog = FirstRunDialog()
        if dialog.exec() != FirstRunDialog.Accepted: return 0
        config["user_name"] = dialog.user.text().strip() or "usuario"
        config["assistant_name"] = dialog.assistant.text().strip() or "JARVIS"
        CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    memory = LocalMemory(BASE / "data", int(config["agent"].get("history_limit", 80)))
    tools = DesktopTools(config, Path(config["agent"]["workspace_root"]))
    engine = AgentEngine(config, OllamaClient(config), memory, tools)
    voice = VoiceService(config)
    window = MainWindow(config, engine, voice, CONFIG_PATH)
    if config.get("ui", {}).get("start_maximized", True): window.showMaximized()
    else: window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
