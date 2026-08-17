#!/usr/bin/env python3
"""Integrate new static OSINT findings without promoting unsupported evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBKIT = ROOT / "analysis" / "webkit_13.52_research.json"
INDIRECT = ROOT / "analysis" / "github_indirect_findings_13.52.json"
ARTIFACT = ROOT / "analysis" / "github_downloaded_artifacts_13.52.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_unique(items: list[dict], item: dict, key: tuple[str, str]) -> None:
    if not any((x.get(key[0]), x.get(key[1])) == (item.get(key[0]), item.get(key[1])) for x in items):
        items.append(item)


def main() -> None:
    webkit = load(WEBKIT)
    indirect = load(INDIRECT)
    artifacts = load(ARTIFACT)

    for doc in (webkit, indirect, artifacts):
        vocab = doc.setdefault("classification_vocabulary", [])
        if "VERIFIED_METADATA" not in vocab:
            vocab.append("VERIFIED_METADATA")

    leandro_history = {
        "repo": "Leandrobts/Host",
        "classification": "STRUCTURAL",
        "artifact_status": "ABSENT",
        "contribution": "Historical blob evolution shows the public 13.52.js began as a 463-byte placeholder and grew through public commits; no decrypted modules, hashes, logs or build IDs were published.",
        "provenance": "https://github.com/Leandrobts/Host",
        "commits": [
            "2b973f7ef20aa3920ed70bf3cfdf4f90cd003953",
            "a0409e966739676f9395bba0de8b77a2a67d8590",
            "8fae6357d4a93cf461b32259320e1f12b6d147c6",
            "aab51818a25ed1119141d1fad5ff64e734c88b48",
            "c3b181fefeb130983dcd891f716b1bc02ea61b44",
            "ba5f35570a6c836687c630e592e9e96966108876",
            "b2a1fca690dced722217e7bccd96aa0497dd4aac",
            "44b1030ca65f551794573ffb5350981eb10888fd",
            "d418755d1c7b4807aa2e53b9b665307ddfafa372",
            "4647873f1bc999e1019a06801dcb4abf4fce13e2",
            "5c469e9bf9ab5844b8247c327d7016fa89621656",
        ],
        "blob_evolution": [
            {"commit": "a0409e966739676f9395bba0de8b77a2a67d8590", "size": 463, "sha256": "93193f55d2a15a888121d1fdadd19db019bc23d1aed421c69743d8befd190269", "note": "initial placeholder table"},
            {"commit": "8fae6357d4a93cf461b32259320e1f12b6d147c6", "size": 529, "sha256": "99410c04f8394313a1dc2b6059d5abb71cf090fd5f60cc9370adfcde6a97070b", "note": "mostly zero TODO fields; host constructor candidate"},
            {"commit": "44b1030ca65f551794573ffb5350981eb10888fd", "size": 1667, "sha256": "c08fa03b38c9ed1e27a959a7d8aa72b38e70c24c8eea60a98ac686670b2f977d", "note": "first larger offset/comment expansion"},
            {"commit": "d418755d1c7b4807aa2e53b9b665307ddfafa372", "size": 1668, "sha256": "c3691e84e5da5a9c4735d11d713f961350407bcc9bda8a556f601ec0efaa5d58", "note": "minor revision"},
            {"commit": "4647873f1bc999e1019a06801dcb4abf4fce13e2", "size": 1896, "sha256": "16b44109386e44dc00dd378e2d9b6c3f6f6eb59451919b8872fadbff89c2f267", "note": "comments and offset adjustments"},
            {"commit": "5c469e9bf9ab5844b8247c327d7016fa89621656", "size": 11820, "sha256": "d924361c4616a1ab05c785fa21cc98b26c1ed3eb73b670ef117a5010978eff45", "note": "current public table"},
        ],
        "not_accepted_as": "DIRECT_BYTES or VERIFIED_METADATA for the three cited retail modules",
    }
    append_unique(webkit.setdefault("github_deep_audit_additions", []), leandro_history, ("repo", "classification"))

    social = {
        "repo": "GamerHack/GamerHack.github.io",
        "classification": "DOCUMENTATION",
        "artifact_status": "ABSENT",
        "contribution": "Public host and README explicitly stop at PS4 11.02; the Aug 10 X post says CSSFontFace was added only for 10.xx-11.02.",
        "provenance": "https://github.com/GamerHack/GamerHack.github.io",
        "commit": "e00f40ab52d965ca73ef968bf06bc0da17cad157",
        "not_accepted_as": "13.52 WebKit implementation or binary artifact",
    }
    append_unique(webkit.setdefault("github_deep_audit_additions", []), social, ("repo", "classification"))

    gist = {
        "repo": "hasyimy-ctrl/a79460845e7268785c8129e18b00655a",
        "url": "https://gist.github.com/hasyimy-ctrl/a79460845e7268785c8129e18b00655a",
        "commit": "ea43af2001ccf0d3a2b1220f98db0eeb663b935a",
        "classification": "UNVERIFIED",
        "artifact_status": "VERIFIED_METADATA",
        "firmware_claim": "PS4 13.52",
        "file": {
            "path": "rtsock_exploit.c",
            "size": 1974,
            "sha256": "a0bf7271b62dd009b862ee68e94c3f23b236e232b72e677649687490de186de2",
            "raw_url": "https://gist.githubusercontent.com/hasyimy-ctrl/a79460845e7268785c8129e18b00655a/raw/71127c98a3a5bb2026dab26df91a621f7f2f3bdc/rtsock_exploit.c",
        },
        "contribution": "Single-file hypothesis applying FreeBSD CVE-2026-3038/rtsock_msg_buffer to Orbis; no kernel bytes, log, build ID, hash or reproduction.",
        "upstream_contrast": "Official FreeBSD advisory and NVD scope FreeBSD 13.5/14.3/15.0; neither mentions PS4/Orbis.",
        "not_accepted_as": "kernel 13.52 bytes, confirmed UAF/overflow, or WebKit-to-kernel chain",
    }
    append_unique(indirect.setdefault("new_sources", []), gist, ("repo", "commit"))
    append_unique(artifacts.setdefault("artifacts", []), gist, ("repo", "commit"))

    # Preserve the existing confirmed anchor and make the new bottleneck explicit.
    webkit["next_best_artifact"] = {
        "name": "libSceNKWebKit_sprx.decrypted or the exact ufm42/rtfonto snapshot",
        "classification_until_obtained": "ABSENT",
        "required_properties": [
            "publicly downloadable bytes",
            "same-build provenance",
            "SHA-256 and size",
            "ELF64/SELF metadata, .text and PT_SCE_RELRO",
            "build ID or equivalent identity",
        ],
    }

    dump(WEBKIT, webkit)
    dump(INDIRECT, indirect)
    dump(ARTIFACT, artifacts)
    print("updated", WEBKIT, INDIRECT, ARTIFACT)


if __name__ == "__main__":
    main()
