#!/usr/bin/env python3
"""Unit tests for the original-binary multiplayer outcome semantics matrix."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "winui_safe_copy_online_multiplayer_outcome_semantics_matrix_check.py"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def load_checker():
    assert CHECKER.is_file(), f"missing checker: {CHECKER}"
    import winui_safe_copy_online_multiplayer_outcome_semantics_matrix_check as checker

    return checker


def expect_failure(checker, value: dict, expected: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "matrix.json"
        write_json(path, value)
        try:
            checker.validate_contract(path)
        except checker.MultiplayerOutcomeSemanticsMatrixError as exc:
            if expected not in str(exc):
                raise AssertionError(f"expected {expected!r} in {exc!s}") from exc
            return
    raise AssertionError(f"expected failure containing {expected!r}")


def main() -> int:
    checker = load_checker()
    good = checker.read_json(checker.CONTRACT)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "matrix.json"
        write_json(path, good)
        checker.validate_contract(path)

    bad = json.loads(json.dumps(good))
    bad["selectedRuntimeCandidate"]["levelId"] = 851
    expect_failure(checker, bad, "selected runtime candidate")

    bad = json.loads(json.dumps(good))
    bad["candidateLevels"][1]["levelWonLooseScriptRows"] = 1
    expect_failure(checker, bad, "loose LevelWon/LevelLost rows")

    bad = json.loads(json.dumps(good))
    bad["runtimeProofBoundary"]["versusModeRuntimeProof"] = True
    expect_failure(checker, bad, "versusModeRuntimeProof")

    bad = json.loads(json.dumps(good))
    bad["runtimeProofBoundary"]["baseOnlineMultiplayerReady"] = True
    expect_failure(checker, bad, "baseOnlineMultiplayerReady")

    bad = json.loads(json.dumps(good))
    bad["runtimeProofBoundary"]["nPlayerOriginalBinaryRuntimeProof"] = 1
    expect_failure(checker, bad, "nPlayerOriginalBinaryRuntimeProof")

    bad = json.loads(json.dumps(good))
    bad["requiredRuntimeHookTargets"].pop("CGame__MPDeclarePlayerWon")
    expect_failure(checker, bad, "CGame__MPDeclarePlayerWon")

    print("WinUI original-binary multiplayer outcome semantics matrix checker tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
