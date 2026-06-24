#!/usr/bin/env python3
"""Validate Wave906 Unit/BattleEngine/gameplay static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave906-unit-battleengine-gameplay-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BASELINE_JSON = BASE / "unit-battleengine-gameplay-baseline.json"
FAMILY_TSV = BASE / "unit-battleengine-gameplay-family-summary.tsv"
CLUSTER_TSV = BASE / "unit-battleengine-gameplay-cluster-summary.tsv"
ANCHORS_TSV = BASE / "unit-battleengine-gameplay-function-anchors.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_battleengine_gameplay_static_review_wave906_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-review-2026-05-26.md"
STATIC_SYSTEM_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
UNIT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNITAI_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
BATTLEENGINE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md"
ROUND_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Round.cpp" / "_index.md"
CANNON_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Cannon.cpp" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified"

EXPECTED_FAMILIES = {
    "CUnit": 90,
    "CUnitAI": 63,
    "CBattleEngine": 47,
    "CBattleEngineWalkerPart": 27,
    "CBattleEngineJetPart": 23,
    "BattleEngineConfigurations": 4,
    "CBattleEngineData": 4,
    "CWeapon": 12,
    "CWeaponRound": 2,
    "CWeaponStatement": 7,
    "CWeaponModeStatement": 6,
    "CPhysicsWeaponValue": 2,
    "CPhysicsWeaponValueList": 3,
    "CPhysicsWeaponModeValue": 3,
    "CPhysicsWeaponModeValueList": 3,
    "CRound": 13,
    "CRoundSeek": 4,
    "CRoundStatement": 6,
    "CPhysicsRoundValue": 4,
    "CPhysicsRoundValueList": 3,
    "CCollisionSeekingRound": 17,
    "CCollisionSeekingInfantryBloke": 3,
    "ProjectileBurst": 3,
    "TargetProfileContext": 2,
    "TargetSet": 2,
    "CGroundUnit": 6,
    "CGroundVehicleGuide": 3,
    "CGroundAttackAircraft": 6,
    "CGroundAttackAI": 3,
    "CGroundAttackGuide": 2,
    "CAirUnit": 8,
    "CBigAirUnit": 3,
    "CAirGuide": 6,
    "CDropship": 6,
    "CDropshipAI": 2,
    "CMCDropship": 5,
    "CInfantryUnit": 3,
    "CInfantryAI": 2,
    "CInfantryGuide": 6,
    "CMech": 3,
    "CMechAI": 2,
    "CMechGuide": 5,
    "CGillM": 9,
    "CGillMAI": 2,
    "CGillMHead": 3,
    "CGillMHeadAI": 6,
    "CHiveBoss": 2,
    "CMCHiveBoss": 3,
    "CCannon": 7,
    "CMCCannon": 4,
    "CDamage": 8,
    "CGeneralVolume": 23,
    "CUnitBehaviour": 3,
    "CUnitNavMap": 3,
    "CUnitAlligence": 2,
    "CSquad": 4,
    "CSquadNormal": 31,
    "CRelaxedSquad": 3,
    "CSpawnerThng": 14,
    "CSpawnerThing": 2,
    "CSpawnerData": 2,
    "CSpawnerStatement": 5,
    "CPhysicsSpawnerValue": 2,
    "CPhysicsSpawnerValueList": 3,
    "PickupSpawn": 2,
    "CRepairPadAI": 6,
    "CCockpit": 3,
    "CDXCockpit": 2,
    "CDestructableSegmentsController": 19,
    "CDestructableSegment": 6,
    "CDestroyableSegment": 13,
    "CDestroyableCoreSegment": 10,
    "CDestroyableEndSegment": 2,
    "CDestroyableSwapSegment": 3,
    "CDestroyableSegmentVariant": 2,
}

EXPECTED_CLUSTERS = {
    "unit-core": 199,
    "battleengine-player": 133,
    "weapons-rounds": 106,
    "unit-subclasses": 102,
    "damage-destruction-spawn": 93,
}

REQUIRED_ANCHORS = {
    "CUnit__ApplyDamage",
    "CUnit__GetCurrentHealthOrSubtreeHealth",
    "CUnitAI__UpdateActivationStateAndSpawnPickup",
    "CUnitAI__UpdateDeployAimAndScheduleEvent",
    "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "CBattleEngine__AddProjectile",
    "CBattleEngine__Morph",
    "CBattleEngine__HandleCloak",
    "CBattleEngine__AugmentWeapon",
    "CBattleEngineJetPart__WeaponFired",
    "CBattleEngineWalkerPart__WeaponFired",
    "CWeapon__HandleFireBurstEvent",
    "CRound__SpawnConfiguredProjectile",
    "CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
    "CDamage__CreateTextureBuffer",
    "CGeneralVolume__SpawnPickupAndDispatch",
    "CSquadNormal__SelectBestEngagementTarget",
    "CSpawnerThng__DoSpawn",
    "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
    "CDestroyableSegment__VFunc_03_ApplyDamage",
    "BattleEngineConfigurations__GetConfiguration",
    "CBattleEngineData__LoadFromMemBuffer",
}

CORE_ANCHORS = (
    "Wave906",
    "unit-battleengine-gameplay-static-review-wave906",
    "static-coherent Unit/BattleEngine/gameplay core",
    "6113/6113 = 100.00%",
    "633",
    "75",
    "CUnit",
    "90",
    "CUnitAI",
    "63",
    "CBattleEngine",
    "47",
    "CSquadNormal",
    "31",
    "CBattleEngineWalkerPart",
    "27",
    "CBattleEngineJetPart",
    "23",
    "CGeneralVolume",
    "23",
    "CDestructableSegmentsController",
    "19",
    "CCollisionSeekingRound",
    "17",
    "CUnit__ApplyDamage",
    "CUnitAI__UpdateActivationStateAndSpawnPickup",
    "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "CBattleEngine__AddProjectile",
    "CBattleEngine__Morph",
    "CBattleEngine__HandleCloak",
    "CBattleEngine__AugmentWeapon",
    "CBattleEngineJetPart__WeaponFired",
    "CBattleEngineWalkerPart__WeaponFired",
    "CWeapon__HandleFireBurstEvent",
    "CRound__SpawnConfiguredProjectile",
    "CSpawnerThng__DoSpawn",
    "CDestroyableSegment__VFunc_03_ApplyDamage",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime damage behavior proven",
    "runtime ai behavior proven",
    "runtime weapon behavior proven",
    "runtime input behavior proven",
    "runtime gameplay outcomes proven",
    "all object layouts proven",
    "all systems complete",
    "every system is complete",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name, entries in queue.get("priorityQueues", {}).items():
        require(entries == [], f"priority queue not empty: {name}", failures)


def check_evidence(failures: list[str]) -> None:
    baseline = read_json(BASELINE_JSON)
    require(baseline.get("wave") == 906, "baseline wave mismatch", failures)
    require(baseline.get("tag") == "unit-battleengine-gameplay-static-review-wave906", "baseline tag mismatch", failures)
    require(baseline.get("classification") == "static-coherent Unit/BattleEngine/gameplay core", "baseline classification mismatch", failures)
    require(baseline.get("selectedFamilyCount") == 75, "baseline family count mismatch", failures)
    require(baseline.get("selectedFunctionRows") == 633, "baseline function count mismatch", failures)
    require(baseline.get("commentedRows") == 633, "baseline commented count mismatch", failures)
    require(baseline.get("cleanSignatureRows") == 633, "baseline clean-signature count mismatch", failures)
    require(baseline.get("missingAnchors") == [], "baseline missing anchors", failures)

    families = {row["family"]: int(row["rows"]) for row in read_tsv(FAMILY_TSV)}
    require(families == EXPECTED_FAMILIES, "family summary mismatch", failures)

    clusters = {row["cluster"]: int(row["rows"]) for row in read_tsv(CLUSTER_TSV)}
    require(clusters == EXPECTED_CLUSTERS, "cluster summary mismatch", failures)

    anchors = read_tsv(ANCHORS_TSV)
    require(len(anchors) == 633, "anchor row count mismatch", failures)
    names = {row["name"] for row in anchors}
    for name in REQUIRED_ANCHORS:
        require(name in names, f"missing anchor: {name}", failures)
    for row in anchors:
        signature = row.get("signature", "")
        require(row.get("comment", "").strip() != "", f"anchor missing comment: {row.get('name')}", failures)
        require(not signature.startswith("undefined "), f"anchor undefined signature: {row.get('name')}", failures)
        require(re.search(r"\bparam_\d+\b", signature) is None, f"anchor param_N signature: {row.get('name')}", failures)
        require(row.get("status") == "OK", f"anchor status mismatch: {row.get('name')}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = (
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM_REVIEW,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        UNIT_INDEX,
        UNITAI_INDEX,
        BATTLEENGINE_INDEX,
        ROUND_INDEX,
        CANNON_INDEX,
        RE_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-unit-battleengine-gameplay-static-review-wave906")
        == r"py -3 tools\ghidra_unit_battleengine_gameplay_static_review_wave906_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_evidence(failures)
    check_docs(failures)

    if failures:
        print("Wave906 Unit/BattleEngine/gameplay static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave906 Unit/BattleEngine/gameplay static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
