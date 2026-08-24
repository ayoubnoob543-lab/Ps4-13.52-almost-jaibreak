#!/usr/bin/env python3
"""Clasificador PASS/FAIL/UNKNOWN sobre results/*.result.json"""
import json, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1] / "results"
summary = {}
for f in sorted(R.glob("*.result.json")):
    d = json.loads(f.read_text())
    summary[d["experiment"]] = {
        "status": d.get("status", "UNKNOWN"),
        "notes": d.get("_note_semsys") or d.get("note") or "",
    }
# reglas de composición
if summary.get("exp00_gate", {}).get("status") == "PASS":
    if summary.get("exp00_gate", {}).get("semctl_via_libkernel") == "FAIL":
        summary["_composition"] = {"semctl_path": "BLOCKED (no wrapper en libkernel)",
            "next": "solo vía syscall directo desde exec nativa JIT; requiere confirmar "
                    "sysvsem en kernel retail (bytes AUSENTES)"}
print(json.dumps(summary, indent=2))
(R/"pipeline_summary.json").write_text(json.dumps(summary, indent=2)+"\n")
