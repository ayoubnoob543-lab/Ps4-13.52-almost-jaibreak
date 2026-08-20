import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from analyze_webkit_retail import analyze  # noqa: E402


class WebKitRetailPipelineTests(unittest.TestCase):
    def test_raw_fixture_is_direct_but_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.bin"
            path.write_bytes(b"authorized-local-fixture\0JSCell\0MarkedVector\0")
            result = analyze(path, KIT / "three_family_signatures.json")
            self.assertEqual(result["evidence"], "DIRECT_BYTES")
            self.assertEqual(result["container"]["format"], "UNKNOWN_OR_RAW")
            self.assertEqual(result["target_promotion"], "CONFIRMED_13.52_DISABLED")
            self.assertTrue(all(x["classification"] in {"PARTIAL MATCH", "UNVERIFIED"} for x in result["family_correlations"]))

    def test_synthetic_elf_has_pt_load_and_build_id_note(self):
        # Minimal ELF64 LE with one PT_LOAD and one GNU build-id note.
        header_size, ph_size = 64, 56
        phoff, note_off = header_size, header_size + (2 * ph_size)
        note_name = b"GNU\0"
        note_desc = bytes.fromhex("00112233445566778899aabbccddeeff")
        note = struct.pack("<III", len(note_name), len(note_desc), 3)
        note += note_name + b"\0" * ((-len(note_name)) % 4)
        note += note_desc + b"\0" * ((-len(note_desc)) % 4)
        file_size = note_off + len(note)
        elf = bytearray(file_size)
        elf[:16] = b"\x7fELF" + bytes([2, 1, 1, 0]) + bytes(8)
        struct.pack_into("<HHIQQQIHHHHHH", elf, 16, 3, 62, 1, 0, phoff, 0, 0, 64, 56, 2, 0, 0, 0)
        struct.pack_into("<IIQQQQQQ", elf, phoff, 1, 4, 0, 0, 0, file_size, file_size, 4)
        struct.pack_into("<IIQQQQQQ", elf, phoff + ph_size, 4, 0, note_off, 0, 0, len(note), len(note), 4)
        elf[note_off:] = note
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.elf"
            path.write_bytes(elf)
            result = analyze(path, KIT / "three_family_signatures.json")
            self.assertEqual(result["container"]["format"], "ELF")
            self.assertEqual(len(result["container"]["pt_load"]), 1)
            self.assertEqual(result["container"]["build_ids"], [note_desc.hex()])
            self.assertEqual(result["semantic_identity"], "UNVERIFIED")

    def test_manifest_has_exact_three_families(self):
        manifest = json.loads((KIT / "three_family_signatures.json").read_text())
        ids = [x["id"] for x in manifest["families"]]
        self.assertEqual(ids, ["jscell_tox_type_validation", "markedvector_gc_containers", "clone_object_pool_alignment"])
        self.assertEqual(manifest["target_bytes_status"], "MISSING")


if __name__ == "__main__":
    unittest.main()
