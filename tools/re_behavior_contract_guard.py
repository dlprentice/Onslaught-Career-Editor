#!/usr/bin/env python3
"""Validate reviewed RE contract inputs and reject superseded active mutations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "ghidra-reviewed-correction-plan-2026-07-13.json"
CANDIDATE = ROOT / "reverse-engineering" / "binary-analysis" / "first-flight-camera-movement-morph-contract-candidate.v1.json"

OBSERVATION_ORDER = (
    "camera_reference_frame",
    "walker_directional_response",
    "jet_directional_response",
    "morph_request_result_correlation",
)
EVIDENCE_FIELDS = (
    "sourceHypothesis",
    "steamStaticCorroboration",
    "copiedRuntimeMeasurement",
    "tolerances",
    "rebuildRequirement",
    "nonclaims",
)

SUPERSEDED = {
    "0x00411630": {
        "forbiddenName": "CMonitor__IntegrateMovementAgainstTerrain",
        "acceptedName": "CBattleEngineJetPart__HandleGroundEffect",
        "forbiddenCommentTokens": (
            "CMonitor__UpdateMovementTransitionAndEffects",
            "monitor movement/terrain helper",
        ),
    },
    "0x00411aa0": {
        "forbiddenName": "CMonitor__ComputeTerrainVelocityScalar",
        "acceptedName": "CBattleEngineJetPart__GetFriction",
        "forbiddenCommentTokens": (
            "CMonitor__UpdateMovementTransitionAndEffects",
            "monitor terrain/velocity scalar helper",
        ),
    },
}

MUTATORS = (
    {
        "path": ROOT / "tools" / "ApplyMovementJetPartSignatureCorrection.java",
        "marker": "applySignature",
        "expectedMarkerCalls": 15,
        "expectedRemaining": {
            ("0x00411a60", "Vec3__Cross"),
            ("0x00411b70", "CBattleEngineJetPart__IsStateMachineActive"),
            ("0x00411e70", "CBattleEngineJetPart__ChangeWeapon"),
            ("0x00412000", "CBattleEngineJetPart__LoseWeaponCharge"),
            ("0x00412050", "CBattleEngineJetPart__WeaponFired"),
            ("0x004121b0", "CBattleEngineJetPart__GetWeaponAmmoPercentage"),
            ("0x004122b0", "CBattleEngineJetPart__IsWeaponOverheated"),
            ("0x00412310", "CBattleEngineJetPart__IsEnergyWeapon"),
            ("0x00412370", "CBattleEngineJetPart__GetWeaponCharge"),
            ("0x00412480", "CBattleEngineJetPart__GetWeaponPhysicsName"),
            ("0x004124d0", "CBattleEngineJetPart__GetCurrentWeaponNameField04"),
            ("0x00412520", "CBattleEngineJetPart__GetWeaponIconName"),
            ("0x00412570", "CBattleEngineJetPart__CanWeaponFire"),
            ("0x00412610", "CBattleEngineJetPart__GetCurrentWeapon"),
        },
    },
    {
        "path": ROOT / "tools" / "ApplyCMonitorMovementAudioAnimationRenderCurrentRiskWave1187.java",
        "marker": "new Target",
        "expectedMarkerCalls": 4,
        "expectedRemaining": {
            ("0x00409950", "CMonitor__UpdateSoundEventPlaybackForReader"),
            ("0x0044e2c0", "CMonitor__CheckSVFAnimationAndAdvanceState"),
            ("0x0047d3b0", "CMonitor__TryQueuePrefireAnimation"),
            ("0x005078f0", "CMonitor__UpdateTrackedRenderPair"),
        },
    },
)


def strip_java_comments(text: str) -> str:
    """Blank Java comments while preserving strings, characters, and line structure."""
    output: list[str] = []
    index = 0
    state = "code"
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and next_char == "/":
                output.extend((" ", " "))
                index += 2
                state = "line-comment"
                continue
            if char == "/" and next_char == "*":
                output.extend((" ", " "))
                index += 2
                state = "block-comment"
                continue
            if char == '"':
                state = "string"
            elif char == "'":
                state = "character"
            output.append(char)
        elif state == "line-comment":
            output.append("\n" if char == "\n" else " ")
            if char == "\n":
                state = "code"
        elif state == "block-comment":
            if char == "*" and next_char == "/":
                output.extend((" ", " "))
                index += 2
                state = "code"
                continue
            output.append("\n" if char == "\n" else " ")
        else:
            output.append(char)
            if char == "\\" and next_char:
                output.append(next_char)
                index += 2
                continue
            if (state == "string" and char == '"') or (state == "character" and char == "'"):
                state = "code"
        index += 1
    return "".join(output)


def extract_literal_mutation_pairs(text: str, marker: str) -> list[tuple[str, str]]:
    """Return direct literal address/name arguments for a Java mutation call."""
    text = strip_java_comments(text)
    pattern = re.compile(
        rf"{re.escape(marker)}\s*\(\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"",
        re.MULTILINE,
    )
    return pattern.findall(text)


def count_marker_calls(text: str, marker: str) -> int:
    """Count executable marker-shaped calls/declarations after comments are removed."""
    return len(re.findall(rf"\b{re.escape(marker)}\s*\(", strip_java_comments(text)))


def contains_forbidden_pair(text: str, address: str, forbidden: dict[str, object]) -> bool:
    """Fail closed when an active helper contains a stale address and stale metadata."""
    text = strip_java_comments(text)
    if address not in text:
        return False
    tokens = (forbidden["forbiddenName"], *forbidden["forbiddenCommentTokens"])
    return any(str(token) in text for token in tokens)


def build_report() -> dict[str, object]:
    failures: list[str] = []
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    authority: dict[str, object] = {}

    for address, expected in SUPERSEDED.items():
        matching = [record for record in plan.get("records", []) if record.get("address") == address]
        if len(matching) != 1:
            failures.append(f"{address}: expected one authoritative correction record, found {len(matching)}")
            continue
        record = matching[0]
        checks = {
            "classification": record.get("classification") == "confirmed-apply",
            "forbiddenName": record.get("currentName") == expected["forbiddenName"],
            "acceptedName": record.get("correctedName") == expected["acceptedName"],
            "nameCorrected": "name" in record.get("correctedFields", []),
            "commentCorrected": "comment" in record.get("correctedFields", []),
            "signatureNamesAcceptedOwner": expected["acceptedName"] in record.get("correctedSignature", ""),
            "correctedCommentRejectsStaleOwner": expected["forbiddenName"]
            not in record.get("correctedComment", ""),
            "correctedCommentRejectsStaleTokens": all(
                token not in record.get("correctedComment", "")
                for token in expected["forbiddenCommentTokens"]
            ),
            "correctedCommentNamesAcceptedOwner": expected["acceptedName"].replace("__", "::")
            in record.get("correctedComment", ""),
        }
        authority[address] = checks
        for check, passed in checks.items():
            if not passed:
                failures.append(f"{address}: authoritative {check} check failed")

    mutator_results: list[dict[str, object]] = []
    for mutator in MUTATORS:
        path = mutator["path"]
        text = path.read_text(encoding="utf-8")
        forbidden_hits: list[str] = []
        for address, forbidden in SUPERSEDED.items():
            if contains_forbidden_pair(text, address, forbidden):
                forbidden_hits.append(address)
        actual_remaining = set(extract_literal_mutation_pairs(text, str(mutator["marker"])))
        expected_remaining = set(mutator["expectedRemaining"])
        marker_calls = count_marker_calls(text, str(mutator["marker"]))
        missing_unrelated = sorted(expected_remaining - actual_remaining)
        unexpected_operations = sorted(actual_remaining - expected_remaining)
        if forbidden_hits:
            failures.append(f"{path.name}: superseded record tokens remain: {forbidden_hits}")
        if missing_unrelated:
            failures.append(f"{path.name}: expected unrelated operations missing: {missing_unrelated}")
        if unexpected_operations:
            failures.append(f"{path.name}: unexpected literal mutation operations: {unexpected_operations}")
        if marker_calls != mutator["expectedMarkerCalls"]:
            failures.append(
                f"{path.name}: expected {mutator['expectedMarkerCalls']} marker calls/declarations, found {marker_calls}"
            )
        mutator_results.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "forbiddenHits": forbidden_hits,
                "expectedRemaining": [list(pair) for pair in sorted(expected_remaining)],
                "missingUnrelated": missing_unrelated,
                "unexpectedOperations": unexpected_operations,
                "expectedMarkerCalls": mutator["expectedMarkerCalls"],
                "markerCalls": marker_calls,
            }
        )

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    candidate_checks = {
        "schemaVersion": candidate.get("schemaVersion")
        == "first-flight-camera-movement-morph-contract-candidate.v1",
        "status": candidate.get("status") == "candidate-static-runtime-required",
        "rebuildChangeBlocked": candidate.get("rebuildChangeAuthorized") is False,
        "retry13Blocked": candidate.get("retry13Authorized") is False,
        "provenancePresent": bool(candidate.get("provenance")),
        "evidenceAuthorityPresent": bool(candidate.get("evidenceAuthority")),
        "globalNonclaimsPresent": bool(candidate.get("globalNonclaims")),
        "observationOrder": tuple(candidate.get("observationOrder", ())) == OBSERVATION_ORDER,
    }
    observations = candidate.get("observations", [])
    candidate_checks["observationRowsOrdered"] = tuple(
        row.get("id") for row in observations
    ) == OBSERVATION_ORDER
    for row in observations:
        row_id = row.get("id", "<missing-id>")
        candidate_checks[f"{row_id}:evidenceFields"] = all(bool(row.get(field)) for field in EVIDENCE_FIELDS)
        candidate_checks[f"{row_id}:runtimeRequired"] = (
            row.get("copiedRuntimeMeasurement", {}).get("status") == "required-not-measured"
        )
        candidate_checks[f"{row_id}:tolerancesOpen"] = (
            row.get("tolerances", {}).get("status") == "not-established"
        )
        candidate_checks[f"{row_id}:rebuildBlocked"] = (
            row.get("rebuildRequirement", {}).get("status") == "blocked-until-runtime-accepted"
        )
    for check, passed in candidate_checks.items():
        if not passed:
            failures.append(f"candidate: {check} check failed")

    return {
        "schemaVersion": "re-behavior-contract-guard.v1",
        "status": "PASS" if not failures else "FAIL",
        "authoritativeCorrectionPlan": PLAN.relative_to(ROOT).as_posix(),
        "authority": authority,
        "candidateContract": {
            "path": CANDIDATE.relative_to(ROOT).as_posix(),
            "checks": candidate_checks,
        },
        "mutators": mutator_results,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return nonzero when the guard fails.")
    args = parser.parse_args()

    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
