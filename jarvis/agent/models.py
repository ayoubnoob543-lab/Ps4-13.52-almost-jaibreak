from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]

@dataclass
class ChatMessage:
    role: Role
    content: str
    images: list[str] = field(default_factory=list)
    name: str | None = None

@dataclass
class ActionEvent:
    phase: str
    tool: str
    arguments: dict[str, Any]
    result: str
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

@dataclass
class ToolResult:
    success: bool
    output: str
    data: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False

@dataclass
class AgentDecision:
    kind: Literal["respond", "action"]
    message: str = ""
    tool: str | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

@dataclass
class AgentState:
    status: str = "idle"
    step: int = 0
    stopped: bool = False
    events: list[ActionEvent] = field(default_factory=list)
