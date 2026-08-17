from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cross_source_evidence
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
        self.assertEqual(report["artifact"]["sha256"], "ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c")
        self.assertNotEqual(report["artifact"]["sha256"], "ef15204fee6f9f9e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c")
        self.assertEqual(report["artifact"]["size"], 479232)
        self.assertTrue(report["reconstruction"]["sha256_matches_artifact"])
        self.assertTrue(report["reconstruction"]["size_matches_artifact"])
        self.assertTrue(all(item["sha256_match"] for item in report["chunks"]))
        self.assertEqual(report["offsets"]["jitshm_create"]["category"], "DIRECT_BYTES")
        self.assertEqual(report["offsets"]["jitshm_alias"]["category"], "DIRECT_BYTES")

    def test_manifest_chunks_are_sequential(self) -> None:
        manifest = json.loads((ROOT / "tools/libkernel_1352_manifest.json").read_text(encoding="utf-8"))
        offsets = [int(item["offset"], 16) for item in manifest["chunks"]]
        sizes = [item["size"] for item in manifest["chunks"]]
        self.assertEqual(offsets, [0, sizes[0], sizes[0] + sizes[1]])

    def test_strong_evidence_requires_artifact_hash_and_reconstruction(self) -> None:
        with self.assertRaises(ValueError):
            cross_source_evidence.validate_strong_claims({"status": "CONFIRMED_1352", "artifact": None, "sha256": None, "size": None, "chunks": [], "reconstruction_match": False})
        with self.assertRaises(ValueError):
            cross_source_evidence.validate_strong_claims({"status": "UNVERIFIED", "findings": [{"status": "DIRECT_BYTES"}]})
        cross_source_evidence.validate_strong_claims({"status": "CONFIRMED_1352", "artifact": "libkernel_sys_13.52.bin", "sha256": "a" * 64, "size": 1, "chunks": [{"sha256_match": True, "size_match": True, "offset_match": True}], "reconstruction_match": True})

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
        self.assertEqual(report["target_13_52"]["status"], "ABSENT")
        self.assertEqual(report["target_13_52"]["detail"], "ABSENT_FROM_PUBLIC_TABLE")
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

    def test_webkit_scanner_reports_container_and_segments(self) -> None:
        import struct
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image = bytearray(0x180)
            image[:16] = b"\x7fELF" + bytes([2, 1, 1]) + bytes(9)
            struct.pack_into("<Q", image, 32, 64)
            struct.pack_into("<H", image, 54, 56)
            struct.pack_into("<H", image, 56, 2)
            struct.pack_into("<IIQQQQQQ", image, 64, 1, 5, 0x120, 0x400000, 0, 8, 8, 0x10)
            struct.pack_into("<IIQQQQQQ", image, 120, 0x61000010, 4, 0x128, 0x400008, 0, 8, 8, 0x10)
            image[0x120:0x128] = bytes.fromhex("48c7c01502000049")
            image[0x128:0x130] = bytes.fromhex("89ca0f057201c348")
            image_path = tmp_path / "synthetic.elf"
            config_path = tmp_path / "config.json"
            image_path.write_bytes(image)
            config_path.write_text(json.dumps({"target_firmware": "13.52", "patterns": {"stub": {"bytes": "48c7c01502000049"}}}), encoding="utf-8")
            report = self.run_json([sys.executable, "tools/scan_webkit_patterns.py", "--image", str(image_path), "--config", str(config_path), "--json"])
            self.assertEqual(report["container"]["format"], "ELF64_LE")
            self.assertEqual(len(report["container"]["segments"]), 2)
            self.assertEqual(report["patterns"]["stub"]["status"], "DIRECT_BYTES")
            self.assertEqual(report["patterns"]["stub"]["semantic_identity"], "REQUIRES_REANALYSIS")

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

    def test_psfree_porting_audit_is_conservative(self) -> None:
        if not PSFREE.is_dir():
            self.skipTest("external PSFree clone is not present in this checkout")
        out = ROOT / "tests/.psfree-porting-report.json"
        subprocess.run(
            [
                sys.executable,
                "tools/audit_psfree_porting.py",
                "--psfree",
                str(PSFREE),
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
        self.assertEqual(report["target_firmware"], "13.52")
        self.assertEqual(report["source_support"]["public_13_52_support"], "ABSENT")
        self.assertEqual(report["source_support"]["8_50_8_52_webkit_table"], "UNVERIFIED")
        self.assertTrue(any(item["status"] == "PORTABLE" for item in report["portable_mechanisms"]))
        self.assertTrue(all(item["status"] == "OBSOLETE" for item in report["historical_absolute_values"]))

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
                    self.assertEqual(data["scanner"]["supported_formats"], ["RAW", "ELF64_LE", "ELF64_LE_WITH_ERRORS", "SELF"])
                    self.assertIn(".text", data["scanner"]["segment_metadata"])
                    self.assertIn("build_id", data["scanner"]["segment_metadata"])
                    self.assertEqual(data["libkernel_sys_anchor"]["symbols"]["stat"]["category"], "STRUCTURAL")

    def test_webkit_research_map_is_explicit(self) -> None:
        report = json.loads((ROOT / "analysis/webkit_13.52_research.json").read_text(encoding="utf-8"))
        self.assertEqual(report["target_firmware"], "13.52")
        self.assertIn("libkernel_sys_13.52.bin", [item["name"] for item in report["verified"]])
        self.assertTrue(report["missing"])
        self.assertEqual(report["next_best_artifact"]["classification_until_obtained"], "ABSENT")
        self.assertIn("rejected", report)

    def test_official_pup_metadata_does_not_promote_modules(self) -> None:
        report = json.loads((ROOT / "analysis/webkit_13.52_research.json").read_text(encoding="utf-8"))
        pup = next(item for item in report["external_artifacts"] if item["name"] == "PS4UPDATE.PUP")
        self.assertEqual(pup["firmware"], "13.52")
        self.assertEqual(pup["classification"], "UNVERIFIED")
        self.assertFalse(pup["local_full_file_retained"])
        self.assertEqual(pup["http_status"], 200)
        self.assertEqual(pup["content_length"], 503310848)
        self.assertEqual(pup["format"].split()[0], "SLB2")
        self.assertIn("libSceNKWebKit.sprx 13.52", report["missing"])

    def test_repository_evidence_integration_is_conservative(self) -> None:
        inventory = json.loads((ROOT / "analysis/research_repos_13.52.json").read_text(encoding="utf-8"))
        self.assertEqual(inventory["repo_count"], 39)
        self.assertEqual(inventory["research_summary"]["verified_repo_count"], 39)
        self.assertEqual(inventory["research_summary"]["cloned_repo_count"], 39)
        self.assertTrue(any(item["repo"] == "ntfargo/CSSFontFace-Exploit" for item in inventory["repositories"]))
        self.assertTrue(any(item["repo"] == "ArabPixel/WebKitty" for item in inventory["repositories"]))
        hen = next(item for item in inventory["repositories"] if item["repo"] == "Scene-Collective/ps4-hen")
        self.assertEqual(hen["evidence_summary"]["classification"], "UNVERIFIED")
        self.assertEqual(hen["evidence_summary"]["candidate_offsets"]["SYSENT"], "0x1102B70")
        self.assertEqual(hen["evidence_summary"]["candidate_offsets"]["pmap_protect"], "0x59DF0")
        self.assertEqual(hen["evidence_summary"]["candidate_offsets"]["pmap_protect_alternate"], "0x58570")
        corpus = next(item for item in inventory["repositories"] if item["repo"] == "FreeBSDKernel9-0/PS4OSSCode")
        self.assertEqual(corpus["corpus_audit"]["tracked_files"], 584706)
        self.assertEqual(corpus["corpus_audit"]["retail_1352_modules"], "ABSENT")
        largest = json.loads((ROOT / "analysis/largest_corpus_ps4osscode_13.52.json").read_text(encoding="utf-8"))
        self.assertEqual(largest["artifact_assessment"]["libSceNKWebKit_13_52"], "ABSENT")
        self.assertEqual(largest["artifact_assessment"]["historical_webkit_source"], "STRUCTURAL")

    def test_github_indirect_findings_remain_conservative(self) -> None:
        report = json.loads((ROOT / "analysis/github_indirect_findings_13.52.json").read_text(encoding="utf-8"))
        self.assertEqual(report["target_firmware"], "13.52")
        by_repo = {item["repo"]: item for item in report["new_sources"]}
        self.assertEqual(by_repo["BillZaiD/ps4-kernel-uaf-research-fw1352"]["classification"], "UNVERIFIED")
        self.assertEqual(by_repo["BillZaiD/ps4-kernel-uaf-research-fw1352"]["artifact_status"], "ABSENT")
        self.assertEqual(by_repo["alferdoss/SLOPOS-offsets"]["candidate_offsets"]["pmap_protect"], "0x58570")
        self.assertEqual(by_repo["Gustuds/PS4-AIO-Host-by-Gustuds"]["classification"], "STRUCTURAL")
        self.assertTrue(all(item["firmware"] != "13.52" or item["classification"] != "DIRECT_BYTES" for item in by_repo["Gustuds/PS4-AIO-Host-by-Gustuds"]["patches"]))

    def test_github_deep_audit_remains_conservative(self) -> None:
        report = json.loads((ROOT / "analysis/github_deep_audit_13.52.json").read_text(encoding="utf-8"))
        self.assertEqual(report["target_firmware"], "13.52")
        self.assertEqual(report["cross_source_conclusions"]["new_direct_1352_bytes"], 0)
        by_repo = {item["repo"]: item for item in report["findings"]}
        self.assertEqual(by_repo["Leandrobts/Test"]["artifact_status"], "ABSENT")
        self.assertEqual(by_repo["Leandrobts/Test"]["classification"], "UNVERIFIED")
        self.assertEqual(by_repo["Gezine/BD-JB5"]["candidate_1352_table"]["SYSENT_661_OFFSET"], "0x110A760")
        self.assertIn("PS4 support gate ends at 13.00", by_repo["Gezine/BD-JB5"]["why_not_direct"])
        loader = by_repo["ps4-linux/ps4-linux-loader"]
        self.assertEqual(loader["candidate_1352_offsets"]["pmap_protect"], "0x58570")
        self.assertEqual(loader["candidate_1352_offsets"]["SYSENT"], "0x1102B70")
        self.assertEqual(by_repo["andleexploit/masticore-13.52"]["artifact_status"], "ABSENT")
        self.assertEqual(report["issues_and_prs"][0]["classification"], "UNVERIFIED")

    def test_downloaded_issue_artifact_remains_historical(self) -> None:
        report = json.loads((ROOT / "analysis/github_downloaded_artifacts_13.52.json").read_text(encoding="utf-8"))
        self.assertEqual(report["target_1352_status"]["new_confirmed_1352_bytes"], 0)
        artifact = report["artifacts"][0]
        self.assertEqual(artifact["declared_firmware"], "11.02")
        member = artifact["members"][0]
        self.assertEqual(member["path"], "11.02/kernel.bin")
        self.assertEqual(member["classification"], "DIRECT_BYTES")
        self.assertEqual(member["sha256"], "451f87357637beedc92fe822fc5942f86e12231a53fa8dfd81c24433093408d4")
        self.assertEqual(member["scope"], "DIRECT_BYTES for historical 11.02 kernel artifact only; not evidence of 13.52")
        self.assertEqual(report["target_1352_status"]["kernel_1352"], "ABSENT")

    def test_webkit_absence_report_is_explicit(self) -> None:
        report = json.loads((ROOT / "analysis/webkit_13.52.json").read_text(encoding="utf-8"))
        self.assertEqual(report["target_firmware"], "13.52")
        self.assertEqual(report["status"], "ABSENT")
        self.assertIsNone(report["artifact"])
        self.assertIsNone(report["sha256"])
        self.assertEqual(report["classification"], "ABSENT")


    def test_independent_suchi96_corroboration_manifest(self) -> None:
        report = json.loads((ROOT / "analysis/libkernel_1352_corroboration.json").read_text(encoding="utf-8"))
        independent = report["independent_provenance"]
        self.assertEqual(independent["repository"], "Suchi96/PS4_13_52_libkerneldump")
        self.assertEqual(independent["commit"], "930e3af24294ebe405920de2b0cdfaddd4acb4e7")
        self.assertEqual(independent["sha256"], "ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c")
        self.assertTrue(independent["bytes_match_local_byte_for_byte"])
        self.assertTrue(report["reconstruction"]["matches_firmware_lab_combined"])
        self.assertEqual(report["reconstruction"]["byte_difference_count"], 0)
        self.assertEqual(report["classification"]["runtime_claims_in_source_readme"], "UNVERIFIED")
        self.assertEqual(report["classification"]["kernel_offsets"], "UNVERIFIED")

    def test_manifest_records_independent_provenance(self) -> None:
        manifest = json.loads((ROOT / "tools/libkernel_1352_manifest.json").read_text(encoding="utf-8"))
        independent = manifest["artifact"]["provenance"]["independent"]
        self.assertEqual(independent["sha256"], "ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c")
        self.assertTrue(independent["byte_for_byte_match"])
        self.assertEqual(manifest["evidence_notes"]["source_readme_runtime_claims"], "UNVERIFIED: the independent README claims retail runtime validation, but no runtime log or hardware evidence is included in this static audit.")


if __name__ == "__main__":
    unittest.main()
