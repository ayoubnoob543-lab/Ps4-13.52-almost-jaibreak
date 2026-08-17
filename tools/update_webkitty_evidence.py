#!/usr/bin/env python3
"""Integrate static provenance findings without promoting them to binary evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "analysis" / "webkit_13.52_research.json"
REPOS = ROOT / "analysis" / "research_repos_13.52.json"


def add_once(items: list[dict], item: dict, key: str = "repo") -> None:
    if not any(existing.get(key) == item.get(key) for existing in items):
        items.append(item)


def main() -> None:
    research = json.loads(RESEARCH.read_text(encoding="utf-8"))
    additions = research.setdefault("github_deep_audit_additions", [])
    add_once(additions, {
        "repo": "ntfargo/CSSFontFace-Exploit",
        "commit": "221baa6e7349b96a6fd299808a25a4178e47741c",
        "classification": "STRUCTURAL",
        "artifact_status": "ABSENT",
        "contribution": "Public CSSFontFace implementation and explicit documentation that the PS4 chain is 6.00-11.02 while the vulnerability scope is declared through 13.52; newer 11.5x+ layout introduces m_propertiesOrCSSConnection and invalidates the historical m_featureSettings primitive.",
        "provenance": "https://github.com/ntfargo/CSSFontFace-Exploit",
        "not_accepted_as": "13.52 WebKit bytes, offsets, vtables, gadgets, or runtime compatibility"
    })
    add_once(additions, {
        "repo": "ArabPixel/WebKitty",
        "commit": "074463f5e2dfea65b692a33110a5fd31238053f3",
        "classification": "STRUCTURAL",
        "artifact_status": "ABSENT",
        "contribution": "Complete public exploit host; current README and firmware-based manifests keep CSSFontFace+Lapse/NetCtrl at 9.00-11.02. August 2026 commits change cache, UI, navigation and payload paths, not a 13.52 WebKit implementation.",
        "provenance": "https://github.com/ArabPixel/WebKitty",
        "not_accepted_as": "13.52 WebKit/libkernel_web/libc/kernel bytes or functional chain"
    })
    research["next_best_artifact"] = {
        "name": "libSceNKWebKit.sprx 13.52 or the exact private WebKitty/ufm42 13.52 source snapshot",
        "required_properties": ["same-build provenance", "SHA-256", "ELF64/SELF metadata or exact source commit", ".text", "PT_SCE_RELRO or equivalent", "build identity"],
        "action": "obtain and statically verify the artifact before changing any CSSFontFace layout or offset classification",
        "classification_until_obtained": "ABSENT"
    }
    research["research_result"] = (
        "New public provenance was audited through ntfargo/CSSFontFace-Exploit and ArabPixel/WebKitty. "
        "Both corroborate the public 11.02 implementation boundary and the 13.52 claim, but neither provides a verified 13.52 module or source snapshot."
    )
    RESEARCH.write_text(json.dumps(research, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    repos = json.loads(REPOS.read_text(encoding="utf-8"))
    repo_items = repos.setdefault("repositories", [])
    add_once(repo_items, {
        "repo": "ntfargo/CSSFontFace-Exploit",
        "url": "https://github.com/ntfargo/CSSFontFace-Exploit",
        "head_commit": "221baa6e7349b96a6fd299808a25a4178e47741c",
        "branch": "main",
        "files_scanned": "complete clone; public source and historical patches",
        "firmware_identified": "vulnerability scope declared 6.00-13.52; published chain 6.00-11.02",
        "artifact_types": ["JavaScript source", "historical PS4 patch blobs"],
        "module_presence": {"WebKit": "STRUCTURAL source", "libkernel_web": "ABSENT", "libSceLibcInternal": "ABSENT", "kernel": "ABSENT", "SELF": "ABSENT", "SPRX": "ABSENT"},
        "sha256": [],
        "classification": "STRUCTURAL",
        "reason": "Complete public source clone and commit history explicitly document the newer WebKit layout change, but no 13.52 retail module or source snapshot is present.",
        "notes": "No repository code or payload was executed."
    })
    add_once(repo_items, {
        "repo": "ArabPixel/WebKitty",
        "url": "https://github.com/ArabPixel/WebKitty",
        "head_commit": "074463f5e2dfea65b692a33110a5fd31238053f3",
        "branch": "main",
        "files_scanned": "complete clone; 173 commits and August 2026 history",
        "firmware_identified": "functional CSSFontFace chain 9.00-11.02; UI also lists newer firmware payload choices",
        "artifact_types": ["exploit host source", "historical patch blobs", "payload files"],
        "module_presence": {"WebKit": "STRUCTURAL source", "libkernel_web": "ABSENT", "libSceLibcInternal": "ABSENT", "kernel": "ABSENT", "SELF": "ABSENT", "SPRX": "ABSENT"},
        "sha256": [],
        "classification": "STRUCTURAL",
        "reason": "Complete host clone and commit history link ufm42/ntfargo CSSFontFace work while README limits the tested chain to 9.00-11.02; August changes are cache/UI/navigation updates.",
        "notes": "No repository code or payload was executed; no 13.52 module bytes were found."
    })
    repos["repo_count"] = len(repo_items)
    repos["total_audited_clones_including_additions"] = len(repo_items) + int(repos.get("additional_github_audit_repositories", 0))
    repos["new_13_52_binary_artifacts_confirmed"] = 0
    summary = repos.setdefault("research_summary", {})
    summary["verified_repo_count"] = len(repo_items)
    summary["cloned_repo_count"] = len(repo_items)
    summary["new_13_52_binary_artifacts_confirmed"] = 0
    REPOS.write_text(json.dumps(repos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
