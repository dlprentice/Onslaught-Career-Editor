#!/usr/bin/env python3
"""Validate the World / Thing / Spawn object-reference bridge proof plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
READINESS = ROOT / "release" / "readiness" / "world_thing_spawn_object_reference_proof_plan_2026-06-08.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
MISSION_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
MISSION_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
MISSION_STATIC = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-static-review-2026-05-26.md"
MISSION_THING = ROOT / "reverse-engineering" / "game-assets" / "mission-thing-usage.md"
MSL_DOC = ROOT / "reverse-engineering" / "game-assets" / "msl-scripting.md"
MSL_COMMANDS = ROOT / "reverse-engineering" / "quick-reference" / "msl-commands.md"
MESH_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-motion-world-particle-static-review-2026-05-26.md"
UNIT_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-review-2026-05-26.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

PLAN_LINK = "world-thing-spawn-object-reference-proof-plan.md"
SCHEMA_LINK = "world-thing-spawn-copied-corpus-schema-proof-plan.md"

STATIC_TOKENS = (
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "Remaining active focused work: `0`",
    "Wave911 focused remains historical-retired/non-reconstructable",
)

PLAN_TOKENS = (
    "World / Thing / Spawn / Object-Reference Bridge Proof Plan",
    "Status: proof plan complete, not runtime proof",
    "world-thing-spawn-object-reference-proof-plan",
    "world-thing-spawn-copied-corpus-schema-proof-plan.md",
    "missionscript-iscript-static-contract.md",
    "missionscript-iscript-proof-plan.md",
    "IScript__GetThingRef",
    "IScript__SpawnThing",
    "ScriptCommandRegistry__InitBuiltins",
    "0x0052ff30",
    "`144` contiguous `0x40`-byte command descriptor records",
    "0x0064ce50",
    "0x0064f210",
    "CThingPtrDataType",
    "mission-thing-usage.md",
    "`57` level rows",
    "`418` `GetThingRef`",
    "`18` `SpawnThing`",
    "`436` total thing/spawn refs",
    "0x005392a0 CScriptObjectCode__CollectSpawnThings",
    "opcode `0x18`",
    "CWorldMeshList__Add",
    "mesh-motion-world-particle-static-review-wave905",
    "`506` function rows",
    "`41` selected owner families",
    "CWorld 38",
    "CWorldPhysicsManager 32",
    "CThing 28",
    "CThing__InitRenderThingFromInitMeshName",
    "CWorld__InitOccupancyBitplanes",
    "CWorldPhysicsManager__CreateThingByType",
    "unit-battleengine-gameplay-static-review-wave906",
    "`633` function rows",
    "`75` families",
    "Damage / destruction / spawn",
    "CSpawnerThng 14",
    "CSpawnerThng__DoSpawn",
    "CUnit__VFunc08_InitAndAddToWorld",
    "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
    "CWorld__LoadWorld",
    "0x0050b9c0",
    "CWorld__LoadScriptEvents",
    "0x0050ac70",
    "CWorld__LoadWorldFile",
    "0x0050d9e0",
    "CWorld__DeserializeWorld",
    "CWorld__SpawnInitialThings",
    "0x0050dcb0",
    "0x0050df80",
    "CWorldPhysicsManager__ResolveLoadedDefinitionReferences",
    "0x0048c650 InitThing__CreateThingByType",
    "0x0040e280 CInitThing__LoadFromMemBuffer",
    "0x0048dcf0 CInitThing__ctor",
    "0x004e3010 CSpawnerThng__Init",
    "0x004e36c0 CSpawnerThng__FindSpawnerByName",
    "0x004e3c60 CSpawnerThng__DoSpawn",
    "0x004e3f90 CSpawnerThng__ProcessSpawnWave",
    "CSpawnerThng__IsSpawnTypeAllowed",
    "0x0050f680 CSpawnerThng__IsSpawnTypeAllowed",
    "0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
    "CUnit__SetSpawnCooldownState3",
    "copied/app-owned",
    "no runtime object identity",
    r"G:\GhidraBackups\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified",
    r"G:\GhidraBackups\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified",
    r"G:\GhidraBackups\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified",
)

READINESS_TOKENS = (
    "World / Thing / Spawn / Object-Reference Bridge Proof Plan Readiness Note",
    "proof plan complete, not runtime proof",
    "not a new static re-audit wave",
    "not a Ghidra mutation",
    "not a runtime test",
    "not a mission execution proof",
    "not a live loose-MSL loading proof",
    "not a BEA patch",
    "not a Godot slice",
    "not a rebuild parity claim",
)

FORBIDDEN_PHRASES = (
    "runtime getthingref behavior proven",
    "runtime spawnthing behavior proven",
    "runtime world loading behavior proven",
    "runtime object identity proven",
    "runtime spawner behavior proven",
    "runtime unit/battleengine spawn behavior proven",
    "live loose-msl loading proven",
    "packed-resource script selection proven",
    "exact world layout proven",
    "exact thing layout proven",
    "exact spawner layout proven",
    "exact source-body identity proven",
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


def check_plan(failures: list[str]) -> None:
    text = read_text(PLAN)
    for token in (*STATIC_TOKENS, *PLAN_TOKENS):
        require(token in text, f"plan missing token: {token}", failures)
    check_no_overclaims(PLAN, failures)
    require(read_text(LORE_PLAN) == text, "lore world/thing/spawn plan mirror mismatch", failures)


def check_readiness(failures: list[str]) -> None:
    text = read_text(READINESS)
    readiness_anchor_tokens = (
        "world-thing-spawn-object-reference-proof-plan",
        "missionscript-iscript-static-contract.md",
        "IScript__GetThingRef",
        "IScript__SpawnThing",
        "CThingPtrDataType",
        "`57` level rows",
        "`418` `GetThingRef`",
        "`18` `SpawnThing`",
        "`436` total thing/spawn refs",
        "0x0052ff30",
        "`144` contiguous `0x40`-byte descriptor records",
        "0x0064ce50",
        "0x0064f210",
        "0x005392a0 CScriptObjectCode__CollectSpawnThings",
        "opcode `0x18`",
        "CWorldMeshList__Add",
        "CWorld__LoadWorld",
        "CWorldPhysicsManager__CreateThingByType",
        "0x0048c650 InitThing__CreateThingByType",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName",
        "copied/app-owned only, no runtime object identity claim",
    )
    for token in (*STATIC_TOKENS, *READINESS_TOKENS, *readiness_anchor_tokens):
        require(token in text, f"readiness missing token: {token}", failures)
    check_no_overclaims(READINESS, failures)


def check_source_docs(failures: list[str]) -> None:
    for path in (
        MISSION_CONTRACT,
        MISSION_PLAN,
        MISSION_STATIC,
        MISSION_THING,
        MSL_DOC,
        MSL_COMMANDS,
        MESH_REVIEW,
        UNIT_REVIEW,
        UNIT_CONTRACT,
    ):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing world/thing/spawn plan link", failures)
        check_no_overclaims(path, failures)


def check_front_doors(failures: list[str]) -> None:
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX):
        text = read_text(path)
        require(PLAN_LINK in text, f"{path.relative_to(ROOT)} missing world/thing/spawn plan link", failures)
        require(SCHEMA_LINK in text, f"{path.relative_to(ROOT)} missing copied-corpus schema plan link", failures)
        require("World / Thing / Spawn / Object-Reference Bridge Proof Plan" in text, f"{path.relative_to(ROOT)} missing world/thing/spawn label", failures)
        require("MissionScript / IScript Static Contract" in text, f"{path.relative_to(ROOT)} missing MissionScript static-contract label", failures)
        check_no_overclaims(path, failures)

    require(read_text(BACKLOG) == read_text(LORE_BACKLOG), "transition backlog lore mirror mismatch", failures)
    require(read_text(MAPPED) == read_text(LORE_MAPPED), "mapped systems lore mirror mismatch", failures)
    require(read_text(BIN_INDEX) == read_text(LORE_BIN_INDEX), "binary index lore mirror mismatch", failures)
    require(read_text(RE_INDEX) == read_text(LORE_RE_INDEX), "RE index lore mirror mismatch", failures)

    backlog = read_text(BACKLOG)
    require(
        "Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan" in backlog,
        "backlog missing completed world/thing/spawn bridge slice",
        failures,
    )
    require(
        "Completed World / Thing / Spawn Copied-Corpus Schema Proof" in backlog,
        "backlog missing completed copied-corpus schema result",
        failures,
    )
    require(
        "Completed World / Thing / Spawn Spawner Handoff Static Proof" in backlog,
        "backlog missing completed spawner handoff static proof",
        failures,
    )
    require(
        "Completed MissionScript / IScript static-contract extraction slice" in backlog,
        "backlog missing completed MissionScript static-contract slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [MissionScript / IScript Static Contract]" not in backlog,
        "backlog still has stale active MissionScript static-contract slice",
        failures,
    )

    mapped = read_text(MAPPED)
    require("Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan" in mapped, "mapped systems missing completed world/thing/spawn bridge slice", failures)
    require("Completed World / Thing / Spawn copied-corpus schema result" in mapped, "mapped systems missing completed copied-corpus schema result", failures)
    require("Completed World / Thing / Spawn Spawner Handoff Static Proof" in mapped, "mapped systems missing completed spawner handoff static proof", failures)
    require("Completed MissionScript / IScript static-contract extraction slice" in mapped, "mapped systems missing completed static-contract slice", failures)
    require("Active MissionScript / IScript static-contract extraction slice" not in mapped, "mapped systems still has stale active static-contract slice", failures)


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
        scripts.get("test:world-thing-spawn-object-reference-proof-plan") == r"py -3 tools\world_thing_spawn_object_reference_proof_plan_probe.py --check",
        "missing package world/thing/spawn proof-plan script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_plan(failures)
    check_readiness(failures)
    check_source_docs(failures)
    check_front_doors(failures)
    check_progress_unchanged(failures)
    check_package(failures)

    if failures:
        print("World / Thing / Spawn object-reference proof-plan probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("World / Thing / Spawn object-reference proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
