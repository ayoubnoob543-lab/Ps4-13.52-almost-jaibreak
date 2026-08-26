from pathlib import Path
import re

paths = {
    "1302": Path("kpayload/source/offsets/1302.c"),
    "1304": Path("kpayload/source/offsets/1304.c"),
}

def parse(path):
    out = {}
    for line in path.read_text(errors="replace").splitlines():
        m = re.search(r"\.(\w+)\s*=\s*(0x[0-9A-Fa-f]+)", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out

data = {fw: parse(path) for fw, path in paths.items()}
for fw, path in paths.items():
    print(f"FILE\t{fw}\t{path}\t{path.stat().st_size}")

print("FIELD\t13.02\t13.04\tSTATUS")
for field in sorted(set(data["1302"]) | set(data["1304"])):
    a = data["1302"].get(field, "-")
    b = data["1304"].get(field, "-")
    status = "same" if a == b else "different_or_missing"
    print(f"{field}\t{a}\t{b}\t{status}")
