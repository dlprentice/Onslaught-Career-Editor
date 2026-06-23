#!/usr/bin/env python3
"""Validate active patch-catalog accounting docs against patches.v2.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "patches" / "catalog" / "patches.v2.json"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
PATCH_README = ROOT / "patches" / "README.md"
CURRENT_CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CURRENT_CAPABILITIES_LORE = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
STATE_FILES = (
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
)
TARGET_HASH = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
TARGET_SIZE = 2_506_752
REQUIRED_POLICY_FIELDS = (
    "dependencies",
    "conflicts",
    "exclusive_group",
    "proof_level",
    "selectability",
    "preset_eligibility",
    "requires_windowed_pair",
)
STALE_PHRASES = (
    "25/25 rows",
    "25/25 target",
    "18 visible",
    "18/18 visible",
    "validated and ready for commit/push",
    "Commit/push the validated free-camera Q-pitch remap proof slice",
)


class AccountingError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AccountingError(message)


def read_catalog() -> list[dict[str, Any]]:
    value = json.loads(CATALOG.read_text(encoding="utf-8"))
    rows = value.get("patches")
    require(isinstance(rows, list), "patch catalog must contain a patches array")
    require(all(isinstance(row, dict) for row in rows), "patch catalog rows must be objects")
    return rows


def is_hidden(row: dict[str, Any]) -> bool:
    return str(row.get("selectability", "")).lower() == "hidden_companion"


def track_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        track = str(row.get("track", "")).lower()
        counts[track] = counts.get(track, 0) + 1
    return counts


def assert_catalog_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [str(row.get("id", "")) for row in rows]
    require(len(ids) == len(set(ids)), "patch catalog contains duplicate ids")
    require(all(ids), "patch catalog contains a row without an id")

    identity_rows = [
        row
        for row in rows
        if row.get("target_binary_hashes") == [TARGET_HASH]
        and row.get("target_binary_size") == TARGET_SIZE
    ]
    policy_rows = [
        row
        for row in rows
        if all(field in row for field in REQUIRED_POLICY_FIELDS)
        and isinstance(row.get("dependencies"), list)
        and isinstance(row.get("conflicts"), list)
        and isinstance(row.get("preset_eligibility"), list)
        and isinstance(row.get("requires_windowed_pair"), bool)
    ]
    visible = [row for row in rows if not is_hidden(row)]
    visible_tracks = track_counts(visible)
    all_tracks = track_counts(rows)

    require(len(identity_rows) == len(rows), "not every catalog row has canonical target specimen identity")
    require(len(policy_rows) == len(rows), "not every catalog row has required policy metadata")
    require(visible_tracks.get("stable", 0) + visible_tracks.get("experimental", 0) == len(visible), "visible rows must be stable or experimental")

    return {
        "total": len(rows),
        "visible": len(visible),
        "hidden": len(rows) - len(visible),
        "allTracks": all_tracks,
        "visibleTracks": visible_tracks,
        "identityRows": len(identity_rows),
        "policyRows": len(policy_rows),
    }


def assert_register(summary: dict[str, Any]) -> None:
    text = REGISTER.read_text(encoding="utf-8")
    expected_snippets = [
        f"| Visible executable patch options | `{summary['visible']} visible options: {summary['visibleTracks']['stable']} stable, {summary['visibleTracks']['experimental']} experimental`",
        f"| Patch-row proof clarity | `{summary['visible']}/{summary['visible']} visible rows with proof drawer fields`",
        f"| Catalog rows with target specimen identity | `{summary['total']}/{summary['total']} rows`",
        f"| Catalog rows with policy metadata | `{summary['total']}/{summary['total']} rows`",
        f"policy metadata for all {summary['total']} rows",
    ]
    missing = [snippet for snippet in expected_snippets if snippet not in text]
    require(not missing, "register missing expected accounting snippets: " + "; ".join(missing))
    for phrase in ("25/25 rows", "25/25 target", "18 visible", "18/18 visible", "all 14 rows"):
        require(phrase not in text, f"register contains stale phrase: {phrase}")


def assert_public_markers(summary: dict[str, Any]) -> None:
    marker = (
        f"Current patch catalog accounting: {summary['total']} total rows; "
        f"{summary['visible']} visible options "
        f"({summary['visibleTracks']['stable']} stable, {summary['visibleTracks']['experimental']} experimental); "
        f"{summary['hidden']} hidden companions."
    )
    for path in (PATCH_README, CURRENT_CAPABILITIES):
        text = path.read_text(encoding="utf-8")
        require(marker in text, f"{path.relative_to(ROOT)} missing current patch catalog accounting marker")
    if CURRENT_CAPABILITIES_LORE.exists():
        text = CURRENT_CAPABILITIES_LORE.read_text(encoding="utf-8")
        require(marker in text, f"{CURRENT_CAPABILITIES_LORE.relative_to(ROOT)} missing current patch catalog accounting marker")


def assert_state(summary: dict[str, Any]) -> None:
    expected_visible = f"{summary['visible']} visible options: {summary['visibleTracks']['stable']} stable, {summary['visibleTracks']['experimental']} experimental"
    expected_catalog = f"{summary['total']}/{summary['total']} target specimen identity and policy metadata rows"
    for path in STATE_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in STALE_PHRASES:
            require(phrase not in text, f"{path.name} contains stale phrase: {phrase}")
        state = json.loads(text)
        counters = state.get("currentCounters", {})
        require(counters.get("visiblePatchRows") == expected_visible, f"{path.name} visiblePatchRows is stale")
        require(counters.get("catalogRows") == expected_catalog, f"{path.name} catalogRows is stale")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate patch catalog accounting.")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    try:
        summary = assert_catalog_rows(read_catalog())
        assert_register(summary)
        assert_public_markers(summary)
        assert_state(summary)
    except AccountingError as exc:
        print(f"WinUI patch catalog accounting check: FAIL: {exc}")
        return 1

    print(
        json.dumps(
            {
                "status": "PASS",
                "totalRows": summary["total"],
                "visibleRows": summary["visible"],
                "hiddenRows": summary["hidden"],
                "visibleTracks": summary["visibleTracks"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
