from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import struct
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCAN = [sys.executable, "tools/scan_webkit_patterns.py"]

PT_GNU_RELRO = 0x6474e550


class WebKitArtifactTests(unittest.TestCase):
    def run_json(self, command: list[str]) -> dict:
        completed = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        return json.loads(completed.stdout)

    def test_migration_manifest_marks_absent(self) -> None:
        cfg = json.loads((ROOT / "tools" / "webkit_1352_migration.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg.get("artifact", {}).get("status"), "ABSENT")
        self.assertEqual(cfg.get("modules", {}).get("libSceNKWebKit.sprx", {}).get("status"), "ABSENT")

    def test_scan_detects_minimal_elf_and_relro(self) -> None:
        # Build a minimal ELF64 little-endian header with one program header of type PT_GNU_RELRO
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "minimal_elf.bin"
            e_ident = b"\x7fELF" + bytes([2, 1, 1]) + b"\x00" * 9  # EI_CLASS=2, EI_DATA=1
            # ELF64 header fields
            e_type = 2
            e_machine = 62
            e_version = 1
            e_entry = 0
            e_phoff = 64
            e_shoff = 0
            e_flags = 0
            e_ehsize = 64
            e_phentsize = 56
            e_phnum = 1
            e_shentsize = 0
            e_shnum = 0
            e_shstrndx = 0
            elf_hdr = struct.pack("<HHIQQQIHHHHHH", e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx)
            # Program header: p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align
            ph = struct.pack("<IIQQQQQQ", PT_GNU_RELRO, 0, 0, 0, 0, 0, 0, 0)
            content = e_ident + elf_hdr + ph
            p.write_bytes(content)
            report = self.run_json(SCAN + ["--image", str(p), "--json"])
            elf = report.get("elf", {})
            self.assertTrue(elf.get("detected"), msg="ELF not detected on minimal ELF sample")
            self.assertTrue(elf.get("relro_present_heuristic"), msg="RELRO heuristic should be true for PT_GNU_RELRO sample")

    def test_scan_rejects_truncated_and_out_of_bounds_elf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            truncated = Path(tmp) / "truncated.bin"
            truncated.write_bytes(b"\x7fELF")
            report = self.run_json(SCAN + ["--image", str(truncated), "--json"])
            self.assertEqual(report["elf"]["format"], "ELF_TRUNCATED")

            malformed = Path(tmp) / "malformed.bin"
            ident = b"\x7fELF" + bytes([2, 1, 1]) + b"\x00" * 9
            header = struct.pack("<HHIQQQIHHHHHH", 2, 62, 1, 0, 0x1000, 0, 0, 64, 56, 1, 0, 0, 0)
            malformed.write_bytes(ident + header)
            report = self.run_json(SCAN + ["--image", str(malformed), "--json"])
            self.assertEqual(report["elf"]["format"], "ELF64_LE_WITH_ERRORS")
            self.assertTrue(report["elf"]["errors"])

    def test_scan_rejects_invalid_relro_and_text_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image = bytearray(0x220)
            image[:16] = b"\x7fELF" + bytes([2, 1, 1]) + bytes(9)
            struct.pack_into("<H", image, 54, 56)
            struct.pack_into("<Q", image, 32, 64)
            struct.pack_into("<H", image, 56, 1)
            struct.pack_into("<IIQQQQQQ", image, 64, PT_GNU_RELRO, 0, 0x210, 0, 0x40, 0x40, 0, 0x10)
            image_path = Path(tmp) / "bad_relro.elf"
            config_path = Path(tmp) / "config.json"
            image_path.write_bytes(image)
            config_path.write_text(json.dumps({"target_firmware": "13.52", "patterns": {"elf_magic": {"bytes": "7f454c46"}}}), encoding="utf-8")
            report = self.run_json(SCAN + ["--image", str(image_path), "--config", str(config_path), "--json"])
            self.assertFalse(report["container"]["relro_present_heuristic"])
            self.assertFalse(report["container"]["segments"][0]["valid_file_range"])
            self.assertEqual(report["patterns"]["elf_magic"]["segment_roles"], [[]])

            text_image = bytearray(0x220)
            text_image[:16] = b"\x7fELF" + bytes([2, 1, 1]) + bytes(9)
            struct.pack_into("<Q", text_image, 40, 0x100)
            struct.pack_into("<H", text_image, 58, 64)
            struct.pack_into("<H", text_image, 60, 3)
            struct.pack_into("<H", text_image, 62, 2)
            struct.pack_into("<IIQQQQIIQQ", text_image, 0x100 + 64, 1, 1, 6, 0, 0x210, 0x40, 0, 0, 1, 0)
            names = b"\x00.text\x00.shstrtab\x00"
            text_image[0x1c0:0x1c0 + len(names)] = names
            struct.pack_into("<IIQQQQIIQQ", text_image, 0x100 + 128, 7, 3, 0, 0, 0x1c0, len(names), 0, 0, 1, 0)
            text_path = Path(tmp) / "bad_text.elf"
            text_path.write_bytes(text_image)
            report = self.run_json(SCAN + ["--image", str(text_path), "--json"])
            self.assertFalse(report["container"]["text_section"]["valid_file_range"])
            self.assertIn(".text section outside file bounds", report["container"]["errors"])

    def test_scan_validates_empty_and_mismatched_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "raw.bin"
            image.write_bytes(b"\x90\xc3")
            config = Path(tmp) / "patterns.json"
            config.write_text(json.dumps({
                "target_firmware": "13.52",
                "patterns": {
                    "empty": {"bytes": "", "mask": "", "status": "REQUIRES_REANALYSIS"},
                    "badmask": {"bytes": "90", "mask": "ffff", "status": "REQUIRES_REANALYSIS"},
                },
            }), encoding="utf-8")
            report = self.run_json(SCAN + ["--image", str(image), "--config", str(config), "--json"])
            self.assertIn("empty pattern", report["patterns"]["empty"]["validation_errors"])
            self.assertEqual(report["patterns"]["empty"]["status"], "REQUIRES_REANALYSIS")
            self.assertIn("mask length does not match pattern length", report["patterns"]["badmask"]["validation_errors"])
            self.assertEqual(report["patterns"]["badmask"]["status"], "UNVERIFIED")

    def test_scan_identifies_non_elf_raw_blob(self) -> None:
        # libkernel_sys_13.52.bin is a raw blob in this repo; ensure scanner does not mark it as ELF
        blob = ROOT / "libkernel_sys_13.52.bin"
        if not blob.is_file():
            self.skipTest("libkernel_sys_13.52.bin not present in this checkout")
        report = self.run_json(SCAN + ["--image", str(blob), "--json"])
        elf = report.get("elf", {})
        self.assertFalse(elf.get("detected", False), msg="libkernel blob should not be detected as ELF/SELF")


if __name__ == "__main__":
    unittest.main()
