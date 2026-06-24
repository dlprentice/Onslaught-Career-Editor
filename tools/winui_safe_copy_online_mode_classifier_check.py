#!/usr/bin/env python3
"""Validate the original-binary online mode classifier contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-online-mode-classifier.v1.json"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
N_SLOT_SCHEMA = ROOT / "roadmap" / "original-binary-online-n-slot-session-schema.v1.json"
P3P4_MAP = ROOT / "roadmap" / "original-binary-online-p3p4-runtime-feasibility-map.v1.json"
READINESS = ROOT / "release" / "readiness" / "original_binary_online_mode_classifier_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
PACKAGE_JSON = ROOT / "package.json"
SOURCE_GAME_CPP = ROOT / "references" / "Onslaught" / "game.cpp"
SOURCE_GAME_H = ROOT / "references" / "Onslaught" / "game.h"
SOURCE_ENGINE_H = ROOT / "references" / "Onslaught" / "engine.h"

EXPECTED_SCHEMA = "winui-original-binary-online-mode-classifier.v1"
EXPECTED_SCOPE = "original-binary-online-mode-classifier"
EXPECTED_STATUS = (
    "complete public-safe online mode classifier; no runtime co-op, versus, team-versus, spectator-admin, "
    "second-host LAN, public matchmaking, native BEA netcode, or P3/P4 gameplay proof"
)
EXPECTED_SCRIPT = (
    r"py -3 tools\winui_safe_copy_online_mode_classifier_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_mode_classifier_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_mode_classifier_check.py --check"
)
EXPECTED_MODE_IDS = {"cooperative", "versus-free-for-all", "team-versus", "spectator-admin"}
EXPECTED_RULE_IDS = {
    "local-splitscreen-is-not-coop-or-versus",
    "session-type-is-not-runtime-mode-proof",
    "team-assignment-schema-is-not-team-runtime-proof",
    "spectator-admin-metadata-is-not-runtime-admin-proof",
    "p3p4-metadata-is-not-p3p4-gameplay",
}
FALSE_BOUNDARY_KEYS = (
    "gameInputSentByModeClassifier",
    "publicNetworkSocketsOpened",
    "publicBind",
    "baseOnlineMultiplayerReady",
    "sameHostRuntimeProofCreatedByClassifier",
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
    "newBeaLaunchCount",
    "cdbAttachCount",
    "ghidraMutationCount",
    "coOpVersusModeRuntimeProofSlices",
    "modeRuntimeProofSlices",
    "nPlayerOriginalBinaryRuntimeProof",
)
FALSE_NON_CLAIM_KEYS = (
    "baseOnlineMultiplayerReady",
    "coOpModeRuntimeProof",
    "versusModeRuntimeProof",
    "teamVersusRuntimeProof",
    "spectatorAdminRuntimeProof",
    "multiHostLanProof",
    "secondPhysicalHostProof",
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


class ModeClassifierError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ModeClassifierError(message)


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
            "(mPlayers==3) || (mPlayers==4)",
            "3/4 player quad split",
            "mPlayer1Lives",
            "mPlayer2Lives",
            "CGame::IsMultiplayer()",
            "mCurrentlyRunningLevel >849 && mCurrentlyRunningLevel < 900",
        ),
    )
    require_tokens(SOURCE_GAME_H, ("#define MAX_PLAYERS 4", "mPlayer[ MAX_PLAYERS ]"))
    require_tokens(SOURCE_ENGINE_H, ("#define VIEWPOINTS", "mCamera[VIEWPOINTS]", "mPlayer[VIEWPOINTS]"))


def require_cross_contracts() -> None:
    scalability = read_json(SCALABILITY)
    runtime = object_at(scalability, "currentOriginalBinaryRuntime")
    require(runtime.get("modeRuntimeClassification") == "unclassified-local-multiplayer", "scalability runtime mode classification drifted")
    require(runtime.get("coOpVersusModeRuntimeProofSlices") == 0, "scalability co-op/versus proof count must stay zero")
    architecture = object_at(scalability, "scalableArchitecture")
    policy = object_at(architecture, "modeClassifierPolicy")
    require(policy.get("proofSchema") == EXPECTED_SCHEMA, "scalability mode-classifier schema mismatch")
    require(policy.get("proofClass") == "static-source-session-taxonomy-not-runtime-mode-proof", "scalability mode-classifier proof class mismatch")
    require(policy.get("modeClassifierScope") == "original-binary-online-mode-classifier-not-runtime-mode-proof", "scalability mode-classifier scope mismatch")
    require(policy.get("modeClassifierProven") is True, "scalability mode-classifier flag missing")
    require(policy.get("currentRuntimeModeClassification") == "unclassified-local-multiplayer", "scalability classifier mode mismatch")
    require(policy.get("modeRuntimeProofSlices") == 0, "scalability classifier runtime proof count must stay zero")
    require(policy.get("coOpVersusModeRuntimeProofSlices") == 0, "scalability classifier co-op/versus proof count must stay zero")
    require(policy.get("teamAssignmentAuthority") == "schema-only-not-runtime-proof", "scalability team assignment boundary mismatch")
    for key in (
        "coOpModeRuntimeProof",
        "versusModeRuntimeProof",
        "teamVersusRuntimeProof",
        "spectatorAdminRuntimeProof",
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "activeP3P4OriginalBinaryGameplayProof",
    ):
        require(policy.get(key) is False, f"scalability mode-classifier overclaim must remain false: {key}")
    require(policy.get("modeFamiliesClassified") == ["cooperative", "versus-free-for-all", "team-versus", "spectator-admin"], "scalability classified mode family list mismatch")

    schema = read_json(N_SLOT_SCHEMA)
    for row in list_at(schema, "modeProfiles"):
        require(isinstance(row, dict), "N-slot mode-family row must be an object")
        require(row.get("runtimeProofStatus") == "planned-not-runtime-proven", f"N-slot mode row overclaims runtime proof: {row.get('modeFamily')}")
        require(row.get("modeRuntimeProofSlices") == 0, f"N-slot mode row runtime proof count drifted: {row.get('modeFamily')}")
        require(row.get("teamAssignmentAuthority") == "schema-only", f"N-slot mode row team authority drifted: {row.get('modeFamily')}")
        require(row.get("friendlyFireStatus") == "unproven", f"N-slot mode row friendly-fire overclaim: {row.get('modeFamily')}")

    p3p4 = read_json(P3P4_MAP)
    boundary = object_at(p3p4, "proofBoundary")
    require(boundary.get("safeToPatchMPlayersAbove2") is False, "P3/P4 map safe-to-patch overclaim")
    require(boundary.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 map active gameplay overclaim")


def validate_contract(path: Path = CONTRACT) -> dict[str, Any]:
    contract = read_json(path)
    require(contract.get("schemaVersion") == EXPECTED_SCHEMA, "schema mismatch")
    require(contract.get("scope") == EXPECTED_SCOPE, "scope mismatch")
    require(contract.get("status") == EXPECTED_STATUS, "status boundary drifted")

    boundary = object_at(contract, "proofBoundary")
    require(boundary.get("proofClass") == "static-source-session-taxonomy-not-runtime-mode-proof", "proof class mismatch")
    require(boundary.get("modeClassifierScope") == "original-binary-online-mode-classifier-not-runtime-mode-proof", "classifier scope mismatch")
    require(boundary.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted gameplay slots must stay P1/P2")
    require(boundary.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots must stay P3/P4")
    require(boundary.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected gameplay slots must stay P3/P4")
    for key in ZERO_BOUNDARY_KEYS:
        require(boundary.get(key) == 0, f"boundary zero counter drifted: {key}")
    for key in FALSE_BOUNDARY_KEYS:
        require(boundary.get(key) is False, f"boundary overclaim must remain false: {key}")

    anchors = object_at(contract, "sourceStaticAnchors")
    require("original-binary-copied-local-splitscreen" in str(anchors.get("runtimeProfile")), "runtime profile anchor missing")
    require(">849 and <900" in str(anchors.get("levelMultiplayerGate")), "level gate anchor missing")
    require("mPlayers=2" in str(anchors.get("currentPlayerCountGate")), "mPlayers=2 anchor missing")
    require("MAX_PLAYERS 4" in str(anchors.get("sourceCapacityDeclaration")), "MAX_PLAYERS anchor missing")
    require("I don't support more than 2 players" in str(anchors.get("controllerAssignmentTrap")), "controller trap anchor missing")
    require("VIEWPOINTS 2" in str(anchors.get("engineViewpointCeiling")), "VIEWPOINTS anchor missing")
    require("source-only branch presence is not runtime proof" in str(anchors.get("latentQuadSplitBranch")), "quad-split non-proof boundary missing")

    current = object_at(contract, "currentRuntimeModeClassification")
    require(current.get("runtimeProfile") == "original-binary-copied-local-splitscreen", "current runtime profile mismatch")
    require(current.get("modeClass") == "unclassified-local-multiplayer", "current runtime must stay unclassified local multiplayer")
    require(current.get("classificationStatus") == "runtime-observed-local-splitscreen-not-co-op-or-versus-proof", "classification status mismatch")
    require(current.get("runtimeModeProofSlices") == 0, "current mode runtime proof count must stay zero")
    for key in ("cooperativeRuntimeProof", "versusRuntimeProof", "teamVersusRuntimeProof", "spectatorAdminRuntimeProof"):
        require(current.get(key) is False, f"current mode overclaim must remain false: {key}")
    require("do not establish objective sharing" in str(current.get("reason")), "classification reason must preserve semantic gap")

    rows = list_at(contract, "plannedModeFamilies")
    mode_ids = {str(row.get("id")) for row in rows if isinstance(row, dict)}
    require(mode_ids == EXPECTED_MODE_IDS, f"mode family id mismatch: {sorted(mode_ids)}")
    for row in rows:
        require(isinstance(row, dict), "planned mode-family row must be an object")
        require(row.get("classificationStatus") == "schema-planned-not-runtime-proven", f"mode family overclaim: {row.get('id')}")
        require(row.get("runtimeProof") is False, f"mode family runtime proof overclaim: {row.get('id')}")
        evidence = [str(item) for item in list_at(row, "requiredRuntimeEvidence")]
        require(len(evidence) >= 5, f"mode family runtime evidence list too short: {row.get('id')}")
    team = next(row for row in rows if row["id"] == "team-versus")
    require(team.get("teamAssignmentAuthority") == "schema-only-not-runtime-proof", "team-versus team authority must stay schema-only")
    spectator = next(row for row in rows if row["id"] == "spectator-admin")
    require(spectator.get("adminAuthority") == "metadata-only-not-runtime-proof", "spectator/admin authority must stay metadata-only")

    rule_ids = {str(row.get("id")) for row in list_at(contract, "classifierRules") if isinstance(row, dict)}
    require(rule_ids == EXPECTED_RULE_IDS, f"classifier rule id mismatch: {sorted(rule_ids)}")
    rejection_text = "\n".join(str(item) for item in list_at(contract, "rejectionCases"))
    for token in (
        "sessionType alone",
        "modeFamily alone",
        "schema-only teamAssignments",
        "metadata-only query rows",
        "slotCapacity=4",
        "same-host, same-workstation, WSL2, or private-interface-only artifacts",
        "local session-directory smoke",
        "host-authority wrapper/protocol scaffolding",
        "joined-session same-host proofs",
    ):
        require(token in rejection_text, f"missing rejection token: {token}")

    ladder = [str(item) for item in list_at(contract, "nextProofLadder")]
    for token in ("second-physical-host", "objective/win/death/respawn", "team/friendly-fire", "spectator/admin", "P3/P4"):
        require(any(token in item for item in ladder), f"missing next-proof ladder token: {token}")

    non_claims = object_at(contract, "nonClaims")
    require(set(non_claims) == set(FALSE_NON_CLAIM_KEYS), "non-claim key set drifted")
    for key in FALSE_NON_CLAIM_KEYS:
        require(non_claims.get(key) is False, f"non-claim must remain false: {key}")

    require_source_tokens()
    if path == CONTRACT:
        require_cross_contracts()
    return {
        "schemaVersion": contract["schemaVersion"],
        "scope": contract["scope"],
        "proofClass": boundary["proofClass"],
        "modeClassifierScope": boundary["modeClassifierScope"],
        "currentRuntimeModeClassification": current["modeClass"],
        "modeFamiliesClassified": sorted(mode_ids),
        "modeRuntimeProofSlices": boundary["modeRuntimeProofSlices"],
        "coOpVersusModeRuntimeProofSlices": boundary["coOpVersusModeRuntimeProofSlices"],
        "newBeaLaunchCount": boundary["newBeaLaunchCount"],
        "cdbAttachCount": boundary["cdbAttachCount"],
        "nPlayerOriginalBinaryRuntimeProof": boundary["nPlayerOriginalBinaryRuntimeProof"],
        "activeP3P4OriginalBinaryGameplayProof": boundary["activeP3P4OriginalBinaryGameplayProof"],
        "claimBoundary": (
            "This is a public-safe online mode classifier and taxonomy guard. It does not prove co-op, versus, "
            "team-versus, spectator/admin, second-host LAN, public matchmaking, native BEA netcode, or P3/P4 gameplay."
        ),
    }


def require_doc_tokens() -> None:
    token_sets = {
        READINESS: (
            "Original Binary Online Mode Classifier Readiness Note",
            "original-binary-online-mode-classifier",
            "winui-original-binary-online-mode-classifier.v1",
            "static-source-session-taxonomy-not-runtime-mode-proof",
            "original-binary-online-mode-classifier-not-runtime-mode-proof",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "runtime-observed-local-splitscreen-not-co-op-or-versus-proof",
            "coOpVersusModeRuntimeProofSlices=0",
            "modeRuntimeProofSlices=0",
            "coOpModeRuntimeProof=false",
            "versusModeRuntimeProof=false",
            "teamVersusRuntimeProof=false",
            "spectatorAdminRuntimeProof=false",
            "sessionType alone",
            "modeFamily alone",
            "schema-only teamAssignments",
            "slotCapacity=4",
            "no BEA launch",
        ),
        FEASIBILITY: (
            "Original Binary Online Mode Classifier",
            "original-binary-online-mode-classifier.v1.json",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "runtime-observed-local-splitscreen-not-co-op-or-versus-proof",
            "modeRuntimeProofSlices=0",
            "coOpVersusModeRuntimeProofSlices=0",
            "cooperative",
            "versus-free-for-all",
            "team-versus",
            "spectator-admin",
            "sessionType alone",
            "modeFamily alone",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
        ),
        LOCAL_CONTRACT: (
            "Online mode classifier",
            "1 public-safe online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "modeRuntimeProofSlices=0",
            "coOpVersusModeRuntimeProofSlices=0",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
            "spectatorAdminRuntimeProof=false",
        ),
        REGISTER: (
            "online mode classifier",
            "1 online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "runtime-observed-local-splitscreen-not-co-op-or-versus-proof",
            "teamAssignmentAuthority=schema-only-not-runtime-proof",
            "sessionType alone",
            "modeFamily alone",
        ),
        CAPABILITIES: (
            "online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "modeRuntimeProofSlices=0",
            "coOpVersusModeRuntimeProofSlices=0",
            "coOpModeRuntimeProof=false",
            "versusModeRuntimeProof=false",
            "teamVersusRuntimeProof=false",
            "spectatorAdminRuntimeProof=false",
        ),
        MAPPED_SYSTEMS: (
            "online mode classifier",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "static-source-session-taxonomy-not-runtime-mode-proof",
            "schema-planned-not-runtime-proven",
            "sessionType-is-not-runtime-mode-proof",
        ),
    }
    for path, tokens in token_sets.items():
        for token in tokens:
            require(token in read_text(path), f"{path} missing token: {token}")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:winui-original-binary-online-mode-classifier") == EXPECTED_SCRIPT, "missing package mode-classifier script")
    require("npm run test:winui-original-binary-online-mode-classifier" in scripts.get("test:winui-copied-profile-runtime", ""), "runtime aggregate missing mode-classifier script")


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
        bad["currentRuntimeModeClassification"]["modeClass"] = "cooperative"
        write_json(path, bad)
        try:
            validate_contract(path)
        except ModeClassifierError:
            pass
        else:
            raise AssertionError("local split-screen cooperative overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["coOpModeRuntimeProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except ModeClassifierError:
            pass
        else:
            raise AssertionError("co-op runtime overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["modeRuntimeProofSlices"] = 1
        write_json(path, bad)
        try:
            validate_contract(path)
        except ModeClassifierError:
            pass
        else:
            raise AssertionError("mode runtime proof count overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["plannedModeFamilies"][2]["teamAssignmentAuthority"] = "runtime-proven"
        write_json(path, bad)
        try:
            validate_contract(path)
        except ModeClassifierError:
            pass
        else:
            raise AssertionError("team assignment runtime overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["acceptedOriginalBinaryGameplaySlots"] = ["P1", "P2", "P3"]
        write_json(path, bad)
        try:
            validate_contract(path)
        except ModeClassifierError:
            pass
        else:
            raise AssertionError("P3 gameplay overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["proofBoundary"]["secondPhysicalHostProof"] = True
        write_json(path, bad)
        try:
            validate_contract(path)
        except ModeClassifierError:
            pass
        else:
            raise AssertionError("second-host overclaim should fail")

        bad = json.loads(json.dumps(good))
        bad["classifierRules"] = bad["classifierRules"][:2]
        write_json(path, bad)
        try:
            validate_contract(path)
        except ModeClassifierError:
            pass
        else:
            raise AssertionError("missing classifier rules should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary online mode classifier checker self-test: PASS")
        return 0
    if not args.check:
        raise SystemExit("use --check or --self-test")
    print(json.dumps(validate_repo_contract(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ModeClassifierError as exc:
        print(f"WinUI original-binary online mode classifier check: FAIL: {exc}")
        raise SystemExit(2)
