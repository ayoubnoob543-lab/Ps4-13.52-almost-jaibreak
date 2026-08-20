#!/usr/bin/env python3
"""Unit tests for the WPE validation protocol; no WebKit runtime is launched."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


TOOLS = pathlib.Path(__file__).resolve().parent
FIXTURES = TOOLS.parent / "homebrew" / "fixtures"


class WPEValidationTests(unittest.TestCase):
    def run_json(self, command: list[str], output: pathlib.Path) -> dict:
        completed = subprocess.run(command + ["--output", str(output)], text=True, capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(output.read_text(encoding="utf-8"))

    def test_missing_minibrowser_is_not_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "runner.json"
            result = self.run_json([sys.executable, str(TOOLS / "run_wpe_headless.py"), "--prefix", "/tmp/wpe-prefix"], output)
            self.assertEqual(result["status"], "NOT_RUN")
            self.assertIsNone(result["actual_assertions"])
            self.assertTrue(all(item["status"] == "PASS" for item in result["fixtures"]))

    def test_comparator_requires_explicit_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            directory = pathlib.Path(directory)
            source = directory / "source.json"
            output = directory / "comparison.json"
            source.write_text(json.dumps({"status": "NOT_RUN", "actual_assertions": None}), encoding="utf-8")
            result = self.run_json([sys.executable, str(TOOLS / "compare_wpe_smoke.py"), str(source)], output)
            self.assertEqual(result["status"], "NOT_RUN")

    def test_comparator_passes_only_exact_contract(self) -> None:
        expected = json.loads((FIXTURES / "wpe-expected-assertions.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            directory = pathlib.Path(directory)
            source = directory / "source.json"
            output = directory / "comparison.json"
            source.write_text(json.dumps({"status": "PASS", "actual_assertions": expected["stages"]}), encoding="utf-8")
            result = self.run_json([sys.executable, str(TOOLS / "compare_wpe_smoke.py"), str(source)], output)
            self.assertEqual(result["status"], "PASS")
            self.assertTrue(all(item["status"] == "PASS" for item in result["capabilities"].values()))


if __name__ == "__main__":
    unittest.main()
