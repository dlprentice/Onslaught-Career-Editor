#!/usr/bin/env python3
"""Validate the World / Thing / Spawn GetThingRef object-reference static proof."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MISSION_USAGE = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
SOURCE_SCHEMA = ROOT / "reverse-engineering" / "game-assets" / "world-thing-spawn-copied-corpus-schema.v1.json"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static.v1.json"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "world_thing_spawn_getthingref_object_reference_static_proof_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
MISSION_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
WORLD_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
CORPUS_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof.md"
SPAWNER_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static-proof.md"
QUICK_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
ISCRIPT_OWNER = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

SELECTED_LEVEL_DIRS = {("22", "level022"), ("100", "level100")}
SELECTED_THINGS = ("Target Zone 1", "Target Zone 2", "Target Zone 3", "Target Zone 4")

FORBIDDEN_PUBLIC_TOKENS = (
    "C:\\Users",
    "Program Files",
    ".env",
    "save-attempts",
    "onslaught_codex_directive",
    "password",
    "token=",
)

FORBIDDEN_OVERCLAIMS = (
    "runtime getthingref behavior proven",
    "runtime object identity proven",
    "runtime object lookup by name proven",
    "runtime missionscript execution proven",
    "runtime world loading proven",
    "runtime spawnthing behavior proven",
    "runtime spawner behavior proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
    "exact vm layout proven",
    "exact thing layout proven",
    "exact world layout proven",
    "exact handler address proof",
    "bea patching behavior proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def clean_cell(value: str) -> str:
    return value.strip().strip("`")


def mission_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in read_text(MISSION_USAGE).splitlines():
        if not line.startswith("| ") or line.startswith("| Level |"):
            continue
        cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not cells[0].isdigit():
            continue
        rows.append(
            {
                "level": cells[0],
                "directory": cells[1],
                "file": cells[2],
                "call": cells[3],
                "thing": cells[4],
                "spawner": cells[5],
            }
        )
    return rows


def selected_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row["call"] == "GetThingRef"
        and (row["level"], row["directory"]) in SELECTED_LEVEL_DIRS
        and row["thing"] in SELECTED_THINGS
    ]


def grouped_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter((row["level"], row["directory"], row["file"], row["thing"]) for row in rows)
    result = []
    for level, directory, file_name, thing in sorted(counts):
        result.append(
            {
                "level": level,
                "directory": directory,
                "file": file_name,
                "thing": thing,
                "rawRows": counts[(level, directory, file_name, thing)],
            }
        )
    return result


def expected_schema() -> dict[str, Any]:
    source = read_json(SOURCE_SCHEMA)
    rows = mission_rows()
    selected = selected_rows(rows)
    unique_object = {(row["level"], row["directory"], row["call"], row["thing"]) for row in selected}
    unique_file_thing = {(row["level"], row["directory"], row["file"], row["thing"]) for row in selected}
    duplicate_rows = len(selected) - len(unique_file_thing)
    empty_spawner_rows = sum(1 for row in selected if not row["spawner"])

    return {
        "schemaVersion": "world-thing-spawn-getthingref-object-reference-static.v1",
        "status": "PASS",
        "source": {
            "copiedCorpusSchemaPath": "reverse-engineering/game-assets/world-thing-spawn-copied-corpus-schema.v1.json",
            "missionThingUsagePath": "reverse-engineering/game-assets/mission-thing-usage.md",
            "copiedAppOwnedInputOnly": True,
            "programFilesInputUsed": False,
            "runtimeExecution": False,
            "ghidraMutation": False,
        },
        "staticContext": source["staticContext"],
        "selectedFamily": {
            "name": "training-target-zone-getthingref-family",
            "call": "GetThingRef",
            "levels": ["22", "100"],
            "directories": ["level022", "level100"],
            "files": sorted({row["file"] for row in selected}),
            "thingLabels": list(SELECTED_THINGS),
            "spawners": [],
            "rawRows": len(selected),
            "uniqueObjectReferenceRows": len(unique_object),
            "uniqueThingLabels": len({row["thing"] for row in selected}),
            "uniqueFileThingRows": len(unique_file_thing),
            "duplicateCallRows": duplicate_rows,
            "emptySpawnerRows": empty_spawner_rows,
            "rows": grouped_rows(selected),
        },
        "corpusCarryForward": source["corpusCounts"],
        "linkageLayers": [
            {
                "id": "corpus-object-reference-family",
                "anchors": [
                    "mission-thing-usage.md",
                    "world-thing-spawn-copied-corpus-schema.v1.json",
                    "training-target-zone-getthingref-family",
                    "level022",
                    "level100",
                    "Level22Script.msl",
                    "LevelScript.msl",
                    "Target Zone 1",
                    "Target Zone 2",
                    "Target Zone 3",
                    "Target Zone 4",
                ],
                "staticContract": "Preserve level, directory, file, thing label, casing, empty spawner column, and duplicate-call counts for the selected GetThingRef target-zone family.",
            },
            {
                "id": "missionscript-command-descriptor",
                "anchors": [
                    "IScript__GetThingRef",
                    "GetThingRef",
                    "CThingPtrDataType",
                    "ScriptCommandRegistry__InitBuiltins",
                    "0x0052ff30",
                    "0x0064ce50",
                    "0x0064f210",
                ],
                "staticContract": "Tie the selected corpus family to the saved MissionScript command registry and thing-pointer datatype surface without claiming exact handler address proof or runtime dispatch.",
            },
            {
                "id": "world-object-reference-boundary",
                "anchors": [
                    "world-thing-spawn-object-reference-proof-plan.md",
                    "CWorld__LoadWorld",
                    "CWorldPhysicsManager__CreateThingByType",
                    "InitThing__CreateThingByType",
                    "CThing__InitRenderThingFromInitMeshName",
                ],
                "staticContract": "Carry the selected object-reference labels to the existing world/load/factory boundary while preserving runtime object identity as unproven.",
            },
            {
                "id": "spawn-handoff-context",
                "anchors": [
                    "world-thing-spawn-spawner-handoff-static-proof.md",
                    "world-thing-spawn-spawner-handoff-static.v1.json",
                    "training-target-spawn-family",
                    "DAT_008553f4",
                    "0x0050f970 CWorldPhysicsManager__CreateSpawner",
                    "0x004e3c60 CSpawnerThng__DoSpawn",
                ],
                "staticContract": "Use the completed SpawnThing handoff as context only; this GetThingRef proof does not claim runtime spawn or lookup behavior.",
            },
        ],
        "claims": [
            "The selected training target-zone GetThingRef copied-corpus family has a reproducible static object-reference row set derived from the tracked loose-MSL mission thing usage table.",
            "The proof preserves raw rows, unique object-reference rows, unique file/thing rows, empty spawner values, exact target-zone casing, and the duplicate Target Zone 4 call in level100.",
            "The selected family is tied to MissionScript command registry, thing-pointer datatype, and existing World / Thing / Spawn static boundary docs without claiming runtime lookup behavior.",
        ],
        "notClaimed": [
            "runtime GetThingRef behavior",
            "runtime object identity",
            "runtime object lookup by name",
            "runtime MissionScript execution",
            "runtime world loading",
            "runtime SpawnThing behavior",
            "runtime spawner behavior",
            "live loose-MSL loading",
            "packed-resource script selection",
            "exact descriptor layout",
            "exact handler address proof",
            "exact VM/object-code/world/thing/spawner layouts",
            "exact source-body identity",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def write_schema() -> None:
    text = json.dumps(expected_schema(), indent=2) + "\n"
    SCHEMA.write_text(text, encoding="utf-8")
    LORE_SCHEMA.parent.mkdir(parents=True, exist_ok=True)
    LORE_SCHEMA.write_text(text, encoding="utf-8")


def check_no_bad_public_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{relative(path)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{relative(path)} overclaims: {phrase}", failures)


def check_schema(failures: list[str]) -> None:
    rows = mission_rows()
    require(len(rows) == 644, "mission thing raw row count mismatch", failures)
    require(sum(1 for row in rows if row["call"] == "GetThingRef") == 574, "GetThingRef raw row count mismatch", failures)
    require(sum(1 for row in rows if row["call"] == "SpawnThing") == 70, "SpawnThing raw row count mismatch", failures)

    stored = read_json(SCHEMA)
    expected = expected_schema()
    require(stored == expected, "tracked GetThingRef schema does not match expected static contract", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore GetThingRef schema mirror mismatch", failures)
    family = stored["selectedFamily"]
    require(family["rawRows"] == 9, "selected raw row mismatch", failures)
    require(family["uniqueObjectReferenceRows"] == 8, "selected unique object-reference mismatch", failures)
    require(family["uniqueFileThingRows"] == 8, "selected unique file/thing mismatch", failures)
    require(family["duplicateCallRows"] == 1, "selected duplicate row mismatch", failures)
    require(family["emptySpawnerRows"] == 9, "selected empty spawner row mismatch", failures)
    require(len(stored["linkageLayers"]) == 4, "linkage layer count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore GetThingRef proof mirror mismatch", failures)
    required_tokens = (
        "Status: static GetThingRef object-reference proof complete, not runtime proof",
        "world-thing-spawn-getthingref-object-reference-static.v1.json",
        "training-target-zone-getthingref-family",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        "Remaining active focused work remains `0`",
        BACKUP,
        "574",
        "70",
        "644",
        "418",
        "18",
        "436",
        "9",
        "8",
        "1",
        "level022",
        "level100",
        "Level22Script.msl",
        "LevelScript.msl",
        "Target Zone 1",
        "Target Zone 2",
        "Target Zone 3",
        "Target Zone 4",
        "IScript__GetThingRef",
        "CThingPtrDataType",
        "ScriptCommandRegistry__InitBuiltins",
        "0x0052ff30",
        "0x0064ce50",
        "0x0064f210",
        "world-thing-spawn-object-reference-proof-plan.md",
        "world-thing-spawn-spawner-handoff-static-proof.md",
        "DAT_008553f4",
        "0x0050f970 CWorldPhysicsManager__CreateSpawner",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "runtime `GetThingRef` behavior",
        "runtime object identity",
    )
    for path in (RESULT, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{relative(path)} missing token: {token}", failures)
        check_no_bad_public_tokens(path, failures)

    for path in (
        BACKLOG,
        MAPPED,
        BIN_INDEX,
        RE_INDEX,
        GAME_ASSETS_INDEX,
        MISSION_CONTRACT,
        WORLD_PLAN,
        CORPUS_RESULT,
        SPAWNER_RESULT,
        QUICK_COMMANDS,
        ISCRIPT_OWNER,
    ):
        text = read_text(path)
        for token in (
            "world-thing-spawn-getthingref-object-reference-static-proof.md",
            "world-thing-spawn-getthingref-object-reference-static.v1.json",
            "static GetThingRef object-reference proof complete, not runtime proof",
        ):
            require(token in text, f"{relative(path)} missing GetThingRef proof token: {token}", failures)
        check_no_bad_public_tokens(path, failures)


def check_progress_and_package(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current risk focused mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current risk remaining mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:world-thing-spawn-getthingref-object-reference-static")
        == r"py -3 tools\world_thing_spawn_getthingref_object_reference_static_probe.py --check",
        "missing package GetThingRef proof script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-schema", action="store_true", help="rewrite generated schema artifacts")
    args = parser.parse_args()

    if args.write_schema:
        write_schema()

    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_progress_and_package(failures)

    if failures:
        print("World / Thing / Spawn GetThingRef object-reference static probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("World / Thing / Spawn GetThingRef object-reference static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
