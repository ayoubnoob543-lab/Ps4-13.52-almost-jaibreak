from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS4_RESEARCH = ROOT.parent
CSS = PS4_RESEARCH / "CSSFontFace-Exploit"
PSFREE = PS4_RESEARCH / "PSFree"
VUE = PS4_RESEARCH / "vue-after-free"
LOADER = PS4_RESEARCH / "ps4-linux-loader"


class StaticMigrationTests(unittest.TestCase):
    def run_json(self, command: list[str]) -> dict:
        completed = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        return json.loads(completed.stdout)

    def test_libkernel_anchor_and_chunks(self) -> None:
        report = self.run_json([sys.executable, "tools/validate_libkernel_1352.py", "--json"])
        self.assertTrue(report["artifact"]["sha256_match"])
        self.assertEqual(report["artifact"]["size"], 479232)
        self.assertTrue(report["reconstruction"]["sha256_matches_artifact"])
        self.assertTrue(report["reconstruction"]["size_matches_artifact"])
        self.assertTrue(all(item["sha256_match"] for item in report["chunks"]))
        self.assertEqual(report["offsets"]["jitshm_create"]["category"], "DIRECT_BYTES")
        self.assertEqual(report["offsets"]["jitshm_alias"]["category"], "DIRECT_BYTES")

    def test_cssfontface_parser_marks_1352_absent(self) -> None:
        out = ROOT / "tests/.cssfontface-report.json"
        constants_path = CSS / "public/src/ps4/constants.js"
        if not constants_path.is_file():
            constants_path = ROOT / "tests/fixtures/constants.js"
        subprocess.run(
            [sys.executable, "tools/analyze_cssfontface_constants.py", str(constants_path), "--out", str(out)],
            cwd=ROOT,
            check=True,
        )
        try:
            report = json.loads(out.read_text(encoding="utf-8"))
        finally:
            out.unlink(missing_ok=True)
        self.assertEqual(report["target_13_52"]["status"], "ABSENT_FROM_PUBLIC_TABLE")
        self.assertIn("wk_CSSFontFace_m_featureSettings_m_buffer", report["field_presence"])
        self.assertNotIn("11.50", [item["label"] for item in report["firmware_keys"]])

    def test_cross_source_classification(self) -> None:
        if not all(path.is_dir() for path in (PSFREE, CSS, VUE, LOADER)):
            self.skipTest("external research clones are not present in this checkout")
        out = ROOT / "tests/.cross-source-report.json"
        subprocess.run(
            [
                sys.executable,
                "tools/cross_source_evidence.py",
                "--lab",
                str(ROOT),
                "--psfree",
                str(PSFREE),
                "--cssfontface",
                str(CSS),
                "--vue",
                str(VUE),
                "--loader",
                str(LOADER),
                "--out",
                str(out),
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        try:
            report = json.loads(out.read_text(encoding="utf-8"))
        finally:
            out.unlink(missing_ok=True)
        self.assertEqual(report["anchor"]["status"], "CONFIRMED_1352")
        by_source = {item["source"]: item for item in report["sources"]}
        css_status = {item["name"]: item["status"] for item in by_source["CSSFontFace-Exploit"]["findings"]}
        loader_status = {item["name"]: item["status"] for item in by_source["ps4-linux-loader"]["findings"]}
        self.assertEqual(css_status["m_featureSettings_13_52"], "REQUIRES_REANALYSIS")
        self.assertEqual(css_status["webkit_13_52_artifact"], "ABSENT")
        self.assertEqual(loader_status["13_52_offset_block"], "STRUCTURAL")
        self.assertEqual(loader_status["kernel_bytes"], "ABSENT")

    def test_webkit_pattern_statuses_are_conservative(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image = tmp_path / "image.bin"
            config = tmp_path / "config.json"
            image.write_bytes((ROOT / "libkernel_sys_13.52.bin").read_bytes()[0x510:0x510 + 16])
            config.write_text(json.dumps({"target_firmware": "13.52", "patterns": {"stub": {"bytes": "48c7c0150200004989ca0f057201c348"}}}), encoding="utf-8")
            report = self.run_json([sys.executable, "tools/scan_webkit_patterns.py", "--image", str(image), "--config", str(config), "--json"])
            self.assertEqual(report["patterns"]["stub"]["status"], "DIRECT_BYTES")
            self.assertEqual(report["patterns"]["stub"]["semantic_identity"], "REQUIRES_REANALYSIS")

    def test_xref_analyzer_has_static_fallback(self) -> None:
        out_dir = ROOT / "tests/.xref-output"
        out_dir.mkdir(exist_ok=True)
        subprocess.run(
            [sys.executable, "tools/analyze_xref_versions.py", str(ROOT / "libkernel_sys_13.52.bin"), "--out-dir", str(out_dir)],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        try:
            report = json.loads((out_dir / "xref_version_analysis_13.52.json").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(out_dir, ignore_errors=True)
        self.assertIn("Capstone", report["method"]["disassembly"])
        self.assertEqual(report["method"]["execution"], "none")

    def test_json_manifests_are_valid(self) -> None:
        for path in [
            ROOT / "tools/libkernel_1352_manifest.json",
            ROOT / "tools/webkit_1352_migration.json",
            ROOT / "tools/jordy_1352_migration.json",
        ]:
            with self.subTest(path=path):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data.get("target_firmware", data.get("artifact", {}).get("firmware")), "13.52")
                if path.name == "webkit_1352_migration.json":
                    self.assertEqual(data["portable_methodology"]["rip_relative_import_resolution"]["status"], "PORTABLE")
                    self.assertEqual(data["modules"]["libSceNKWebKit.sprx"]["status"], "ABSENT")
                    self.assertEqual(data["libkernel_sys_anchor"]["symbols"]["stat"]["category"], "STRUCTURAL")


if __name__ == "__main__":
    unittest.main()
