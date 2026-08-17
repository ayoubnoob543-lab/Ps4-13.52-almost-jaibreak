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
