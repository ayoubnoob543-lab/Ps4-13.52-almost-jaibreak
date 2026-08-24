#!/usr/bin/env python3
"""exp01a_static_stubs — enumera stubs de syscall en libkernel_sys_13.52.bin.

Patrón canónico verificado: 48 c7 c0 <imm32> 49 89 ca 0f 05
(mov rax, num ; mov r10, rcx ; syscall ; jb +1 ; ret)

Clasifica presencia de wrappers críticos para las vías del plan.
NOTA: wrapper userland presente NO implica syscall habilitado en kernel/prison.
"""
import json, pathlib, datetime, struct, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
BLOB = ROOT / "libkernel_sys_13.52.bin"
PATTERN = bytes.fromhex("48c7c0" + "????????"[:0] ) # placeholder, real below
PAT_HEAD = b"\x48\xc7\xc0"
PAT_TAIL = b"\x49\x89\xca\x0f\x05"

GATE = {
    "kqueue": 362, "kevent": 363,
    "__semctl": 220, "semget": 221, "semop": 222,
    "msgget": 225, "shmget": 231,
    "_known_present": {"mmap": 477, "read": 3},
}

def enumerate_stubs(data):
    found = []
    i = 0
    while True:
        i = data.find(PAT_HEAD, i)
        if i < 0 or i + 13 > len(data):
            break
        if data[i+7:i+12] == PAT_TAIL:
            num = struct.unpack_from("<I", data, i + 3)[0]
            found.append({"offset": f"0x{i:x}", "syscall": num})
        i += 1
    return found

def main():
    data = BLOB.read_bytes()
    stubs = enumerate_stubs(data)
    nums = {}
    for s in stubs:
        nums.setdefault(s["syscall"], []).append(s["offset"])

    gate = {name: {"num": num,
                   "present": num in nums,
                   "offsets": [f"0x{o}" for o in nums.get(num, [])][:4]}
            for name, num in GATE.items() if name != "_known_present"}

    known = {name: (num in nums) for name, num in GATE["_known_present"].items()}

    out = {
        "experiment": "exp01a_static_stubs",
        "firmware": "13.52", "blob": str(BLOB.name),
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_stub_sites": len(stubs),
        "distinct_syscalls": len(nums),
        "sanity_known_present": known,
        "gate": gate,
    }
    # sanity: mmap(477)/read(3) DEBEN existir; si no, patrón/parse inválido
    sanity_ok = all(known.values())
    out["status"] = ("PASS" if sanity_ok else "UNKNOWN") 
    print(json.dumps(out, indent=2))

    resdir = pathlib.Path(__file__).parents[2] / "results"
    (resdir / "exp01a_static_stubs.result.json").write_text(json.dumps(out, indent=2) + "\n")
    (resdir / "exp01a_static_stubs.raw.json").write_text(json.dumps(stubs) + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
