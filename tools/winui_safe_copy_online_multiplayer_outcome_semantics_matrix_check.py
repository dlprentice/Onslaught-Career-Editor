#!/usr/bin/env python3
"""Validate the original-binary multiplayer outcome semantics matrix."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-multiplayer-outcome-semantics-matrix.v1.json"
MISSION_EVENTS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "mission-events-index.md"
GAME_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "gameplay" / "game-system.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"

EXPECTED_SCHEMA = "winui-original-binary-multiplayer-outcome-semantics-matrix.v1"
EXPECTED_SCOPE = "original-binary-p1p2-multiplayer-outcome-semantics-matrix-not-runtime-proof"
EXPECTED_STATUS = (
    "complete public-safe static candidate matrix; no runtime outcome, co-op, versus, online, matchmaking, "
    "native BEA netcode, or active P3/P4 gameplay proof"
)
EXPECTED_LEVELS = {
    851: {"directory": "level851", "eventRows": 6, "objectiveIds": 0, "levelWonLooseScriptRows": 0, "levelLostLooseScriptRows": 0, "rank": 3},
    854: {"directory": "level854", "eventRows": 2, "objectiveIds": 0, "levelWonLooseScriptRows": 0, "levelLostLooseScriptRows": 0, "rank": 1},
    855: {"directory": "level855", "eventRows": 4, "objectiveIds": 0, "levelWonLooseScriptRows": 0, "levelLostLooseScriptRows": 0, "rank": 2},
    860: {"directory": "level860", "eventRows": 12, "objectiveIds": 0, "levelWonLooseScriptRows": 0, "levelLostLooseScriptRows": 0, "rank": 4},
}
EXPECTED_HOOK_TARGETS = {
    "CGame__MPDeclarePlayerWon": "0x0046f360",
    "CGame__MPDeclareGameDrawn": "0x0046f3e0",
    "CGame__DeclarePlayerDead": "0x0046f550",
    "CGame__RespawnPlayer": "0x00470120",
    "CGame__GetPlayerLives": "0x004725f0",
    "CGame__DeclareLevelWon": "0x0046f2f0",
    "CGame__DeclareLevelLost": "0x0046f430",
    "IScript__LevelWon": "0x005381e0",
    "IScript__LevelLost": "0x005381a0",
    "IScript__LevelLostString": "0x005381c0",
}
FALSE_BOUNDARY_KEYS = (
    "runtimeProofCreatedByThisMatrix",
    "baseOnlineMultiplayerReady",
    "secondPhysicalHostProof",
    "multiHostLanProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "coOpModeRuntimeProof",
    "versusModeRuntimeProof",
    "teamVersusRuntimeProof",
    "spectatorAdminRuntimeProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "safeToPatchMPlayersAbove2",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
)
ZERO_BOUNDARY_KEYS = (
    "modeRuntimeProofSlicesAdded",
    "coOpVersusModeRuntimeProofSlicesAdded",
    "newBeaLaunchCount",
    "cdbAttachCount",
    "nPlayerOriginalBinaryRuntimeProof",
)
FALSE_NON_CLAIM_KEYS = (
    "runtimeOutcomeProof",
    "coOpModeRuntimeProof",
    "versusModeRuntimeProof",
    "teamVersusRuntimeProof",
    "spectatorAdminRuntimeProof",
    "baseOnlineMultiplayerReady",
    "secondPhysicalHostProof",
    "multiHostLanProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "moreThanTwoOriginalBinaryRuntimeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
)


class MultiplayerOutcomeSemanticsMatrixError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MultiplayerOutcomeSemanticsMatrixError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def require_source_tokens() -> None:
    mission_index = read_text(MISSION_EVENTS_INDEX)
    for level, expected in EXPECTED_LEVELS.items():
        token = (
            f"| {level} | {expected['directory']} | {expected['eventRows']} | {expected['objectiveIds']} | "
            "0 | 0 | 0 | 0 | 0 | 0 |"
        )
        require(token in mission_index, f"mission-events index missing candidate row: {level}")

    game_system = read_text(GAME_SYSTEM)
    for token in (
        "MPDeclarePlayerWon(otherPlayer)",
        "Co-op",
        "Versus",
        "DeclareLevelLost()",
        "Default lives per player",
        "mPlayer1Lives = 2",
        "mPlayer2Lives = 2",
    ):
        require(token in game_system, f"game-system source summary missing token: {token}")

    ghidra = read_text(GHIDRA_REFERENCE)
    for name, address in EXPECTED_HOOK_TARGETS.items():
        require(address in ghidra and name in ghidra, f"GHIDRA reference missing hook target: {name} {address}")


def validate_contract(path: Path = CONTRACT) -> dict[str, Any]:
    contract = read_json(path)
    require(contract.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(contract.get("scope") == EXPECTED_SCOPE, "scope mismatch")
    require(contract.get("status") == EXPECTED_STATUS, "status boundary drifted")
    require(contract.get("proofClass") == "static-candidate-matrix-not-runtime-outcome-proof", "proof class mismatch")

    baseline = object_at(contract, "currentRuntimeBaseline")
    require(baseline.get("baselineLevelId") == 850, "baseline level must stay 850")
    require(baseline.get("modeSemanticsObserverProven") is True, "baseline observer proof missing")
    require(baseline.get("unforcedTransitionHitCount") == 0, "baseline must preserve zero unforced transitions")
    require(baseline.get("forcedWinDeathRespawn") is False, "baseline must preserve no forced transitions")
    require(baseline.get("currentRuntimeModeClassification") == "unclassified-local-multiplayer", "baseline mode classification drifted")

    rows = list_at(contract, "candidateLevels")
    by_level = {}
    for row in rows:
        require(isinstance(row, dict), "candidate level row must be an object")
        by_level[row.get("levelId")] = row
    require(set(by_level) == set(EXPECTED_LEVELS), f"candidate level set mismatch: {sorted(by_level)}")
    for level, expected in EXPECTED_LEVELS.items():
        row = by_level[level]
        require(row.get("directory") == expected["directory"], f"level {level} directory mismatch")
        require(row.get("eventRows") == expected["eventRows"], f"level {level} event count mismatch")
        require(row.get("objectiveIds") == expected["objectiveIds"], f"level {level} objective count mismatch")
        require(
            row.get("levelWonLooseScriptRows") == 0 and row.get("levelLostLooseScriptRows") == 0,
            f"level {level} must have zero loose LevelWon/LevelLost rows",
        )
        require(row.get("runtimeSelectionRank") == expected["rank"], f"level {level} rank mismatch")
        require("CGame" in str(row.get("candidateReason")), f"level {level} reason must point at CGame outcome paths")

    selected = object_at(contract, "selectedRuntimeCandidate")
    require(selected.get("levelId") == 854, "selected runtime candidate must be level 854")
    require(selected.get("directory") == "level854", "selected runtime candidate directory mismatch")
    require(selected.get("runtimeProofCreatedByThisMatrix") is False, "matrix must not claim runtime proof")
    require("CGame__MPDeclarePlayerWon" in str(selected.get("selectionReason")), "selected runtime candidate must name MPDeclarePlayerWon")

    targets = object_at(contract, "requiredRuntimeHookTargets")
    missing_targets = sorted(set(EXPECTED_HOOK_TARGETS) - set(targets))
    extra_targets = sorted(set(targets) - set(EXPECTED_HOOK_TARGETS))
    wrong_targets = sorted(
        name for name, address in EXPECTED_HOOK_TARGETS.items() if targets.get(name) != address
    )
    require(
        not missing_targets and not extra_targets and not wrong_targets,
        "required runtime hook target set or address mismatch; "
        f"missing={missing_targets} extra={extra_targets} wrong={wrong_targets}",
    )

    anchors = object_at(contract, "staticAnchors")
    require("zero loose LevelWon" in str(anchors.get("missionEventIndex")), "mission-event anchor missing zero LevelWon/LevelLost boundary")
    require("MPDeclarePlayerWon" in str(anchors.get("sourceOutcomeSemantics")), "source outcome anchor missing MPDeclarePlayerWon")
    require("0x0046f360" in str(anchors.get("retailOutcomeAddresses")), "retail address anchor missing MPDeclarePlayerWon")

    boundary = object_at(contract, "runtimeProofBoundary")
    for key in ZERO_BOUNDARY_KEYS:
        require(boundary.get(key) == 0, f"runtime boundary zero counter drifted: {key}")
    for key in FALSE_BOUNDARY_KEYS:
        require(boundary.get(key) is False, f"runtime boundary overclaim must remain false: {key}")

    requirements = "\n".join(str(item) for item in list_at(contract, "nextRuntimeProofRequirements"))
    for token in (
        "copied clean-specimen BEA.exe",
        "exact managed copied BEA process",
        "foreground, unoccluded visual captures",
        "managed stop success",
        "CGame__MPDeclarePlayerWon",
        "P1/P2 local copied-runtime outcome observation",
    ):
        require(token in requirements, f"next runtime proof requirement missing: {token}")

    non_claims = object_at(contract, "nonClaims")
    require(set(non_claims) == set(FALSE_NON_CLAIM_KEYS), "non-claim key set drifted")
    for key in FALSE_NON_CLAIM_KEYS:
        require(non_claims.get(key) is False, f"non-claim must remain false: {key}")

    require_source_tokens()
    return {
        "schemaVersion": contract["schemaVersion"],
        "scope": contract["scope"],
        "proofClass": contract["proofClass"],
        "candidateLevels": sorted(by_level),
        "selectedRuntimeCandidate": selected["levelId"],
        "requiredHookTargetCount": len(targets),
        "runtimeProofCreatedByThisMatrix": boundary["runtimeProofCreatedByThisMatrix"],
        "modeRuntimeProofSlicesAdded": boundary["modeRuntimeProofSlicesAdded"],
        "coOpVersusModeRuntimeProofSlicesAdded": boundary["coOpVersusModeRuntimeProofSlicesAdded"],
        "baseOnlineMultiplayerReady": boundary["baseOnlineMultiplayerReady"],
        "activeP3P4OriginalBinaryGameplayProof": boundary["activeP3P4OriginalBinaryGameplayProof"],
        "claimBoundary": contract["claimBoundary"],
    }


def run_self_test() -> None:
    good = read_json(CONTRACT)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "matrix.json"
        write_json(path, good)
        validate_contract(path)

        bad = json.loads(json.dumps(good))
        bad["selectedRuntimeCandidate"]["levelId"] = 851
        write_json(path, bad)
        try:
            validate_contract(path)
        except MultiplayerOutcomeSemanticsMatrixError:
            pass
        else:
            raise AssertionError("wrong selected candidate should fail")

        bad = json.loads(json.dumps(good))
        bad["runtimeProofBoundary"]["runtimeProofCreatedByThisMatrix"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except MultiplayerOutcomeSemanticsMatrixError:
            pass
        else:
            raise AssertionError("runtime proof overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["requiredRuntimeHookTargets"]["CGame__MPDeclarePlayerWon"] = "0x00000000"
        write_json(path, bad)
        try:
            validate_contract(path)
        except MultiplayerOutcomeSemanticsMatrixError:
            pass
        else:
            raise AssertionError("wrong hook address should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary multiplayer outcome semantics matrix checker self-test: PASS")
        return 0
    if not args.check:
        raise SystemExit("use --check or --self-test")
    print(json.dumps(validate_contract(CONTRACT), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MultiplayerOutcomeSemanticsMatrixError as exc:
        print(f"WinUI original-binary multiplayer outcome semantics matrix check: FAIL: {exc}")
        raise SystemExit(2)
