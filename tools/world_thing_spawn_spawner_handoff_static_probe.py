#!/usr/bin/env python3
"""Validate the World / Thing / Spawn spawner handoff static proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCHEMA = ROOT / "reverse-engineering" / "game-assets" / "world-thing-spawn-copied-corpus-schema.v1.json"
SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static.v1.json"
LORE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static.v1.json"
RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static-proof.md"
READINESS = ROOT / "release" / "readiness" / "world_thing_spawn_spawner_handoff_static_proof_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
MISSION_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
WORLD_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
CORPUS_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

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
    "runtime spawnthing behavior proven",
    "runtime getthingref behavior proven",
    "runtime missionscript execution proven",
    "runtime object identity proven",
    "runtime object lookup by name proven",
    "runtime world loading proven",
    "runtime spawner behavior proven",
    "runtime unit/battleengine spawn behavior proven",
    "runtime ai activation proven",
    "runtime collision proven",
    "runtime damage proven",
    "runtime hud/message/audio output proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact descriptor layout proven",
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


def expected_schema() -> dict[str, Any]:
    source = read_json(SOURCE_SCHEMA)
    return {
        "schemaVersion": "world-thing-spawn-spawner-handoff-static.v1",
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
            key: source["selectedFamily"][key]
            for key in (
                "name",
                "call",
                "levels",
                "directories",
                "thingLabels",
                "spawners",
                "rawRows",
                "uniqueObjectReferenceRows",
                "uniqueThingLabels",
                "uniqueFileThingSpawnerRows",
            )
        },
        "corpusCarryForward": source["corpusCounts"],
        "handoffLayers": [
            {
                "id": "corpus-command-family",
                "anchors": [
                    "world-thing-spawn-copied-corpus-schema.v1.json",
                    "mission-thing-usage.md",
                    "training-target-spawn-family",
                    "Target Drone",
                    "Target Tank",
                    "Target Truck",
                    "Air Trainer",
                    "SpawnerA",
                    "SpawnerB",
                ],
                "staticContract": "Preserve level, directory, file, thing, spawner, casing, and duplicate-call counts for the selected SpawnThing family.",
            },
            {
                "id": "missionscript-command-descriptor",
                "anchors": [
                    "IScript__SpawnThing",
                    "IScript__GetThingRef",
                    "CThingPtrDataType",
                    "ScriptCommandRegistry__InitBuiltins",
                    "0x0064ce50",
                    "0x0064f210",
                ],
                "staticContract": "Tie the selected corpus command family to the saved MissionScript command registry and thing-pointer datatype surface without claiming runtime dispatch.",
            },
            {
                "id": "bytecode-preload",
                "anchors": [
                    "0x005392a0 CScriptObjectCode__CollectSpawnThings",
                    "opcode 0x18",
                    "CWorldMeshList__Add",
                ],
                "staticContract": "Record the static SpawnThing pre-scan path that adds mesh/world dependencies before any live script execution proof.",
            },
            {
                "id": "world-load-mesh-dependency",
                "anchors": [
                    "0x0050b9c0 CWorld__LoadWorld",
                    "0x0050ac70 CWorld__LoadScriptEvents",
                    "0x0050d9e0 CWorldMeshList__Add",
                    "DAT_00855358",
                    "DAT_008553fc +0xb0",
                ],
                "staticContract": "Map the world-load and mesh-list dependency surface needed before object-reference or spawn runtime proof.",
            },
            {
                "id": "world-factory-init",
                "anchors": [
                    "0x0050dcb0 CWorld__SpawnInitialThings",
                    "0x0050df80 CWorldPhysicsManager__CreateThingByType",
                    "0x0048c650 InitThing__CreateThingByType",
                    "0x0040e280 CInitThing__LoadFromMemBuffer",
                    "CThing__InitRenderThingFromInitMeshName",
                ],
                "staticContract": "Map the static thing-definition and init-object factory path without claiming exact object layout or runtime creation.",
            },
            {
                "id": "spawner-gate-wave",
                "anchors": [
                    "0x004e3010 CSpawnerThng__Init",
                    "0x004e36c0 CSpawnerThng__FindSpawnerByName",
                    "0x004e3c60 CSpawnerThng__DoSpawn",
                    "0x004e3f90 CSpawnerThng__ProcessSpawnWave",
                    "0x0050f680 CSpawnerThng__IsSpawnTypeAllowed",
                    "0x0050f970 CWorldPhysicsManager__CreateSpawner",
                    "0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
                    "0x005115b0 CWorldPhysicsManager__MapGunOrSpawnerTagToIndex",
                    "0x00511ad0 CWorldPhysicsManager__AddSpawnerByName",
                    "DAT_008553f4",
                ],
                "staticContract": "Map the spawner name/tag/type-gate shell required for selected SpawnThing handoff proof.",
            },
            {
                "id": "unit-world-add-cooldown",
                "anchors": [
                    "CUnit__VFunc08_InitAndAddToWorld",
                    "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
                    "0x004fc3a0 CUnit__SetSpawnCooldownState3",
                ],
                "staticContract": "Record the Unit/BattleEngine spawn-add and post-spawn cooldown handoff anchors without claiming runtime activation.",
            },
            {
                "id": "mesh-resource-render-boundary",
                "anchors": [
                    "CThing__InitRenderThingFromInitMeshName",
                    "mesh-resource-render-static-contract.md",
                    "texture-resource-decode-static-contract.md",
                ],
                "staticContract": "Preserve the render/resource dependency boundary for rebuild planning without claiming visual output or GPU parity.",
            },
        ],
        "fieldRoleEvidence": {
            "CSpawnerThng+0x0468": "spawner name string role",
            "CSpawnerThng+0x007c": "parent or owner role",
            "CSpawnerThng+0x0080": "next spawn time role",
            "CSpawnerThng+0x0090": "batch size role",
            "CSpawnerThng+0x0094": "total count role",
            "CSpawnerThng+0x0098": "current wave count role",
            "CSpawnerThng+0x009c": "current batch count role",
            "CSpawnerThng+0x00a0": "infinite spawn flag role",
            "CSpawnerThng+0x00a4": "active flag role",
            "CSpawnerThng+0x00b0": "spawn mode role",
            "CUnit+0x0168": "spawn cooldown state role",
            "CUnit+0x016c": "spawn cooldown timestamp role",
        },
        "claims": [
            "The selected training-target SpawnThing copied-corpus family has a bounded static handoff map from loose corpus rows to MissionScript descriptor/datatype anchors, bytecode pre-scan, world load/mesh dependencies, spawner gates, world factory/init, Unit world-add/cooldown, and mesh/resource boundaries.",
            "The proof preserves raw, unique object-reference, and spawner-preserving corpus count vocabulary from the copied-corpus schema.",
            "Field-role offsets are preserved as static roles only, not final C++ layouts.",
        ],
        "notClaimed": [
            "runtime SpawnThing behavior",
            "runtime GetThingRef behavior",
            "runtime MissionScript execution",
            "runtime object identity",
            "runtime object lookup by name",
            "runtime world loading",
            "runtime spawner behavior",
            "runtime Unit/BattleEngine spawn behavior",
            "runtime AI activation",
            "runtime collision",
            "runtime damage",
            "runtime HUD/message/audio output",
            "live loose-MSL loading",
            "packed-resource script selection",
            "exact descriptor layout",
            "exact VM/object-code/world/thing/spawner/Unit layouts",
            "exact source-body identity",
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
    require(stored == expected_schema(), "tracked handoff schema does not match expected static handoff contract", failures)
    require(read_json(LORE_SCHEMA) == stored, "lore handoff schema mirror mismatch", failures)
    require(stored["selectedFamily"]["rawRows"] == 34, "selected rawRows mismatch", failures)
    require(stored["selectedFamily"]["uniqueObjectReferenceRows"] == 6, "selected unique object refs mismatch", failures)
    require(stored["selectedFamily"]["uniqueFileThingSpawnerRows"] == 8, "selected unique file/thing/spawner mismatch", failures)
    require(len(stored["handoffLayers"]) == 8, "handoff layer count mismatch", failures)
    for token in (
        "runtime SpawnThing behavior",
        "runtime object identity",
        "runtime spawner behavior",
        "runtime Unit/BattleEngine spawn behavior",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in stored["notClaimed"], f"schema missing non-claim: {token}", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_RESULT) == read_text(RESULT), "lore handoff proof mirror mismatch", failures)
    required_tokens = (
        "Status: static spawner handoff proof complete, not runtime proof",
        "world-thing-spawn-spawner-handoff-static.v1.json",
        "world-thing-spawn-copied-corpus-schema-proof.md",
        "world-thing-spawn-copied-corpus-schema.v1.json",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        "Remaining active focused work remains `0`",
        BACKUP,
        "training-target-spawn-family",
        "574",
        "70",
        "644",
        "418",
        "18",
        "436",
        "29",
        "447",
        "34",
        "Target Drone",
        "Target Tank",
        "Target Truck",
        "Air Trainer",
        "SpawnerA",
        "SpawnerB",
        "IScript__SpawnThing",
        "IScript__GetThingRef",
        "CThingPtrDataType",
        "0x005392a0 CScriptObjectCode__CollectSpawnThings",
        "opcode `0x18`",
        "0x0050b9c0 CWorld__LoadWorld",
        "0x0050d9e0 CWorldMeshList__Add",
        "DAT_00855358",
        "DAT_008553fc +0xb0",
        "0x0050df80 CWorldPhysicsManager__CreateThingByType",
        "0x0048c650 InitThing__CreateThingByType",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "0x004e3f90 CSpawnerThng__ProcessSpawnWave",
        "0x0050f680 CSpawnerThng__IsSpawnTypeAllowed",
        "0x0050f970 CWorldPhysicsManager__CreateSpawner",
        "0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
        "0x005115b0 CWorldPhysicsManager__MapGunOrSpawnerTagToIndex",
        "0x00511ad0 CWorldPhysicsManager__AddSpawnerByName",
        "DAT_008553f4",
        "CUnit__VFunc08_InitAndAddToWorld",
        "0x004fc3a0 CUnit__SetSpawnCooldownState3",
        "CSpawnerThng+0x0468",
        "CSpawnerThng+0x00b0",
        "CUnit+0x0168",
        "runtime `SpawnThing` behavior",
    )
    for path in (RESULT, READINESS):
        text = read_text(path)
        for token in required_tokens:
            require(token in text, f"{relative(path)} missing token: {token}", failures)
        check_no_bad_public_tokens(path, failures)

    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, MISSION_CONTRACT, WORLD_PLAN, CORPUS_RESULT):
        text = read_text(path)
        for token in (
            "world-thing-spawn-spawner-handoff-static-proof.md",
            "world-thing-spawn-spawner-handoff-static.v1.json",
            "static spawner handoff proof complete, not runtime proof",
        ):
            require(token in text, f"{relative(path)} missing handoff token: {token}", failures)
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
        scripts.get("test:world-thing-spawn-spawner-handoff-static")
        == r"py -3 tools\world_thing_spawn_spawner_handoff_static_probe.py --check",
        "missing package handoff proof script",
        failures,
    )

    spawner_doc = read_text(ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SpawnerThng.cpp" / "_index.md")
    require("Uses global spawner list at `DAT_008553f4`" in spawner_doc, "SpawnerThng owner doc missing corrected spawner-list global", failures)
    require("Uses global list at `DAT_008553fc` for spawner iteration" not in spawner_doc, "SpawnerThng owner doc retains stale spawner-list global", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_schema(failures)
    check_docs(failures)
    check_progress_and_package(failures)

    if failures:
        print("World / Thing / Spawn spawner handoff static probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("World / Thing / Spawn spawner handoff static probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
