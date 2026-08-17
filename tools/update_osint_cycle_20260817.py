#!/usr/bin/env python3
"""Integrate static OSINT findings from the 2026-08-17 cycle.

This script only records provenance and evidence classification. It never
promotes source claims or payload bytes to retail 13.52 module evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBKIT = ROOT / "analysis" / "webkit_13.52_research.json"
REPOS = ROOT / "analysis" / "research_repos_13.52.json"

NEW = [
    {
        "repo": "Leandrobts/Host",
        "commit": "c6f66c7b0ba363e618da95c6f7a013c901a3c316",
        "classification": "STRUCTURAL",
        "artifact_status": "ABSENT",
        "contribution": (
            "Public 13.52.js resolver source; claims analysis of three decrypted modules "
            "but ships no WebKit/libkernel_web/libc artifacts, hashes, logs or build IDs. "
            "The current source is shared byte-for-byte with Leandrobts/Test."
        ),
        "provenance": "https://github.com/Leandrobts/Host",
        "not_accepted_as": "DIRECT_BYTES or VERIFIED_METADATA for 13.52 retail modules",
        "evidence": {
            "file": "13.52.js",
            "size": 11820,
            "sha256": "d924361c4616a1ab05c785fa21cc98b26c1ed3eb73b670ef117a5010978eff45",
            "module_claims": [
                "libSceNKWebKit_sprx.decrypted (~70 MB)",
                "libkernel_web_sprx.decrypted (~448 KB)",
                "libSceLibcInternal_sprx.decrypted (~1.5 MB)",
            ],
            "history": [
                "8fae6357d4a93cf461b32259320e1f12b6d147c6",
                "c3b181fefeb130983dcd891f716b1bc02ea61b44",
                "ba5f35570a6c836687c630e592e9e96966108876",
                "b2a1fca690dced722217e7bccd96aa0497dd4aac",
                "d418755d1c7b4807aa2e53b9b665307ddfafa372",
                "4647873f1bc999e1019a06801dcb4abf4fce13e2",
                "5c469e9bf9ab5844b8247c327d7016fa89621656",
            ],
        },
    },
    {
        "repo": "Leandrobts/Test",
        "commit": "24dd1e17dcca73098a025b583c2d73d8c7f5e79e",
        "classification": "STRUCTURAL",
        "artifact_status": "ABSENT",
        "contribution": (
            "Related host/resolver source. Shared 13.52.js and resources/main.js hashes with "
            "Leandrobts/Host; no standalone retail modules or reproducible dump."
        ),
        "provenance": "https://github.com/Leandrobts/Test",
        "not_accepted_as": "independent binary corroboration",
    },
    {
        "repo": "Gezine/BD-JB5",
        "commit": "4c28ff2d36cf9cade6763f2a8b801c2219e951f5",
        "classification": "STRUCTURAL",
        "artifact_status": "VERIFIED_METADATA_ONLY",
        "contribution": (
            "BD-J Poops source includes a 13.52 offset table and shellcode string; release 2.0 "
            "assets have verified GitHub digests, but none is a retail kernel/WebKit module."
        ),
        "provenance": "https://github.com/Gezine/BD-JB5",
        "not_accepted_as": "DIRECT_BYTES of the 13.52 kernel or WebKit",
        "evidence": {
            "source_commit": "fef9084ef18435cc451f2fb5039d88957ddc8f85",
            "release": "2.0",
            "assets": [
                {
                    "name": "BD-JB5-2.0.iso",
                    "size": 16777216,
                    "sha256": "88dec100489794cb3790f802511146cdc2e8c1fc3845a6347f8c2913908bbde4",
                    "format": "BDMV/BD-J ISO",
                },
                {
                    "name": "bdj_unpatch_1360.elf",
                    "size": 433704,
                    "sha256": "22bae58b6214832c99457d56fc97676ce8eef1d626fbaf50b6a69508e5c1e18e",
                    "format": "ELF64 PIE",
                },
                {
                    "name": "poops_1.8.jar",
                    "size": 178729,
                    "sha256": "96cf108e0a2fe38a7a644775f9775e09be69a0ccb138f8597453d59b6587ac03",
                    "format": "Java archive",
                },
            ],
        },
    },
    {
        "repo": "andleexploit/masticore-13.52",
        "commit": "1e890a84256f4a8a898eecad1c4834d65b9427a4",
        "classification": "DOCUMENTATION",
        "artifact_status": "ABSENT",
        "contribution": "Two-commit README-only claim; no source, binary, log, hash or compiler SELF.",
        "provenance": "https://github.com/andleexploit/masticore-13.52",
        "not_accepted_as": "mast1c0re 13.52 evidence",
    },
]


def merge_list(items: list[dict], key: str = "repo") -> None:
    by_key = {item.get(key): item for item in items if isinstance(item, dict) and item.get(key)}
    for item in NEW:
        if item[key] in by_key:
            by_key[item[key]].update(item)
        else:
            items.append(item)


def update(path: Path, kind: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if kind == "webkit":
        arr = data.setdefault("github_deep_audit_additions", [])
        merge_list(arr)
        if not isinstance(data.get("research_result"), dict):
            data["research_result_note"] = data.get("research_result")
            data["research_result"] = {}
        data["research_result"]["latest_cycle"] = {
            "date": "2026-08-17",
            "new_primary_lead": "Leandrobts/Host 13.52.js",
            "new_verified_retail_1352_binary": False,
            "coverage": {
                "github_candidate_repositories": 974,
                "github_queries": 108,
                "selected_cloned_files": 2652,
                "selected_clone_commits": 1875,
            },
        }
        data["next_best_artifact"] = {
            "name": "The three decrypted 13.52 modules cited by Leandrobts/Host, or the exact WebKit snapshot used by ufm42/rtfonto",
            "classification_until_obtained": "ABSENT",
            "required_properties": [
                "publicly downloadable bytes",
                "same-build provenance",
                "SHA-256 and size",
                "ELF64/SELF metadata, .text and PT_SCE_RELRO",
                "build ID or equivalent identity",
            ],
        }
    else:
        repos = data.setdefault("repositories", [])
        merge_list(repos)
        data["repo_count"] = len({item.get("repo") for item in repos if isinstance(item, dict) and item.get("repo")})
        if isinstance(data.get("research_summary"), dict):
            data["research_summary"]["verified_repo_count"] = data["repo_count"]
            data["research_summary"]["cloned_repo_count"] = data["repo_count"]
        if not isinstance(data.get("additional_github_audit_repositories"), list):
            data["additional_github_audit_repositories_count"] = data.get("additional_github_audit_repositories")
            data["additional_github_audit_repositories"] = []
        existing = {x.get("repo") for x in data["additional_github_audit_repositories"] if isinstance(x, dict)}
        for item in NEW:
            if item["repo"] not in existing:
                data["additional_github_audit_repositories"].append(item)
        data["latest_cycle_coverage"] = {
            "date": "2026-08-17",
            "candidate_repositories": 974,
            "search_queries": 108,
            "selected_full_clones": 12,
            "selected_tracked_files": 2652,
            "selected_commits": 1875,
            "selection_policy": "technical relevance, artifact/module terms, author provenance, recent activity, or recursive references; candidates were not auto-accepted",
        }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


update(WEBKIT, "webkit")
update(REPOS, "repos")
print("updated", WEBKIT)
print("updated", REPOS)
