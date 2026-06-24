#!/usr/bin/env python3
"""Validate the original-binary P3/P4 runtime feasibility map."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-p3p4-runtime-feasibility-map.v1.json"
SLOT_GUARD = ROOT / "roadmap" / "original-binary-online-slot-ceiling-guard.v1.json"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_online_p3p4_runtime_feasibility_map_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
PACKAGE_JSON = ROOT / "package.json"
SOURCE_GAME_CPP = ROOT / "references" / "Onslaught" / "game.cpp"
SOURCE_GAME_H = ROOT / "references" / "Onslaught" / "game.h"
SOURCE_ENGINE_H = ROOT / "references" / "Onslaught" / "engine.h"
SOURCE_FRONTEND_CPP = ROOT / "references" / "Onslaught" / "FrontEnd.cpp"
SOURCE_CONTROLLER_CPP = ROOT / "references" / "Onslaught" / "Controller.cpp"

EXPECTED_SCHEMA = "winui-original-binary-online-p3p4-runtime-feasibility-map.v1"
EXPECTED_SCOPE = "original-binary-online-p3p4-runtime-feasibility-map"
EXPECTED_SCRIPT = r"py -3 tools\winui_safe_copy_online_p3p4_runtime_feasibility_map_check_test.py && py -3 tools\winui_safe_copy_online_p3p4_runtime_feasibility_map_check.py --self-test && py -3 tools\winui_safe_copy_online_p3p4_runtime_feasibility_map_check.py --check"
EXPECTED_ROW_IDS = {
    "source-max-players-capacity",
    "current-mplayers-gate",
    "controller-assignment-p1-p2-trap",
    "engine-viewpoints-two",
    "reconnect-interface-two",
    "lives-respawn-results-two",
    "input-flush-loop-by-mplayers",
    "gameplay-systems-multiplayer-branches",
}
FALSE_BOUNDARY_KEYS = (
    "moreThanTwoOriginalBinaryRuntimeProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "sourceOnlyMaxPlayersIsRuntimeProof",
    "quadSplitBranchIsRuntimeProof",
    "mapCompleteForRuntimeAttempt",
    "safeToPatchMPlayersAbove2",
    "permanentImpossibilityClaim",
)
FALSE_NON_CLAIM_KEYS = (
    "moreThanTwoOriginalBinaryRuntimeProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "coOpModeRuntimeProof",
    "versusModeRuntimeProof",
    "teamVersusRuntimeProof",
    "multiHostLanProof",
    "secondPhysicalHostProof",
    "publicMatchmakingProof",
    "nativeBeaNetcodeProof",
    "deterministicSyncProof",
    "rollbackProof",
    "antiCheatProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
)


class P3P4FeasibilityMapError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise P3P4FeasibilityMapError(message)


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


def require_tokens(path: Path, tokens: tuple[str, ...]) -> None:
    text = read_text(path)
    for token in tokens:
        require(token in text, f"{path} missing token: {token}")


def require_source_tokens() -> None:
    require_tokens(
        SOURCE_GAME_CPP,
        (
            "WORLD.IsMultiplayer()",
            "mPlayers=2",
            "mPlayers=1",
            "I don't support more than 2 players.",
            "ASSERT(i == 1)",
            "(mPlayers==3) || (mPlayers==4)",
            "3/4 player quad split",
            "ENGINE.SetViewpoint(2",
            "ENGINE.SetViewpoint(3",
            "RECONNECT_INTERFACE[0].Render",
            "RECONNECT_INTERFACE[1].Render",
            "mPlayer1Lives",
            "mPlayer2Lives",
            "CGame::IsMultiplayer()",
            ">849",
            "< 900",
        ),
    )
    require_tokens(
        SOURCE_GAME_H,
        (
            "#define MAX_PLAYERS 4",
            "mPlayer[ MAX_PLAYERS ]",
            "mController[ MAX_PLAYERS ]",
            "mCurrentCamera[ MAX_PLAYERS ]",
            "mPlayer1Lives,mPlayer2Lives",
        ),
    )
    require_tokens(
        SOURCE_ENGINE_H,
        (
            "#define VIEWPOINTS",
            "mCamera[VIEWPOINTS]",
            "mViewport[VIEWPOINTS]",
            "mPlayer[VIEWPOINTS]",
            "SetViewpoint",
            "SetNumViewpoints",
        ),
    )
    require_tokens(SOURCE_FRONTEND_CPP, ("GetPlayer0ControllerPort", "mPlayer0ControllerPort"))
    require_tokens(SOURCE_CONTROLLER_CPP, ("RECONNECT_INTERFACE[0]", "RECONNECT_INTERFACE[1]"))


def require_cross_contracts() -> None:
    slot = read_json(SLOT_GUARD)
    ceiling = object_at(slot, "currentOriginalBinaryRuntimeCeiling")
    require(ceiling.get("maxOriginalBinaryActiveSlotsProven") == 2, "slot guard max active slots drifted")
    require(ceiling.get("nPlayerOriginalBinaryRuntimeProof") == 0, "slot guard N-player proof drifted")
    require(ceiling.get("activeP3P4OriginalBinaryGameplayProof") is False, "slot guard P3/P4 overclaim")
    require(ceiling.get("beyondTwoPlayersRequiresNewProofClass") is True, "slot guard proof-class requirement missing")
    require(ceiling.get("permanentImpossibilityClaim") is False, "slot guard permanent-impossibility claim drifted")

    scalability = read_json(SCALABILITY)
    runtime = object_at(scalability, "currentOriginalBinaryRuntime")
    require(runtime.get("maxRuntimePlayerSlotsProven") == 2, "scalability runtime cap drifted")
    require(runtime.get("nPlayerOriginalBinaryRuntimeProof") == 0, "scalability N-player proof drifted")
    require(runtime.get("beyondTwoPlayersRequiresNewProofClass") is True, "scalability beyond-two requirement missing")
    architecture = object_at(scalability, "scalableArchitecture")
    require(architecture.get("minimumArchitectureAcceptanceSlots") == 4, "scalability architecture no longer admits four slots")
    policy = object_at(architecture, "slotPolicy")
    require(policy.get("maxOriginalBinaryActiveSlots") == 2, "scalability slot policy cap drifted")
    require(policy.get("unsupportedSlotsRejected") is True, "scalability unsupported-slot rejection missing")
    p3p4_policy = object_at(architecture, "p3p4RuntimeFeasibilityMapPolicy")
    require(p3p4_policy.get("proofSchema") == EXPECTED_SCHEMA, "scalability P3/P4 map schema missing")
    require(p3p4_policy.get("mapProofClass") == "static-blast-radius-map-not-runtime-proof", "scalability P3/P4 proof class missing")
    require(p3p4_policy.get("p3p4FeasibilityScope") == "static-blast-radius-not-runtime-proof", "scalability P3/P4 scope missing")
    require(p3p4_policy.get("nPlayerOriginalBinaryRuntimeProof") == 0, "scalability P3/P4 N-player proof drifted")
    require(p3p4_policy.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "scalability P3/P4 active slots overclaim")
    require(p3p4_policy.get("metadataOnlySlots") == ["P3", "P4"], "scalability P3/P4 metadata slots missing")
    require(p3p4_policy.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "scalability P3/P4 rejected routes missing")
    require(p3p4_policy.get("safeToPatchMPlayersAbove2") is False, "scalability P3/P4 safe-to-patch overclaim")
    require(p3p4_policy.get("mapCompleteForRuntimeAttempt") is False, "scalability P3/P4 map-complete overclaim")
    require(p3p4_policy.get("beyondTwoPlayersRequiresNewProofClass") is True, "scalability P3/P4 proof-class requirement missing")
    ladder = [str(item) for item in list_at(scalability, "nextProofLadder")]
    require(not any("N-slot runtime feasibility map" in item for item in ladder), "scalability still lists completed P3/P4 map as next rung")
    require(any("P3/P4 proof-class deep dive" in item for item in ladder), "scalability missing P3/P4 proof-class deep-dive next rung")


def validate_contract(path: Path = CONTRACT) -> dict[str, Any]:
    contract = read_json(path)
    require(contract.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(contract.get("scope") == EXPECTED_SCOPE, "scope mismatch")
    require(contract.get("status") == "complete public-safe P3/P4 blast-radius map; no BEA launch or runtime proof", "status mismatch")

    boundary = object_at(contract, "proofBoundary")
    require(boundary.get("mapProofClass") == "static-blast-radius-map-not-runtime-proof", "map proof class mismatch")
    require(boundary.get("p3p4FeasibilityScope") == "static-blast-radius-not-runtime-proof", "scope boundary mismatch")
    require(boundary.get("newBeaLaunchCount") == 0, "map must not launch BEA")
    require(boundary.get("cdbAttachCount") == 0, "map must not attach CDB")
    require(boundary.get("ghidraMutationCount") == 0, "map must not mutate Ghidra")
    require(boundary.get("maxOriginalBinaryActiveSlotsProven") == 2, "runtime slot proof must stay two")
    require(boundary.get("maxRuntimePlayerSlotsProven") == 2, "runtime player proof must stay two")
    require(boundary.get("maxRetailPlayersProven") == 2, "retail player proof must stay two")
    require(boundary.get("retailViewpointsProven") == 2, "retail viewpoint proof must stay two")
    require(boundary.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    require(boundary.get("moreThanTwoOriginalBinaryRuntimeProofSlices") == 0, "more-than-two proof slices must stay zero")
    require(boundary.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted gameplay slots must stay P1/P2")
    require(boundary.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots must stay P3/P4")
    require(boundary.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected gameplay slots must stay P3/P4")
    require(boundary.get("p3p4GameplayInputRejected") is True, "P3/P4 gameplay input must stay rejected")
    require(boundary.get("beyondTwoPlayersRequiresNewProofClass") is True, "beyond-two must require a new proof class")
    require(boundary.get("absenceOfCurrentProofIsNotProofOfPermanentAbsence") is True, "absence/non-impossibility boundary missing")
    for key in FALSE_BOUNDARY_KEYS:
        require(boundary.get(key) is False, f"boundary overclaim must remain false: {key}")

    anchors = object_at(contract, "sourceStaticAnchors")
    require("MAX_PLAYERS 4" in str(anchors.get("capacityDeclaration")), "capacity declaration missing")
    require("mPlayers to 2" in str(anchors.get("currentPlayerCountGate")), "mPlayers gate missing")
    require("I don't support more than 2 players" in str(anchors.get("controllerAssignmentTrap")), "controller trap missing")
    require("VIEWPOINTS 2" in str(anchors.get("engineViewpointCeiling")), "viewpoint ceiling missing")
    require("not proof" in str(anchors.get("latentQuadSplitBranch")), "quad-split non-proof boundary missing")
    require(len(list_at(anchors, "runtimeRetailAnchors")) >= 5, "retail anchor list too narrow")

    rows = list_at(contract, "blastRadiusRows")
    row_ids = {str(row.get("id")) for row in rows if isinstance(row, dict)}
    require(row_ids == EXPECTED_ROW_IDS, f"blast-radius row id mismatch: {sorted(row_ids)}")
    for row in rows:
        require(isinstance(row, dict), "blast-radius row must be an object")
        require(row.get("runtimeProofStatus") == "unproven", f"row overclaims runtime proof: {row.get('id')}")
        require(row.get("evidenceClass") == "source-static", f"row evidence class must stay source-static: {row.get('id')}")
        require(row.get("supportsOriginalBinaryRuntimeProof") is False, f"row source-only evidence cannot support runtime proof: {row.get('id')}")
        require(isinstance(row.get("anchors"), list) and len(row["anchors"]) >= 2, f"row needs grounded anchors: {row.get('id')}")
        require(str(row.get("beforeRuntimeAttempt", "")).strip(), f"row needs beforeRuntimeAttempt: {row.get('id')}")

    blockers = [str(item) for item in list_at(contract, "hardBlockersBeforeP3P4Runtime")]
    for token in ("CEngine viewpoint storage", "mPlayers=3", "Controller assignment", "Reconnect UI", "Lives, respawn", "CPlayer__ReceiveButtonActionState"):
        require(any(token in item for item in blockers), f"missing blocker token: {token}")
    require(len(blockers) >= 8, "blocker list too short")

    prerequisites = [str(item) for item in list_at(contract, "runtimeAttemptPrerequisites")]
    for token in ("retail Ghidra", "retail layout proof", "exact-PID CDB", "P1/P2 regression", "death/respawn/result"):
        require(any(token in item for item in prerequisites), f"missing prerequisite token: {token}")
    require(len(prerequisites) >= 8, "prerequisite list too short")

    required = [str(item) for item in list_at(contract, "requiredNewProofClassForP3P4")]
    require(len(required) >= 6, "required P3/P4 proof-class checklist too short")
    for token in ("fresh retail static map", "retail Ghidra", "exact-PID CDB", "visual or state evidence", "P1/P2 behavior", "mode proof"):
        require(any(token in item for item in required), f"required proof class missing token: {token}")

    ladder = [str(item) for item in list_at(contract, "nextProofLadder")]
    require(any("same-host session-control" in item for item in ladder), "missing same-host session-control next rung")
    require(any("second-host" in item for item in ladder), "missing second-host command-source next rung")
    require(any("retail Ghidra P3/P4" in item for item in ladder), "missing retail P3/P4 deep-dive next rung")
    require(any("copied-runtime P3/P4" in item for item in ladder), "missing copied-runtime P3/P4 eventual rung")

    non_claims = object_at(contract, "nonClaims")
    require(set(non_claims) == set(FALSE_NON_CLAIM_KEYS), "non-claim key set drifted")
    for key in FALSE_NON_CLAIM_KEYS:
        require(non_claims.get(key) is False, f"non-claim must remain false: {key}")

    require_source_tokens()
    require_cross_contracts()
    return {
        "schemaVersion": contract["schemaVersion"],
        "scope": contract["scope"],
        "mapProofClass": boundary["mapProofClass"],
        "p3p4FeasibilityScope": boundary["p3p4FeasibilityScope"],
        "newBeaLaunchCount": boundary["newBeaLaunchCount"],
        "cdbAttachCount": boundary["cdbAttachCount"],
        "ghidraMutationCount": boundary["ghidraMutationCount"],
        "maxOriginalBinaryActiveSlotsProven": boundary["maxOriginalBinaryActiveSlotsProven"],
        "nPlayerOriginalBinaryRuntimeProof": boundary["nPlayerOriginalBinaryRuntimeProof"],
        "p3p4GameplayInputRejected": boundary["p3p4GameplayInputRejected"],
        "blastRadiusRowCount": len(rows),
        "hardBlockerCount": len(blockers),
        "runtimeAttemptPrerequisiteCount": len(prerequisites),
        "requiredNewProofClassForP3P4Count": len(required),
        "beyondTwoPlayersRequiresNewProofClass": boundary["beyondTwoPlayersRequiresNewProofClass"],
        "absenceOfCurrentProofIsNotProofOfPermanentAbsence": boundary["absenceOfCurrentProofIsNotProofOfPermanentAbsence"],
        "permanentImpossibilityClaim": boundary["permanentImpossibilityClaim"],
        "claimBoundary": (
            "This is a public-safe static/source blast-radius map. It does not prove active P3/P4 original-binary "
            "gameplay, does not raise the runtime slot ceiling above P1/P2, and does not claim P3/P4 are impossible forever."
        ),
    }


def require_doc_tokens() -> None:
    token_sets = {
        READINESS: (
            "Original Binary Online P3/P4 Runtime Feasibility Map Readiness Note",
            "original-binary-online-p3p4-runtime-feasibility-map",
            "mapProofClass=static-blast-radius-map-not-runtime-proof",
            "p3p4FeasibilityScope=static-blast-radius-not-runtime-proof",
            "newBeaLaunchCount=0",
            "cdbAttachCount=0",
            "ghidraMutationCount=0",
            "maxOriginalBinaryActiveSlotsProven=2",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "P3/P4 metadata-only",
            "p3p4GameplayInputRejected=true",
            "sourceOnlyMaxPlayersIsRuntimeProof=false",
            "quadSplitBranchIsRuntimeProof=false",
            "mapCompleteForRuntimeAttempt=false",
            "safeToPatchMPlayersAbove2=false",
            "beyondTwoPlayersRequiresNewProofClass=true",
            "absenceOfCurrentProofIsNotProofOfPermanentAbsence=true",
            "permanentImpossibilityClaim=false",
            "publicMatchmakingProof=false",
            "multiHostLanProof=false",
            "nativeBeaNetcodeProof=false",
        ),
        FEASIBILITY: (
            "Original Binary Online P3/P4 Runtime Feasibility Map",
            "original-binary-online-p3p4-runtime-feasibility-map.v1.json",
            "mapProofClass=static-blast-radius-map-not-runtime-proof",
            "p3p4FeasibilityScope=static-blast-radius-not-runtime-proof",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "P3/P4 metadata-only",
            "sourceOnlyMaxPlayersIsRuntimeProof=false",
            "quadSplitBranchIsRuntimeProof=false",
            "safeToPatchMPlayersAbove2=false",
        ),
        LOCAL_CONTRACT: (
            "P3/P4 runtime feasibility map",
            "mapProofClass=static-blast-radius-map-not-runtime-proof",
            "static-blast-radius-not-runtime-proof",
            "sourceOnlyMaxPlayersIsRuntimeProof=false",
            "quadSplitBranchIsRuntimeProof=false",
            "mapCompleteForRuntimeAttempt=false",
        ),
        REGISTER: (
            "P3/P4 runtime feasibility map",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "safeToPatchMPlayersAbove2=false",
            "hardBlockersBeforeP3P4Runtime",
            "same-host session-control",
        ),
        CAPABILITIES: (
            "P3/P4 runtime feasibility map",
            "mapProofClass=static-blast-radius-map-not-runtime-proof",
            "p3p4FeasibilityScope=static-blast-radius-not-runtime-proof",
            "nPlayerOriginalBinaryRuntimeProof=0",
            "activeP3P4OriginalBinaryGameplayProof=false",
            "safeToPatchMPlayersAbove2=false",
        ),
        MAPPED_SYSTEMS: (
            "P3/P4 runtime feasibility map",
            "engine-viewpoints-two",
            "controller-assignment-p1-p2-trap",
            "lives-respawn-results-two",
            "runtimeProofStatus=unproven",
            "supportsOriginalBinaryRuntimeProof=false",
        ),
    }
    for path, tokens in token_sets.items():
        for token in tokens:
            require(token in read_text(path), f"{path} missing token: {token}")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:winui-original-binary-online-p3p4-runtime-feasibility-map") == EXPECTED_SCRIPT, "missing package P3/P4 map script")


def validate_repo_contract() -> dict[str, Any]:
    summary = validate_contract(CONTRACT)
    require_doc_tokens()
    return summary


def run_self_test() -> None:
    good = read_json(CONTRACT)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "contract.json"
        write_json(path, good)
        validate_contract(path)

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["maxOriginalBinaryActiveSlotsProven"] = 4
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("P3/P4 runtime slot overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["maxRetailPlayersProven"] = 4
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("retail player count overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["retailViewpointsProven"] = 4
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("retail viewpoint overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["nPlayerOriginalBinaryRuntimeProof"] = 1
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("N-player proof overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["sourceOnlyMaxPlayersIsRuntimeProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("MAX_PLAYERS source-only proof should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["quadSplitBranchIsRuntimeProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("quad-split source-only proof should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["acceptedOriginalBinaryGameplaySlots"] = ["P1", "P2", "P3"]
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("P3 accepted gameplay slot should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["p3p4GameplayInputRejected"] = False
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("P3/P4 gameplay acceptance should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["mapCompleteForRuntimeAttempt"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("map-complete-for-runtime overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["blastRadiusRows"][0]["supportsOriginalBinaryRuntimeProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("source-static row runtime support should fail")

        bad = json.loads(json.dumps(good))
        bad["blastRadiusRows"] = [row for row in bad["blastRadiusRows"] if row["id"] != "engine-viewpoints-two"]
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("missing engine viewpoint row should fail")

        bad = json.loads(json.dumps(good))
        bad["requiredNewProofClassForP3P4"] = bad["requiredNewProofClassForP3P4"][:2]
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("weakened P3/P4 proof-class checklist should fail")

        bad = json.loads(json.dumps(good))
        bad["nonClaims"]["publicMatchmakingProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except P3P4FeasibilityMapError:
            pass
        else:
            raise AssertionError("public matchmaking overclaim should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary P3/P4 runtime feasibility map checker self-test: PASS")
        return 0
    if not args.check:
        raise SystemExit("use --check or --self-test")
    print(json.dumps(validate_repo_contract(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except P3P4FeasibilityMapError as exc:
        print(f"WinUI original-binary P3/P4 runtime feasibility map check: FAIL: {exc}")
        raise SystemExit(2)
