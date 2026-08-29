from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ActionEvent, ChatMessage

class LocalMemory:
    def __init__(self, data_dir: Path, history_limit: int = 80):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = data_dir / "conversation.json"
        self.actions_path = data_dir / "actions.jsonl"
        self.history_limit = history_limit
        self.messages: list[ChatMessage] = self._load_messages()

    def _load_messages(self) -> list[ChatMessage]:
        if not self.history_path.exists():
            return []
        try:
            rows = json.loads(self.history_path.read_text(encoding="utf-8"))
            return [ChatMessage(**row) for row in rows[-self.history_limit:]]
        except (OSError, ValueError, TypeError):
            return []

    def add(self, message: ChatMessage) -> None:
        self.messages.append(message)
        self.messages = self.messages[-self.history_limit:]
        self.history_path.write_text(json.dumps([m.__dict__ for m in self.messages], ensure_ascii=False, indent=2), encoding="utf-8")

    def record(self, event: ActionEvent) -> None:
        with self.actions_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.__dict__, ensure_ascii=False) + "\n")

    def recent_actions(self, limit: int = 30) -> list[dict[str, Any]]:
        if not self.actions_path.exists():
            return []
        lines = self.actions_path.read_text(encoding="utf-8").splitlines()
        result = []
        for line in lines[-limit:]:
            try:
                result.append(json.loads(line))
            except ValueError:
                continue
        return result

    def clear(self) -> None:
        self.messages = []
        if self.history_path.exists():
            self.history_path.unlink()
