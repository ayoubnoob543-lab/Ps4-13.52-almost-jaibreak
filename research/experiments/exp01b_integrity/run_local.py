#!/usr/bin/env python3
"""exp01b_integrity — verifica integridad del blob dual-anclado antes de confiar en él."""
import hashlib, json, pathlib, datetime, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
EXPECT = {
    "libkernel_sys_13.52.bin": "ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c",
    "lk_dump1.bin": "d4a9a642f85446785469750532d9353c9010ebec4373b8e9c4c06d594536da57",
    "lk_dump2.bin": "e044d0e5303596df94f86190d34bee6dda8e87f9a51578d067e8d1650ca15e8d",
    "lk_dump3.bin": "e31dd16ddc488851c98bc1782cfe919ece1cab2c141bd0ef7c8a9ef82fb9fdf2",
}

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def main():
    out = {"experiment": "exp01b_integrity", "firmware": "13.52",
           "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "checks": [], "status": None}
    ok = True
    for name, want in EXPECT.items():
        p = ROOT / name
        if not p.exists():
            out["checks"].append({"file": name, "status": "FAIL", "reason": "missing"})
            ok = False
            continue
        got = sha256(p)
        match = got == want
        ok &= match
        out["checks"].append({"file": name, "size": p.stat().st_size,
                              "sha256": got, "expected": want,
                              "status": "PASS" if match else "FAIL"})
    raw = pathlib.Path(__file__).parent / "raw.bin"
    raw.write_bytes(json.dumps(out, indent=2).encode())
    out["status"] = "PASS" if ok else "FAIL"
    print(json.dumps(out, indent=2))
    (pathlib.Path(__file__).parents[2] / "results" / "exp01b_integrity.result.json").write_text(
        json.dumps(out, indent=2) + "\n")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
