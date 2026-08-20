#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "webkit-kit" / "tools"


class ModuleEvidencePipelineTests(unittest.TestCase):
    def test_system_elf_is_parsed_without_execution(self):
        from structural_signatures import analyze
        result = analyze(Path("/bin/true"))
        self.assertEqual(result["evidence"], "DIRECT_BYTES")
        self.assertEqual(result["format"]["format"], "ELF64")
        self.assertTrue(result["format"]["pt_load"])
        self.assertEqual(result["execution"], "PROHIBITED_BY_TOOL_POLICY")
        self.assertEqual(result["absolute_offsets"], "DISABLED")

    def test_raw_file_is_not_promoted(self):
        from structural_signatures import analyze
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw.bin"
            path.write_bytes(b"not-an-elf\0PUBLIC\0")
            result = analyze(path)
        self.assertEqual(result["format"]["format"], "UNKNOWN_OR_RAW")
        self.assertEqual(result["semantic_identity"], "UNVERIFIED")

    def test_pipeline_writes_comparison_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence.json"
            command = [sys.executable, str(TOOLS / "analyze_module_evidence.py"), "/bin/true", "--reference", "/bin/true", "-o", str(output)]
            completed = subprocess.run(command, cwd=TOOLS, capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["schema"], "ps4-webkit-module-evidence/v1")
        self.assertEqual(report["comparisons"][0]["classification"], "CANDIDATE_STRUCTURAL_ONLY")
        self.assertEqual(report["policy"]["wpe_or_oss_equivalence"], "NEVER_INFERRED")


if __name__ == "__main__":
    unittest.main()
