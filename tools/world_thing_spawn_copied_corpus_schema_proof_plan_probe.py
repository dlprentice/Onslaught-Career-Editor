#!/usr/bin/env python3
"""Validate the World / Thing / Spawn copied-corpus schema proof plan."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "world_thing_spawn_copied_corpus_schema_proof_plan_2026-06-08.md"
MISSION_THING = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
WORLD_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
LORE_WORLD_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

SCHEMA_LINK = "world-thing-spawn-copied-corpus-schema-proof-plan.md"
WORLD_LINK = "world-thing-spawn-object-reference-proof-plan.md"
BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    BACKUP,
)

SCHEMA_TOKENS = (
    "World / Thing / Spawn Copied-Corpus Object-Reference Schema Proof Plan",
    "Status: active public-safe copied-corpus schema proof plan, not runtime proof",
    "world-thing-spawn-copied-corpus-schema-proof-plan",
    WORLD_LINK,
    "mission-thing-usage.md",
    "Raw detailed call rows",
    "Published unique object-reference rows",
    "Spawn-preserving unique rows",
    "`574`",
    "`70`",
    "`644`",
    "`418`",
    "`18`",
    "`436`",
    "`29`",
    "`447`",
    "`Level + Dir + File + Call + Thing + Spawner + call occurrence`",
    "`Level + Dir + Call + Thing`",
    "`Level + Dir + Call + Thing + Spawner`",
    "`22`",
    "`level022`",
    "`100`",
    "`level100`",
    "`Hangar.msl`",
    "`TankFactory.msl`",
    "`LevelScript.msl`",
    "`Target Drone`",
    "`Target Tank`",
    "`Target Truck`",
    "`Air Trainer`",
    "`SpawnerA`",
    "`SpawnerB`",
    "`34` raw `SpawnThing` rows",
    "`6` unique `Level + Dir + Call + Thing` rows",
    "`4` unique thing labels",
    "`8` unique `Level + Dir + File + Thing + Spawner` rows",
    "IScript__SpawnThing",
    "IScript__GetThingRef",
    "ScriptCommandRegistry__InitBuiltins",
    "0x0052ff30",
    "0x0064ce50",
    "0x0064f210",
    "0x005392a0 CScriptObjectCode__CollectSpawnThings",
    "opcode `0x18`",
    "CWorldMeshList__Add",
    "0x0050b9c0 CWorld__LoadWorld",
    "0x0050ac70 CWorld__LoadScriptEvents",
    "0x0050dcb0 CWorld__SpawnInitialThings",
    "0x0050df80 CWorldPhysicsManager__CreateThingByType",
    "0x0048c650 InitThing__CreateThingByType",
    "0x004e3c60 CSpawnerThng__DoSpawn",
    "0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
    "CUnit__VFunc08_InitAndAddToWorld",
    "CUnit__SetSpawnCooldownState3",
    "CThing__InitRenderThingFromInitMeshName",
    "mesh-resource-render-static-contract.md",
    "world-thing-spawn-copied-corpus-schema.v1",
)

FORBIDDEN_PHRASES = (
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
    "runtime proof complete",
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

SELECTED_FAMILY = Counter(
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


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_no_overclaims(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims: {phrase}", failures)
    for token in FORBIDDEN_PUBLIC_TOKENS:
        require(token not in text, f"{path.relative_to(ROOT)} leaks public-forbidden token: {token}", failures)


def parse_mission_thing_rows() -> list[dict[str, str]]:
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


def check_counts(failures: list[str]) -> None:
    rows = parse_mission_thing_rows()
    raw = Counter(row["Call"] for row in rows)
    unique_object_keys = {(
        row["Level"],
        row["Dir"],
        row["Call"],
        row["Thing"],
    ) for row in rows}
    unique_object = Counter(key[2] for key in unique_object_keys)
    unique_spawner_keys = {(
        row["Level"],
        row["Dir"],
        row["Call"],
        row["Thing"],
        row["Spawner"],
    ) for row in rows}
    unique_spawner = Counter(key[2] for key in unique_spawner_keys)

    require(len(rows) == 644, "mission thing raw row total mismatch", failures)
    require(raw["GetThingRef"] == 574, "raw GetThingRef mismatch", failures)
    require(raw["SpawnThing"] == 70, "raw SpawnThing mismatch", failures)
    require(unique_object["GetThingRef"] == 418, "unique-object GetThingRef mismatch", failures)
    require(unique_object["SpawnThing"] == 18, "unique-object SpawnThing mismatch", failures)
    require(unique_spawner["GetThingRef"] == 418, "unique-spawner GetThingRef mismatch", failures)
    require(unique_spawner["SpawnThing"] == 29, "unique-spawner SpawnThing mismatch", failures)

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
    require(selected == SELECTED_FAMILY, f"selected SpawnThing family mismatch: {selected}", failures)
    require(sum(selected.values()) == 34, "selected family raw row count mismatch", failures)
    unique_selected_object = {
        (level, directory, "SpawnThing", thing)
        for (level, directory, _file, thing, _spawner), _count in selected.items()
    }
    require(len(unique_selected_object) == 6, "selected unique object-reference count mismatch", failures)
    require(len(selected) == 8, "selected unique file/thing/spawner count mismatch", failures)


def check_plan(failures: list[str]) -> None:
    text = read_text(PLAN)
    for token in (*STATIC_TOKENS, *SCHEMA_TOKENS):
        require(token in text, f"schema plan missing token: {token}", failures)
    check_no_overclaims(PLAN, failures)
    require(read_text(LORE_PLAN) == text, "lore schema plan mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    readiness_tokens = (
        "World / Thing / Spawn Copied-Corpus Schema Proof Plan Readiness Note",
        "schema proof plan complete, not runtime proof",
        "world-thing-spawn-copied-corpus-schema-proof-plan",
        "not a new static re-audit wave",
        "not a Ghidra mutation",
        "not a runtime test",
        "not a mission execution proof",
        "not a live loose-MSL loading proof",
        "not a BEA patch",
        "not a Godot slice",
        "not a rebuild parity claim",
        "`574`",
        "`70`",
        "`644`",
        "`418`",
        "`18`",
        "`436`",
        "`29`",
        "`447`",
        "`34` raw `SpawnThing` rows",
        "`6` unique `Level + Dir + Call + Thing` rows",
        "`4` unique thing labels",
        "`8` unique `Level + Dir + File + Thing + Spawner` rows",
        "IScript__SpawnThing",
        "0x005392a0 CScriptObjectCode__CollectSpawnThings",
        "0x004e3c60 CSpawnerThng__DoSpawn",
    )
    for token in (*STATIC_TOKENS, *readiness_tokens):
        require(token in text, f"readiness missing token: {token}", failures)
    check_no_overclaims(READINESS, failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (MISSION_THING, WORLD_PLAN, BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(SCHEMA_LINK in text, f"{path.relative_to(ROOT)} missing schema plan link", failures)
        require(WORLD_LINK in text, f"{path.relative_to(ROOT)} missing bridge plan link", failures)
        check_no_overclaims(path, failures)

    require(read_text(LORE_WORLD_PLAN) == read_text(WORLD_PLAN), "world bridge plan lore mirror mismatch", failures)
    require(read_text(LORE_BACKLOG) == read_text(BACKLOG), "backlog lore mirror mismatch", failures)
    require(read_text(LORE_MAPPED) == read_text(MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(LORE_BIN_INDEX) == read_text(BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(LORE_RE_INDEX) == read_text(RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require(
        "The selected active static-to-proof slice is [World / Thing / Spawn Copied-Corpus Object-Reference Schema Proof Plan]" in backlog,
        "backlog missing active schema slice",
        failures,
    )
    require(
        "Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan" in backlog,
        "backlog missing completed bridge plan",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [World / Thing / Spawn / Object-Reference Bridge Proof Plan]" not in backlog,
        "backlog still has stale active bridge plan",
        failures,
    )

    mapped = read_text(MAPPED)
    require("Active World / Thing / Spawn copied-corpus schema proof plan" in mapped, "mapped systems missing active schema slice", failures)
    require("Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan" in mapped, "mapped systems missing completed bridge plan", failures)
    require("Active World / Thing / Spawn / Object-Reference Bridge Proof Plan" not in mapped, "mapped systems still has stale active bridge plan", failures)


def check_progress_unchanged(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total function mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented function mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)

    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1210, "legacy additive mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)


def check_package(failures: list[str]) -> None:
    scripts = read_json(PACKAGE_JSON)["scripts"]
    require(
        scripts.get("test:world-thing-spawn-copied-corpus-schema-proof-plan")
        == r"py -3 tools\world_thing_spawn_copied_corpus_schema_proof_plan_probe.py --check",
        "missing package schema proof-plan script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_plan(failures)
    check_readiness(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("World / Thing / Spawn copied-corpus schema proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("World / Thing / Spawn copied-corpus schema proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
