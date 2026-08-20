#!/usr/bin/env python3
"""Static comparison of PS4 blobs; no loading, execution, or exploit offsets."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

TARGET_STRINGS = (
    b"libkernel_web",
    b"libSceLibcInternal",
    b"libSceNKWebKit",
    b"WebKit",
    b"SceShell",
    b"ORBISDMP",
    b"NXDP",
)


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def string_hits(data: bytes) -> list[dict[str, object]]:
    hits = []
    for match in re.finditer(rb"[ -~]{6,}", data):
        value = match.group().decode("ascii", "replace")
        if any(token.lower() in value.lower().encode() for token in TARGET_STRINGS):
            hits.append({"offset": match.start(), "value": value[:240]})
    return hits[:200]


def find_occurrences(haystack: bytes, needle: bytes) -> list[int]:
    if not needle or len(needle) > len(haystack):
        return []
    result = []
    start = 0
    while True:
        offset = haystack.find(needle, start)
        if offset < 0:
            return result
        result.append(offset)
        start = offset + 1


def pairwise(a: bytes, b: bytes) -> dict[str, object]:
    n = min(len(a), len(b))
    equal = sum(x == y for x, y in zip(a[:n], b[:n]))
    prefix = 0
    while prefix < n and a[prefix] == b[prefix]:
        prefix += 1
    suffix = 0
    while suffix < n - prefix and a[-1 - suffix] == b[-1 - suffix]:
        suffix += 1
    return {
        "same_size": len(a) == len(b),
        "compared_bytes": n,
        "equal_byte_count": equal,
        "equal_fraction": round(equal / n, 8) if n else 1.0,
        "common_prefix_bytes": prefix,
        "common_suffix_bytes": suffix,
        "same_sha256": hashlib.sha256(a).digest() == hashlib.sha256(b).digest(),
    }


def aligned_word_summary(data: bytes) -> dict[str, int]:
    # Generic structural counts only; values are not emitted as addresses/offsets.
    canonical = aligned = 0
    for offset in range(0, len(data) - 7, 8):
        value = int.from_bytes(data[offset : offset + 8], "little")
        if value == 0 or value == 0xFFFFFFFFFFFFFFFF:
            continue
        if value % 8 == 0:
            aligned += 1
        if (value >> 48) in (0, 0xFFFF):
            canonical += 1
    return {"nontrivial_aligned_u64_count": aligned, "canonical_like_u64_count": canonical}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    records = []
    data_by_name: dict[str, bytes] = {}
    for path in args.files:
        data = path.read_bytes()
        name = path.name
        data_by_name[name] = data
        records.append({
            "name": name,
            "path": str(path.resolve()),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "entropy_bits_per_byte": round(entropy(data), 8),
            "target_string_hits": string_hits(data),
            "generic_aligned_word_summary": aligned_word_summary(data),
            "classification": "DIRECT_BYTES",
            "static_only": True,
        })
    pairs = {}
    names = list(data_by_name)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            comparison = pairwise(data_by_name[left], data_by_name[right])
            if len(data_by_name[left]) >= len(data_by_name[right]):
                comparison["right_as_contiguous_substring_offsets_in_left"] = find_occurrences(data_by_name[left], data_by_name[right])
            else:
                comparison["left_as_contiguous_substring_offsets_in_right"] = find_occurrences(data_by_name[right], data_by_name[left])
            pairs[f"{left}__{right}"] = comparison
    report = {
        "schema": "ps4-1352-blob-comparison-v2",
        "scope": "byte-level and generic structural comparison only; no execution or exploit offsets",
        "records": records,
        "pairwise": pairs,
        "conclusion_guardrail": "Byte similarity or shared strings does not establish firmware, module, or WebKit identity without provenance and format metadata.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
