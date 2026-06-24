#!/usr/bin/env python3
"""Tests for the copied-runtime controller mapping-table artifact checker."""

from __future__ import annotations

import tempfile
from pathlib import Path

import winui_safe_copy_controller_mapping_table_artifact_check as checker


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        artifact = checker.make_artifact(Path(temp_dir), include_o_pause=True)
        summary = checker.validate_artifact(artifact)
        require(summary["mappingTable"]["rowCount"] == 2, "expected two decoded rows before sentinel")
        require(summary["mappingTable"]["sentinelFound"] is True, "expected sentinel row")
        require(summary["mappingTable"]["pauseRows"][0]["slot0"]["keyArg"] == 0x18, "expected O scan-style key argument in pause slot")
        require(summary["oPauseClassification"] == "runtime-table-o-pause-slot-present", "expected O pause slot classification")

    with tempfile.TemporaryDirectory() as temp_dir:
        artifact = checker.make_artifact(Path(temp_dir), include_o_pause=False)
        summary = checker.validate_artifact(artifact)
        require(summary["mappingTable"]["pauseRows"][0]["slot0"]["keyArg"] == 1, "expected non-O key argument in pause slot")
        require(
            summary["oPauseClassification"] == "runtime-table-pause-row-present-without-o-slot",
            "expected pause row without O slot classification",
        )

    print("WinUI safe-copy controller mapping-table artifact checker tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
