[README.md](https://github.com/user-attachments/files/30945377/README.md)

# PS4 13.52 libkernel_sys.sprx — Memory Dump

Captured live from a **retail PS4 running firmware 13.52** using the mast1c0re exploit on Okage Shadow King (CUSA02282 / BASCUS-97129, eboot v1.01).

---

## Files

| File | Offset Range | Size |
|------|-------------|------|
| lk_dump1.bin | lk+0x00000 – lk+0x26FFF | 156KB |
| lk_dump2.bin | lk+0x27000 – lk+0x4DFFF | 156KB |
| lk_dump3.bin | lk+0x4E000 – lk+0x75FFF | 156KB |
| libkernel_sys_13.52.bin | lk+0x00000 – lk+0x75FFF | 468KB (combined) |

The combined file covers the full library. 13.52 is slightly larger than 12.52 (0x6EFC0) — the dump covers everything.

To combine the chunks yourself and verify:
```bash
cat lk_dump1.bin lk_dump2.bin lk_dump3.bin > libkernel_sys_13.52.bin
```

---

## How It Was Dumped

The mast1c0re exploit was used to escape the PS2 emulator sandbox on a retail PS4 13.52. From inside the breakout:

1. Library base computed at runtime via the GOT anchor method (see below)
2. `pread()` used to read the library in 156KB chunks directly from the mapped region
3. Each chunk written to `/av_contents/content_tmp/` via `open()`/`write()`
4. Exfiltrated via PS2 memory card (VMC) dump on PC

No CFW. No kernel exploit. Retail hardware only.

---

## How To Verify It Is 13.52

### Step 1 — Compute library base at runtime

```cpp
// Okage eboot v1.01 — Ghidra static address
#define GOT_USLEEP   0x0083d1c0
#define USLEEP_OFF   0x013b20

uint64_t lk_base = DEREF(EBOOT(GOT_USLEEP)) - USLEEP_OFF;
```

The GOT entry for `sceKernelUsleep` contains its runtime address. Subtracting the known offset gives `lk_base`.

### Step 2 — Run the verification script

```python
import struct

combined = bytearray(0x75000)
for fname, base in [('lk_dump1.bin', 0x00000),
                    ('lk_dump2.bin', 0x27000),
                    ('lk_dump3.bin', 0x4E000)]:
    d = open(fname, 'rb').read()
    combined[base:base+len(d)] = d

def check(name, off):
    b = combined[off:off+4]
    ok = b[0:3] in (bytes([0x55,0x48,0x89]),
                    bytes([0x55,0x41,0x57]),
                    bytes([0x55,0x41,0x56]))
    print(f"  {name:<12} lk+0x{off:05X}  {'OK' if ok else 'FAIL'}  {b.hex()}")

print("13.52 fingerprint:")
check("usleep",   0x013b20)  # anchor — unique per firmware
check("open",     0x0148d0)
check("close",    0x014900)
check("read",     0x014870)
check("write",    0x0148a0)
check("notify",   0x019320)
check("socket",   0x0045f0)
check("connect",  0x00c990)  # real connect wrapper
```

All entries should show `OK` (valid x86-64 function prologue). If any show `FAIL` the dump is corrupt at that location.

### Step 3 — Cross-reference firmware deltas

| Cluster | 9.00→13.52 | 11.02→13.52 |
|---------|-----------|------------|
| IO / notification | -0x1db0 | -0x1c30 |

Example: `open` on 11.02 is at `0x14B00`. On 13.52 it is at `0x148D0`. Delta = `-0x230` (within the IO cluster shift of `-0x1c30`).

> **Note:** McCaulay's `13.52.hpp` in the mast1c0re SDK is a copy of `11.00` — the offsets are wrong. Do not use it for 13.52.

---

## Confirmed Working Offsets

All offsets below were verified by actually calling the functions on retail 13.52 hardware and confirming correct behavior.

```cpp
// libkernel_sys.sprx — firmware 13.52
// lk_base = DEREF(eboot_GOT_usleep) - 0x013b20

#define LK_USLEEP        0x013b20  // anchor
#define LK_OPEN          0x0148d0  // confirmed: returns valid fd
#define LK_CLOSE         0x014900  // confirmed
#define LK_READ          0x014870  // confirmed
#define LK_WRITE         0x0148a0  // confirmed: 31 bytes written
#define LK_STAT          0x015310  // confirmed
#define LK_PREAD         0x015460  // confirmed
#define LK_PWRITE        0x015490  // confirmed
#define LK_LSEEK         0x0154f0  // confirmed
#define LK_UNLINK        0x014930  // confirmed
#define LK_NOTIFY        0x019320  // confirmed: PS4 notification displayed
#define LK_SOCKET        0x0045f0  // confirmed: returns fd=22
#define LK_ERROR         0x001bb0  // __error() returns ptr to errno
#define LK_JITSHM_CREATE 0x00510   // syscall 533 — confirmed working
#define LK_JITSHM_ALIAS  0x00530   // syscall 534 — confirmed working
#define LK_MMAP          0x114E0   // confirmed: anon mmap returns 0x211xxxxxxx
#define LK_CONNECT       0x0C990   // real connect — calls connect(98) at +49
#define LK_CONNECT_ALT   0x0C970   // alternative connect wrapper
```

---

## Important Notes

**`0x00c7e0` is NOT connect.**
This offset is cited in multiple places as the connect wrapper. Dump analysis proves it calls `accept(#30)` internally. Using it for connect will always return -1.

**bind / listen / setsockopt have no wrappers in 13.52.**
These syscalls exist as raw stubs but their wrapper functions were removed. The PS4 process cannot act as a TCP server. Only outbound connect via `0x0C990` is possible.

**RSP validation on 13.52.**
BSD syscalls (1–200) invoked via raw `syscall` instruction from a ROP chain will crash the process — the kernel validates RSP is within a legitimate thread stack. PS4-custom syscalls (500+) are exempt. Always call complete libkernel wrapper functions.

---

## Related

- [mast1c0re 13.52 research](https://github.com/Suchi96/mast1c0re-13_52-test)
- [ps2-emu-compiler.self 11.02](https://github.com/Suchi96/ps411_02stuff)
- [CTurt's mast1c0re writeup](https://cturt.github.io/mast1c0re.html)
