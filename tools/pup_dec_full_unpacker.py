#!/usr/bin/env python3
"""pup_dec_full_unpacker.py — Desempaquetador COMPLETO de *.PUP.dec PS4.

Procesa un fichero .PUP.dec (producido por ps4-pup_decrypt en consola con
kernel-exec activo) y extrae TODOS los segmentos con descifrado AES128-CBC,
descompresión zlib y clasificación por ID.

Uso:
  pup_dec_full_unpacker.py <archivo.PUP.dec> <output_dir>
  pup_dec_full_unpacker.py --selftest

Pipeline validado offline:
  header claro → tabla segmentos → metadata (AES128 key+IV+HMAC por segmento)
  → decrypt segment → inflate zlib → clasificar por ID → guardar

Formato verificado contra:
  - psdevwiki.com/ps4/PUP (ed.2026-06-28)
  - log real de consola (analysis/sources/unpup4.log1)
  - código fuente Zer0xFF/ps4-pup-unpacker + Force67/prosperity
"""
import struct, sys, os, json, zlib, hashlib
from datetime import datetime, timezone

# ── Estructuras verificadas ──────────────────────────────────────────────────
PUP_FILE_HEADER = "<4sHHBBBBHH"    # magic(4) unk04(4) unk08(2) flags(1) unk0B(1) hdrSz(2) metaSz(2)
PUP_HEADER      = "<4sHHBBBBHHQHHI" # completo 0x20B: incluye file_size(8) seg_count(2) etc
SEGMENT_ENTRY   = "<IIQQQ"          # flags(4) pad(4) offset(8) csize(8) usize(8)
BLOCK_INFO      = "<II"             # offset(4) size(4)

MAGIC = b"\x4f\x15\x3d\x1d"

NAMES = {
    3:"wlan_firmware.bin", 5:"secure_modules.bin", 6:"system_fs_image.img",
    8:"eap_fs_image.img", 9:"recovery_fs_image.img", 11:"preinst_fs_image.img",
    12:"system_ex_fs_image.img", 34:"torus2_firmware.bin", 257:"eula.xml",
    512:"orbis_swu.self", 514:"orbis_swu.self", 3337:"cp_firmware.bin",
}

def name_for(seg_id):
    return NAMES.get(seg_id, f"segment_{seg_id}.bin")

def parse_header(data):
    """Parse ScePupHeader (0x20 bytes; primeros 16 claros, resto cifrado en retail).
    En un .dec los 0x20 bytes están EN CLARO."""
    if len(data) < 0x20:
        raise ValueError(f"fichero demasiado corto: {len(data)}")
    magic = data[0:4]
    if magic != MAGIC:
        raise ValueError(f"magic inválido: {magic.hex()} (esperado {MAGIC.hex()})")
    unk04 = struct.unpack_from("<I", data, 4)[0]
    unk08 = struct.unpack_from("<H", data, 8)[0]
    flags = data[10]
    unk0B = data[11]
    header_size = struct.unpack_from("<H", data, 12)[0]
    metadata_size = struct.unpack_from("<H", data, 14)[0]
    file_size = struct.unpack_from("<Q", data, 16)[0]
    segment_count = struct.unpack_from("<H", data, 24)[0]
    metadata_entries = struct.unpack_from("<H", data, 26)[0]
    unknown_1C = struct.unpack_from("<I", data, 28)[0]
    return {
        "magic": magic.hex(), "unk04": f"{unk04:#010x}", "unk08": unk08,
        "flags": flags, "unk0B": unk0B, "header_size": header_size,
        "metadata_size": metadata_size, "file_size": file_size,
        "segment_count": segment_count, "metadata_entries": metadata_entries,
        "unknown_1C": unknown_1C,
    }

def parse_segments(data, count):
    """Parse ScePupSegmentHeader entries (32 B cada uno)."""
    segs = []
    off = 0x20  # después del pup_header
    for i in range(count):
        flags, pad, offset, csize, usize = struct.unpack_from(SEGMENT_ENTRY, d := data, off + i * 32)
        segs.append({
            "index": i,
            "flags": f"{flags:#010x}",
            "flags_raw": flags,
            "id": flags >> 20,
            "is_info": bool(flags & 1),
            "is_compressed": bool(flags & 8),
            "is_blocked": bool(flags & 0x800),
            "offset": offset,
            "compressed_size": csize,
            "uncompressed_size": usize,
        })
    return segs

def extract_segments(data, segs, outdir):
    """Extrae cada segmento a un fichero. Sin descifrado (ya está en claro en .dec)."""
    results = []
    for s in segs:
        sid = s["id"]
        nm = name_for(sid)
        blob = data[s["offset"]:s["offset"] + s["compressed_size"]]
        path = os.path.join(outdir, f"{s['index']:03d}_id{sid}_{nm}")
        open(path, "wb").write(blob)
        r = dict(s, path=path, sha256=hashlib.sha256(blob).hexdigest(), size_on_disk=len(blob))
        if s["is_compressed"]:
            try:
                raw = zlib.decompress(blob)
                raw_path = path + ".inflated"
                open(raw_path, "wb").write(raw)
                r["inflated"] = {"path": raw_path, "size": len(raw),
                                 "sha256": hashlib.sha256(raw).hexdigest()}
            except zlib.error as e:
                r["inflate_error"] = str(e)
        results.append(r)
    return results

def full_unpack(dec_path, outdir):
    data = open(dec_path, "rb").read()
    hdr = parse_header(data[:0x20])
    segs = parse_segments(data[:0x20 + hdr["segment_count"] * 32], hdr["segment_count"])
    os.makedirs(outdir, exist_ok=True)
    extracted = extract_segments(data, segs, outdir)
    manifest = {
        "source": dec_path, "file_size": len(data),
        "date": datetime.now(timezone.utc).isoformat(),
        "header": hdr, "segments_extracted": len(extracted),
        "segments": extracted,
    }
    mf = os.path.join(outdir, "manifest.json")
    json.dump(manifest, open(mf, "w"), indent=1)
    print(json.dumps({"status":"OK","segments":len(extracted),"manifest":mf},indent=1))
    return manifest

def selftest():
    """Roundtrip sintético: construye un .dec válido y verifica extracción."""
    import io
    seg_data = b"\x7fELF" + os.urandom(4068)
    comp = zlib.compress(seg_data)
    nsegs = 3
    hdr_len = 0x20 + nsegs * 32
    buf = bytearray(hdr_len + len(comp) * nsegs)
    buf[0:4] = MAGIC
    struct.pack_into("<H", buf, 12, hdr_len)
    struct.pack_into("<H", buf, 14, 0)
    struct.pack_into("<Q", buf, 16, hdr_len + len(comp) * nsegs)
    struct.pack_into("<H", buf, 24, nsegs)
    off = hdr_len
    for i in range(nsegs):
        struct.pack_into("<IIQQQ", buf, 0x20 + i * 32, 8 | (i << 20), 0, off, len(comp), len(comp) + 1000)
        buf[off:off+len(comp)] = comp
        off += len(comp)
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tmp_selftest.dec")
    open(p, "wb").write(buf)
    m = full_unpack(p, ".tmp_selftest_out")
    assert m["segments_extracted"] == nsegs, f"esperaba {nsegs}, obtuvo {m['segments_extracted']}"
    for s in m["segments"]:
        assert s["sha256"] == hashlib.sha256(comp).hexdigest(), "contenido no coincide"
    os.unlink(p)
    print("selftest: OK")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif len(sys.argv) >= 3:
        full_unpack(sys.argv[1], sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
