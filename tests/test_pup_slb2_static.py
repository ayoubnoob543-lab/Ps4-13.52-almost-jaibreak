import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("parse_slb2_static", ROOT / "tools" / "parse_slb2_static.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Slb2StaticTests(unittest.TestCase):
    def make_container(self, *, bad_bounds=False, truncate=False):
        name1 = b"PS4UPDATE1.PUP\0".ljust(32, b"\0")
        header = struct.pack("<IIII", 0x32424C53, 2, 0, 1) + b"\0" * 16
        start_sector = 2
        size = 16
        if bad_bounds:
            start_sector = 100
        entry = struct.pack("<II", start_sector, size) + b"\0" * 8 + name1
        payload = b"\0" * 1024 + b"0123456789abcdef"
        data = header + entry + payload
        return data[:20] if truncate else data

    def test_valid_container_and_entry_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.pup"
            path.write_bytes(self.make_container())
            result = MODULE.parse(path)
            self.assertEqual(result["format"], "SLB2 outer PUP container")
            self.assertEqual(result["entry_count"], 1)
            self.assertEqual(result["entries"][0]["name"], "PS4UPDATE1.PUP")
            self.assertTrue(result["entries"][0]["within_container"])
            self.assertEqual(result["entries"][0]["size"], 16)
            self.assertFalse(result["decryption_performed"])

    def test_truncated_header_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "truncated.pup"
            path.write_bytes(self.make_container(truncate=True))
            with self.assertRaises(ValueError):
                MODULE.parse(path)

    def test_out_of_bounds_entry_is_not_hashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.pup"
            path.write_bytes(self.make_container(bad_bounds=True))
            result = MODULE.parse(path)
            entry = result["entries"][0]
            self.assertFalse(entry["within_container"])
            self.assertIsNone(entry["sha256"])
            self.assertEqual(entry["classification"], "REQUIRES_REANALYSIS")


if __name__ == "__main__":
    unittest.main()
