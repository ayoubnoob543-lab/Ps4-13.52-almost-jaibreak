from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from .memory import LocalMemory
from .models import ActionEvent, AgentState, ChatMessage, ToolResult
from .ollama import OllamaClient, OllamaError

class AgentEngine:
    def __init__(self, config: dict[str, Any], client: OllamaClient, memory: LocalMemory, tools: Any):
        self.config, self.client, self.memory, self.tools = config, client, memory, tools
        self.state = AgentState()
        self._stop = threading.Event()
        self.on_event: Callable[[ActionEvent], None] | None = None
        self.on_status: Callable[[str], None] | None = None
        self.on_confirmation: Callable[[str], bool] | None = None

    def stop(self) -> None:
        self._stop.set()
        self.state.stopped = True
        self._status("stopped")

    def reset_stop(self) -> None:
        self._stop.clear()
        self.state.stopped = False

    def _status(self, value: str) -> None:
        self.state.status = value
        if self.on_status:
            self.on_status(value)

    def _emit(self, phase: str, tool: str, args: dict[str, Any], result: ToolResult) -> None:
        event = ActionEvent(phase, tool, args, result.output, result.success)
        self.memory.record(event)
        self.state.events.append(event)
        if self.on_event:
            self.on_event(event)

    def run(self, user_text: str) -> str:
        self.reset_stop()
        user = ChatMessage("user", user_text)
        self.memory.add(user)
        self._status("observing")
        if not self.client.is_available():
            return "No encuentro Ollama en ejecución. Inícialo con `ollama serve` y vuelve a intentarlo."
        catalog = self.tools.catalog()
        max_steps = int(self.config["agent"].get("max_steps", 12))
        last_observation = ""
        for step in range(1, max_steps + 1):
            if self._stop.is_set():
                return "Ejecución detenida por el usuario."
            self.state.step = step
            self._status("thinking")
            context = list(self.memory.messages)
            if last_observation:
                context.append(ChatMessage("tool", f"Resultado de la observación/verificación anterior:\n{last_observation}"))
            try:
                decision = self.client.decide(context, catalog)
            except OllamaError as exc:
                return str(exc)
            if decision.get("kind") != "action":
                answer = str(decision.get("message", "No tengo una respuesta."))
                self.memory.add(ChatMessage("assistant", answer))
                self._status("idle")
                return answer
            tool_name = str(decision.get("tool", ""))
            args = decision.get("arguments") or {}
            if not self.tools.exists(tool_name):
                last_observation = f"Herramienta inexistente: {tool_name}"
                self._emit("ACT", tool_name, args, ToolResult(False, last_observation))
                continue
            description = self.tools.confirmation_message(tool_name, args)
            if description and not self.config["agent"].get("autonomous_mode", False):
                approved = self.on_confirmation(description) if self.on_confirmation else False
                if not approved:
                    return "Acción cancelada: no se concedió confirmación."
            self._status("executing")
            result = self.tools.execute(tool_name, args, self._stop)
            self._emit("ACT", tool_name, args, result)
            if result.success:
                if result.data.get("path"):
                    self._status("observing")
                    try:
                        vision = self.client.chat([ChatMessage("user", "Describe de forma concisa lo visible en esta captura y destaca elementos relevantes para la tarea.", [result.data["path"]])], vision=True)
                        last_observation = vision
                        self._emit("OBSERVE", "vision", {"image": result.data["path"]}, ToolResult(True, vision))
                    except OllamaError as exc:
                        last_observation = f"Captura disponible, pero la visión no está disponible: {exc}"
                self._status("verifying")
                verified = self.tools.verify(tool_name, args, result)
                self._emit("VERIFY", tool_name, args, verified)
                last_observation = (last_observation + "\nVerificación: " + verified.output).strip()
                if verified.success and tool_name in {"respond", "open_app", "close_app", "write_file", "delete_file", "run_powershell", "git", "type_text", "click", "key_press"}:
                    self.memory.add(ChatMessage("assistant", verified.output))
                    self._status("idle")
                    return verified.output
            else:
                self._status("repairing")
                last_observation = f"La acción falló: {result.output}. Revisa el error y repara si es posible."
        self._status("idle")
        answer = f"He alcanzado el límite de {max_steps} pasos. Última observación: {last_observation}"
        self.memory.add(ChatMessage("assistant", answer))
        return answer
