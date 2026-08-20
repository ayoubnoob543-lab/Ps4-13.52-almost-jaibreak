#!/usr/bin/env python3
"""Compare an explicit WPE smoke result against the fixture contract."""
from __future__ import annotations

import argparse
import json
import pathlib


CAPABILITY_MAP = {
    "dom": "dom",
    "css": "css",
    "flex": "flex",
    "grid": "grid",
    "javascript": "javascript",
    "events": "events",
    "forms": "forms",
    "svg": "svg",
    "images": "images",
    "canvas": "canvas",
    "localstorage": "localstorage",
    "navigation": "navigation",
    "history": "history",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result")
    parser.add_argument("--expected", default=str(pathlib.Path(__file__).resolve().parents[1] / "homebrew/fixtures/wpe-expected-assertions.json"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    actual_result = json.loads(pathlib.Path(args.result).read_text(encoding="utf-8"))
    expected = json.loads(pathlib.Path(args.expected).read_text(encoding="utf-8"))
    comparison = {"schema": 1, "status": "NOT_RUN", "reason": None, "stages": {}, "capabilities": {}, "sequence": {"expected": expected["sequence"], "actual": None, "status": "NOT_RUN"}}
    actual = actual_result.get("actual_assertions")
    if actual is None:
        comparison["reason"] = "no explicit actual assertions; source result remains " + actual_result.get("status", "UNKNOWN")
    else:
        comparison["sequence"]["actual"] = [stage for stage in expected["sequence"] if stage in actual]
        comparison["sequence"]["status"] = "PASS" if comparison["sequence"]["actual"] == expected["sequence"] else "FAIL"
        for stage, expected_values in expected["stages"].items():
            actual_values = actual.get(stage)
            stage_result = {"status": "PASS", "expected": expected_values, "actual": actual_values, "capabilities": {}}
            if not isinstance(actual_values, dict):
                stage_result["status"] = "FAIL"
                stage_result["reason"] = "stage missing or not an object"
            else:
                for key, expected_value in expected_values.items():
                    if key not in actual_values:
                        capability_status = "FAIL"
                    else:
                        capability_status = "PASS" if actual_values[key] == expected_value else "FAIL"
                    stage_result["capabilities"][CAPABILITY_MAP.get(key, key)] = {"status": capability_status, "expected": expected_value, "actual": actual_values.get(key)}
                    previous = comparison["capabilities"].get(CAPABILITY_MAP.get(key, key))
                    if previous is None or capability_status == "FAIL":
                        comparison["capabilities"][CAPABILITY_MAP.get(key, key)] = {"status": capability_status, "stages": [stage]}
                    else:
                        previous["stages"].append(stage)
                    if capability_status == "FAIL":
                        stage_result["status"] = "FAIL"
            comparison["stages"][stage] = stage_result
        all_pass = comparison["sequence"]["status"] == "PASS" and all(item["status"] == "PASS" for item in comparison["stages"].values())
        comparison["status"] = "PASS" if all_pass else "FAIL"
        comparison["reason"] = "all expected stages and capabilities matched" if all_pass else "one or more expected assertions failed"
    pathlib.Path(args.output).write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0 if comparison["status"] in {"PASS", "NOT_RUN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
