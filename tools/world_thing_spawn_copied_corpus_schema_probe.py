#!/usr/bin/env python3
"""Validate the World / Thing / Spawn copied-corpus schema proof."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "reverse-engineering" / "game-assets" / "world-thing-spawn-copied-corpus-schema.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "world-thing-spawn-copied-corpus-schema.v1.json"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof.md"
READINESS = ROOT / "release" / "readiness" / "world_thing_spawn_copied_corpus_schema_proof_2026-06-08.md"
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof-plan.md"
WORLD_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
MISSION_THING = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

SCHEMA_LINK = "world-thing-spawn-copied-corpus-schema.v1.json"
RESULT_LINK = "world-thing-spawn-copied-corpus-schema-proof.md"
PLAN_LINK = "world-thing-spawn-copied-corpus-schema-proof-plan.md"
WORLD_PLAN_LINK = "world-thing-spawn-object-reference-proof-plan.md"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

EXPECTED_SELECTED = Counter(
    {
        ("22", "level022", "Hangar.msl", "Target Drone", "SpawnerA"): 3,
        ("22", "level022", "Hangar.msl", "Target Drone", "SpawnerB"): 6,
        ("22", "level022", "TankFactory.msl", "Target Tank", "SpawnerA"): 5,
        ("100", "level100", "Hangar.msl", "Target Drone", "SpawnerA"): 3,
        ("100", "level100", "Hangar.msl", "Target Drone", "SpawnerB"): 6,
        ("100", "level100", "LevelScript.msl", "Air Trainer", "SpawnerB"): 1,
        ("100", "level100", "TankFactory.msl", "Target Tank", "SpawnerA"): 4,
        ("100", "level100", "TankFactory.msl", "Target Truck", "SpawnerA"): 6,
    }
)

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
    "runtime spawnthing behavior proven",
    "runtime missionscript execution proven",
    "runtime object identity proven",
    "runtime world loading proven",
    "runtime spawner behavior proven",
    "runtime unit/battleengine spawn behavior proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact handler address proven",
    "exact vm layout proven",
    "exact world layout proven",
    "exact thing layout proven",
    "exact spawner layout proven",
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


def parse_rows() -> list[dict[str, str]]:
    lines = read_text(MISSION_THING).splitlines()
    try:
        start = lines.index("## Detailed Call Sites")
    except ValueError as exc:
        raise AssertionError("mission-thing-usage missing Detailed Call Sites") from exc

    rows: list[dict[str, str]] = []
    for line in lines[start + 3 :]:
        if not line.startswith("|"):
            continue
        if line.startswith("|------"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) != 6:
            continue
        rows.append(
            {
                "Level": cells[0],
                "Dir": cells[1],
                "File": cells[2],
                "Call": cells[3],
                "Thing": cells[4],
                "Spawner": cells[5],
            }
        )
    return rows


def build_expected_schema() -> dict[str, Any]:
    rows = parse_rows()
    raw = Counter(row["Call"] for row in rows)
    unique_object_keys = {
        (
            row["Level"],
            row["Dir"],
            row["Call"],
            row["Thing"],
        )
        for row in rows
    }
    unique_spawner_keys = {
        (
            row["Level"],
            row["Dir"],
            row["Call"],
            row["Thing"],
            row["Spawner"],
        )
        for row in rows
    }
    unique_object = Counter(key[2] for key in unique_object_keys)
    unique_spawner = Counter(key[2] for key in unique_spawner_keys)

    selected = Counter(
        (
            row["Level"],
            row["Dir"],
            row["File"],
            row["Thing"],
            row["Spawner"],
        )
        for row in rows
        if row["Call"] == "SpawnThing"
        and row["Level"] in {"22", "100"}
        and row["Thing"] in {"Target Drone", "Target Tank", "Target Truck", "Air Trainer"}
    )
    selected_rows = [
        {
            "level": level,
            "directory": directory,
            "file": file_name,
            "thing": thing,
            "spawner": spawner,
            "rawRows": count,
        }
        for (level, directory, file_name, thing, spawner), count in sorted(
            selected.items(),
            key=lambda item: (int(item[0][0]), item[0][1], item[0][2], item[0][3], item[0][4]),
        )
    ]
    unique_selected_object = {
        (level, directory, "SpawnThing", thing)
        for (level, directory, _file_name, thing, _spawner), _count in selected.items()
    }

    return {
        "schemaVersion": "world-thing-spawn-copied-corpus-schema.v1",
        "status": "PASS",
        "source": {
            "path": "reverse-engineering/game-assets/mission-thing-usage.md",
            "copiedAppOwnedInputOnly": True,
            "programFilesInputUsed": False,
            "runtimeExecution": False,
            "ghidraMutation": False,
        },
        "staticContext": {
            "staticFunctionQuality": "6411/6411 = 100.00%",
            "staticDebt": "0 / 0 / 0",
            "expandedStaticSurface": "1560/1560 = 100.00%",
            "currentRiskFocused": "1179/1179 = 100.00%",
            "remainingActiveFocusedWork": 0,
            "latestGhidraBackup": BACKUP,
        },
        "countKeys": {
            "rawDetailedCallRows": "Level + Dir + File + Call + Thing + Spawner + call occurrence",
            "uniqueObjectReferenceRows": "Level + Dir + Call + Thing",
            "uniqueSpawnPreservingSpawnerRows": "Level + Dir + Call + Thing + Spawner",
            "selectedFamilyRows": "Level + Dir + File + Thing + Spawner",
        },
        "corpusCounts": {
            "rawDetailedCallRows": {
                "GetThingRef": raw["GetThingRef"],
                "SpawnThing": raw["SpawnThing"],
                "total": len(rows),
            },
            "uniqueObjectReferenceRows": {
                "GetThingRef": unique_object["GetThingRef"],
                "SpawnThing": unique_object["SpawnThing"],
                "total": len(unique_object_keys),
            },
            "uniqueSpawnPreservingSpawnerRows": {
                "GetThingRef": unique_spawner["GetThingRef"],
                "SpawnThing": unique_spawner["SpawnThing"],
                "total": len(unique_spawner_keys),
            },
        },
        "selectedFamily": {
            "name": "training-target-spawn-family",
            "call": "SpawnThing",
            "levels": ["22", "100"],
            "directories": ["level022", "level100"],
            "thingLabels": ["Air Trainer", "Target Drone", "Target Tank", "Target Truck"],
            "spawners": ["SpawnerA", "SpawnerB"],
            "rawRows": sum(selected.values()),
            "uniqueObjectReferenceRows": len(unique_selected_object),
            "uniqueThingLabels": len({thing for (_level, _directory, _file_name, thing, _spawner), _count in selected.items()}),
            "uniqueFileThingSpawnerRows": len(selected),
            "rows": selected_rows,
        },
        "staticAnchors": [
            "IScript__SpawnThing",
            "IScript__GetThingRef",
            "ScriptCommandRegistry__InitBuiltins",
            "0x005392a0 CScriptObjectCode__CollectSpawnThings",
            "opcode 0x18",
            "CWorldMeshList__Add",
            "0x0050b9c0 CWorld__LoadWorld",
            "0x0050dcb0 CWorld__SpawnInitialThings",
            "0x0050df80 CWorldPhysicsManager__CreateThingByType",
            "0x004e3c60 CSpawnerThng__DoSpawn",
            "0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
            "CUnit__VFunc08_InitAndAddToWorld",
            "CThing__InitRenderThingFromInitMeshName",
        ],
        "claims": [
            "The selected copied-corpus schema can be rebuilt from the tracked loose-MSL mission thing usage table.",
            "Raw detailed call rows, public deduped object-reference rows, and spawner-preserving rows are distinct metrics.",
            "The first training-target SpawnThing family preserves level, directory, file, thing, spawner, casing, and duplicate-call counts.",
        ],
        "notClaimed": [
            "runtime GetThingRef behavior",
            "runtime SpawnThing behavior",
            "runtime MissionScript execution",
            "runtime object identity",
            "runtime world loading",
            "runtime spawner behavior",
            "runtime Unit/BattleEngine spawn behavior",
            "live loose-MSL loading",
            "packed-resource script selection",
            "exact handler address proof",
            "exact VM/object-code/world/thing/spawner layouts",
            "BEA patching behavior",
            "visual QA",
            "Godot parity",
            "rebuild parity",
            "no-noticeable-difference parity",
        ],
    }


def check_no_bad_public_tokens(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{relative(path)} leaks public-forbidden token: {token}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{relative(path)} overclaims: {phrase}", failures)


def check_schema(failures: list[str]) -> None:
    stored = read_json(SCHEMA)
    expected = build_expected_schema()
    require(stored == expected, "tracked schema does not match rebuilt mission-thing schema", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore schema mirror mismatch", failures)

    counts = stored["corpusCounts"]
    require(counts["rawDetailedCallRows"] == {"GetThingRef": 574, "SpawnThing": 70, "total": 644}, "raw count mismatch", failures)
    require(counts["uniqueObjectReferenceRows"] == {"GetThingRef": 418, "SpawnThing": 18, "total": 436}, "unique object count mismatch", failures)
    require(counts["uniqueSpawnPreservingSpawnerRows"] == {"GetThingRef": 418, "SpawnThing": 29, "total": 447}, "unique spawner count mismatch", failures)
    family = stored["selectedFamily"]
    require(family["rawRows"] == 34, "selected family raw row mismatch", failures)
    require(family["uniqueObjectReferenceRows"] == 6, "selected unique object mismatch", failures)
    require(family["uniqueThingLabels"] == 4, "selected thing label mismatch", failures)
    require(family["uniqueFileThingSpawnerRows"] == 8, "selected file/thing/spawner mismatch", failures)
    require(len(family["rows"]) == 8, "selected row count mismatch", failures)

    serialized = json.dumps(stored, sort_keys=True)
    require("Program Files" not in serialized, "schema leaks Program Files path", failures)
    require("C:\\Users" not in serialized, "schema leaks absolute user path", failures)
    for token in (
        "runtime SpawnThing behavior",
        "runtime MissionScript execution",
        "runtime object identity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in stored["notClaimed"], f"schema missing non-claim: {token}", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore result mirror mismatch", failures)
    result_tokens = (
        "Status: copied-corpus schema proof complete, not runtime proof",
        SCHEMA_LINK,
        PLAN_LINK,
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        "Remaining active focused work remains `0`",
        BACKUP,
        "world-thing-spawn-copied-corpus-schema.v1",
        "574",
        "70",
        "644",
        "418",
        "18",
        "436",
        "29",
        "447",
        "`34` raw `SpawnThing` rows",
        "`6` unique `Level + Dir + Call + Thing` rows",
        "`4`: `Air Trainer`, `Target Drone`, `Target Tank`, `Target Truck`",
        "`8` unique `Level + Dir + File + Thing + Spawner` rows",
        "IScript__SpawnThing",
        "0x005392a0 CScriptObjectCode__CollectSpawnThings",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "runtime `SpawnThing` behavior",
    )
    for path in (RESULT, READINESS):
        text = read_text(path)
        for token in result_tokens:
            require(token in text, f"{relative(path)} missing token: {token}", failures)
        check_no_bad_public_tokens(path, failures)

    for path in (PLAN, WORLD_PLAN, MISSION_THING, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, GAME_ASSETS_INDEX):
        text = read_text(path)
        require(RESULT_LINK in text, f"{relative(path)} missing result link", failures)
        require(SCHEMA_LINK in text, f"{relative(path)} missing schema link", failures)
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
        scripts.get("test:world-thing-spawn-copied-corpus-schema")
        == r"py -3 tools\world_thing_spawn_copied_corpus_schema_probe.py --check",
        "missing package schema proof script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_progress_and_package(failures)

    if failures:
        print("World / Thing / Spawn copied-corpus schema probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("World / Thing / Spawn copied-corpus schema probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
