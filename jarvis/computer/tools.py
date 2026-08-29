from __future__ import annotations

import os
import re
import subprocess
import threading
from pathlib import Path
from typing import Any

import psutil

try:
    import pyautogui
except Exception:
    pyautogui = None
try:
    from mss import mss
except ImportError:
    mss = None

from agent.models import ToolResult

class DesktopTools:
    def __init__(self, config: dict[str, Any], root: Path):
        self.config, self.root = config, root
        self.root.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir = root / "data" / "screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self._specs = {
            "respond": "Responder al usuario. argumentos: {message}",
            "screenshot": "Capturar pantalla. argumentos: {monitor: opcional}",
            "move_mouse": "Mover ratón. argumentos: {x, y, duration: opcional}",
            "click": "Hacer clic. argumentos: {x: opcional, y: opcional, button: left|right|middle, clicks: 1|2}",
            "scroll": "Desplazar. argumentos: {clicks, x: opcional, y: opcional}",
            "type_text": "Escribir texto. argumentos: {text, interval: opcional}",
            "key_press": "Pulsar tecla o combinación. argumentos: {keys: string o lista}",
            "open_app": "Abrir aplicación/URL. argumentos: {target}",
            "close_app": "Cerrar procesos por nombre. argumentos: {name}",
            "run_powershell": "Ejecutar PowerShell. argumentos: {command, cwd: opcional}",
            "read_file": "Leer archivo de texto. argumentos: {path}",
            "write_file": "Crear o sobrescribir archivo. argumentos: {path, content}",
            "delete_file": "Eliminar archivo o carpeta. argumentos: {path}",
            "list_directory": "Listar carpeta. argumentos: {path: opcional}",
            "git": "Ejecutar Git en un proyecto. argumentos: {command, cwd}",
        }

    def catalog(self) -> str:
        return "\n".join(f"- {name}: {desc}" for name, desc in self._specs.items())

    def exists(self, name: str) -> bool:
        return name in self._specs

    def confirmation_message(self, name: str, args: dict[str, Any]) -> str | None:
        security = self.config.get("security", {})
        if name == "delete_file" and security.get("confirm_file_delete", True):
            return f"Confirmar eliminación de: {args.get('path', '')}"
        if name in {"run_powershell", "git"} and security.get("confirm_dangerous_commands", True):
            command = str(args.get("command", ""))
            blocked = security.get("blocked_commands", [])
            if any(token.lower() in command.lower() for token in blocked) or name == "run_powershell":
                return f"Confirmar ejecución del comando: {command}"
        if name in {"click", "type_text", "key_press", "close_app"} and security.get("confirm_sensitive_actions", True):
            return f"Confirmar acción de control del equipo: {name} {args}"
        return None

    def _safe_path(self, raw: str) -> Path:
        path = Path(os.path.expandvars(os.path.expanduser(raw)))
        if not path.is_absolute():
            path = self.root / path
        return path.resolve()

    def execute(self, name: str, args: dict[str, Any], stop: threading.Event) -> ToolResult:
        try:
            if stop.is_set(): return ToolResult(False, "Detenido")
            if name == "respond": return ToolResult(True, str(args.get("message", "")))
            if name == "screenshot": return self._screenshot(args)
            if name == "move_mouse":
                if pyautogui is None: return ToolResult(False, "pyautogui no está instalado")
                pyautogui.moveTo(int(args["x"]), int(args["y"]), duration=float(args.get("duration", .2)))
                return ToolResult(True, f"Ratón movido a ({args['x']}, {args['y']})")
            if name == "click":
                if pyautogui is None: return ToolResult(False, "pyautogui no está instalado")
                if args.get("x") is not None: pyautogui.moveTo(int(args["x"]), int(args["y"]))
                pyautogui.click(button=args.get("button", "left"), clicks=int(args.get("clicks", 1)), interval=.12)
                return ToolResult(True, "Clic realizado")
            if name == "scroll":
                if pyautogui is None: return ToolResult(False, "pyautogui no está instalado")
                if args.get("x") is not None: pyautogui.moveTo(int(args["x"]), int(args["y"]))
                pyautogui.scroll(int(args.get("clicks", 1)))
                return ToolResult(True, "Scroll realizado")
            if name == "type_text":
                if pyautogui is None: return ToolResult(False, "pyautogui no está instalado")
                pyautogui.write(str(args.get("text", "")), interval=float(args.get("interval", .01)))
                return ToolResult(True, "Texto escrito")
            if name == "key_press":
                if pyautogui is None: return ToolResult(False, "pyautogui no está instalado")
                keys = args.get("keys", [])
                keys = [keys] if isinstance(keys, str) else keys
                pyautogui.hotkey(*keys) if len(keys) > 1 else pyautogui.press(keys[0])
                return ToolResult(True, f"Tecla/combinación pulsada: {keys}")
            if name == "open_app":
                subprocess.Popen(str(args["target"]), shell=True)
                return ToolResult(True, f"Abierto: {args['target']}")
            if name == "close_app":
                needle = str(args["name"]).lower(); closed = []
                for proc in psutil.process_iter(["pid", "name"]):
                    if needle in (proc.info.get("name") or "").lower():
                        proc.terminate(); closed.append(proc.info["name"])
                return ToolResult(True, f"Procesos cerrados: {closed or 'ninguno'}")
            if name == "run_powershell": return self._command(args, "powershell.exe")
            if name == "git": return self._git(args)
            if name == "read_file":
                p = self._safe_path(str(args["path"])); return ToolResult(True, p.read_text(encoding="utf-8"), {"path": str(p)})
            if name == "write_file":
                p = self._safe_path(str(args["path"])); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(str(args.get("content", "")), encoding="utf-8"); return ToolResult(True, f"Archivo escrito: {p}")
            if name == "delete_file":
                p = self._safe_path(str(args["path"]));
                if p.is_dir():
                    import shutil; shutil.rmtree(p)
                else: p.unlink()
                return ToolResult(True, f"Eliminado: {p}")
            if name == "list_directory":
                p = self._safe_path(str(args.get("path", "."))); rows = [f"{'DIR' if x.is_dir() else 'FILE'} {x.name}" for x in sorted(p.iterdir())]; return ToolResult(True, "\n".join(rows))
            return ToolResult(False, f"Herramienta no implementada: {name}")
        except Exception as exc:
            return ToolResult(False, f"{type(exc).__name__}: {exc}")

    def _screenshot(self, args: dict[str, Any]) -> ToolResult:
        if mss is None: return ToolResult(False, "mss no está instalado")
        path = self.screenshot_dir / "latest.png"
        with mss() as shot:
            monitor = int(args.get("monitor", 1)); shot.shot(mon=monitor, output=str(path))
        return ToolResult(True, f"Captura guardada en {path}", {"path": str(path)})

    def _command(self, args: dict[str, Any], executable: str) -> ToolResult:
        command = str(args.get("command", "")); cwd = self._safe_path(str(args.get("cwd", ".")))
        result = subprocess.run([executable, "-NoProfile", "-NonInteractive", "-Command", command], cwd=str(cwd), capture_output=True, text=True, timeout=120)
        out = (result.stdout + "\n" + result.stderr).strip()
        return ToolResult(result.returncode == 0, out or f"Código {result.returncode}")

    def _git(self, args: dict[str, Any]) -> ToolResult:
        command = str(args.get("command", "status --short")); cwd = self._safe_path(str(args.get("cwd", ".")))
        parts = command.split(); result = subprocess.run(["git", *parts], cwd=str(cwd), capture_output=True, text=True, timeout=120)
        return ToolResult(result.returncode == 0, (result.stdout + "\n" + result.stderr).strip())

    def verify(self, name: str, args: dict[str, Any], result: ToolResult) -> ToolResult:
        if not result.success: return result
        if name in {"write_file", "read_file", "delete_file"} and args.get("path"):
            p = self._safe_path(str(args["path"]))
            exists = p.exists()
            expected = name != "delete_file"
            return ToolResult(exists == expected, f"Verificación {name}: {'correcta' if exists == expected else 'fallida'} ({p})")
        return ToolResult(True, result.output)
