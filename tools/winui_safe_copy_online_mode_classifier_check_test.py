#!/usr/bin/env python3
"""Unit tests for the original-binary online mode classifier checker."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import winui_safe_copy_online_mode_classifier_check as checker


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def expect_failure(value: dict, expected: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "contract.json"
        write_json(path, value)
        try:
            checker.validate_contract(path)
        except checker.ModeClassifierError as exc:
            if expected not in str(exc):
                raise AssertionError(f"expected {expected!r} in {exc!s}") from exc
            return
    raise AssertionError(f"expected failure containing {expected!r}")


def main() -> int:
    good = checker.read_json(checker.CONTRACT)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "contract.json"
        write_json(path, good)
        checker.validate_contract(path)

    bad = json.loads(json.dumps(good))
    bad["currentRuntimeModeClassification"]["modeClass"] = "versus-free-for-all"
    expect_failure(bad, "unclassified local multiplayer")

    bad = json.loads(json.dumps(good))
    bad["proofBoundary"]["versusModeRuntimeProof"] = True
    expect_failure(bad, "versusModeRuntimeProof")

    bad = json.loads(json.dumps(good))
    bad["proofBoundary"]["publicMatchmakingProof"] = True
    expect_failure(bad, "publicMatchmakingProof")

    bad = json.loads(json.dumps(good))
    bad["plannedModeFamilies"][0]["runtimeProof"] = True
    expect_failure(bad, "runtime proof overclaim")

    bad = json.loads(json.dumps(good))
    bad["plannedModeFamilies"][2].pop("teamAssignmentAuthority", None)
    expect_failure(bad, "team authority")

    bad = json.loads(json.dumps(good))
    bad["rejectionCases"] = ["reject cooperative runtime proof from sessionType alone"]
    expect_failure(bad, "modeFamily alone")

    bad = json.loads(json.dumps(good))
    bad["nonClaims"]["nativeBeaNetcodeProof"] = True
    expect_failure(bad, "nativeBeaNetcodeProof")

    print("WinUI original-binary online mode classifier checker tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
