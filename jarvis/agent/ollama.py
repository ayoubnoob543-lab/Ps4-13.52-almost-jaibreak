from __future__ import annotations

import base64
import json
from typing import Any

import requests

from .models import ChatMessage

class OllamaError(RuntimeError):
    pass

class OllamaClient:
    def __init__(self, config: dict[str, Any]):
        self.base_url = config["ollama"]["base_url"].rstrip("/")
        self.model = config["ollama"]["model"]
        self.vision_model = config["ollama"].get("vision_model", self.model)
        self.timeout = int(config["ollama"].get("timeout_seconds", 120))
        self.temperature = float(config["ollama"].get("temperature", 0.2))

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.ok
        except requests.RequestException:
            return False

    def models(self) -> list[str]:
        response = requests.get(f"{self.base_url}/api/tags", timeout=10)
        response.raise_for_status()
        return [m.get("name", "") for m in response.json().get("models", [])]

    def chat(self, messages: list[ChatMessage], *, vision: bool = False, json_mode: bool = False) -> str:
        payload_messages = []
        for msg in messages:
            item: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.images:
                item["images"] = [base64.b64encode(open(p, "rb").read()).decode("ascii") for p in msg.images]
            payload_messages.append(item)
        payload: dict[str, Any] = {
            "model": self.vision_model if vision else self.model,
            "messages": payload_messages,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if json_mode:
            payload["format"] = "json"
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
            response.raise_for_status()
            body = response.json()
            return body.get("message", {}).get("content", "").strip()
        except (requests.RequestException, ValueError) as exc:
            raise OllamaError(f"No se pudo comunicar con Ollama: {exc}") from exc

    def decide(self, messages: list[ChatMessage], tool_catalog: str) -> dict[str, Any]:
        instruction = ChatMessage("system", f"""Eres el motor de decisiones de JARVIS. Debes elegir entre responder o ejecutar UNA herramienta.\nHerramientas disponibles:\n{tool_catalog}\nResponde únicamente JSON válido con esta forma: {{\"kind\":\"respond|action\",\"message\":\"...\",\"tool\":\"nombre o null\",\"arguments\":{{}},\"reasoning\":\"breve\"}}. No inventes herramientas. Si falta información, pide aclaración con kind=respond.""")
        raw = self.chat([instruction, *messages[-20:]], json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start, end = raw.find("{"), raw.rfind("}")
            if start >= 0 and end > start:
                return json.loads(raw[start:end + 1])
            return {"kind": "respond", "message": raw, "tool": None, "arguments": {}, "reasoning": "fallback"}
