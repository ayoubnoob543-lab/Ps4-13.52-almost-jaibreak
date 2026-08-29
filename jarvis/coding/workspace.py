from __future__ import annotations

import subprocess
from pathlib import Path

class Workspace:
    """Operaciones de proyecto que no requieren conocer el lenguaje del repositorio."""
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve(); self.root.mkdir(parents=True, exist_ok=True)

    def files(self, pattern: str = "*") -> list[str]:
        return [str(p.relative_to(self.root)) for p in self.root.glob(pattern) if p.is_file()]

    def read(self, relative: str) -> str:
        return (self.root / relative).resolve().read_text(encoding="utf-8")

    def write(self, relative: str, content: str) -> str:
        path = (self.root / relative).resolve(); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8"); return str(path)

    def run_test_command(self, command: str = "python -m pytest -q") -> tuple[bool, str]:
        result = subprocess.run(command, cwd=self.root, shell=True, capture_output=True, text=True, timeout=180)
        return result.returncode == 0, (result.stdout + "\n" + result.stderr).strip()
