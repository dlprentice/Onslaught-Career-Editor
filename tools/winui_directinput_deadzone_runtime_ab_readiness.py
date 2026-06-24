#!/usr/bin/env python3
"""Validate the DirectInput deadzone runtime A/B readiness gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "roadmap" / "original-binary-directinput-deadzone-runtime-ab-readiness.v1.json"
CONTRACT_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-directinput-deadzone-runtime-ab-readiness.v1.json"
CANDIDATE_MAP = ROOT / "roadmap" / "original-binary-control-feel-candidate-map.v1.json"
READINESS = ROOT / "release" / "readiness" / "winui_directinput_deadzone_runtime_ab_readiness_2026-06-23.md"
BYTE_EXPORT_READINESS = ROOT / "release" / "readiness" / "winui_directinput_deadzone_byte_export_2026-06-19.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
PACKAGE_JSON = ROOT / "package.json"
PATCH_CATALOG = ROOT / "patches" / "catalog" / "patches.v2.json"

SCHEMA = "winui-directinput-deadzone-runtime-ab-readiness.v1"
GAMEPAD_SCHEMA = "winui-safe-copy-local-multiplayer-gamepad-readiness.v1"
EXPECTED_SCRIPT = (
    r"py -3 tools\winui_directinput_deadzone_runtime_ab_readiness_test.py && "
    r"py -3 tools\winui_directinput_deadzone_runtime_ab_readiness.py --self-test && "
    r"py -3 tools\winui_directinput_deadzone_runtime_ab_readiness.py --check"
)
FALSE_CLAIMS = (
    "addsPatchRow",
    "visiblePatchRowAdded",
    "runtimeAbProof",
    "runtimeProof",
    "improvedControlFeelProof",
    "physicalGamepadProof",
    "directInputRuntimeProof",
    "copiedExecutablePatchProof",
    "wallClockLatencyProof",
    "trueOnlineMultiplayerProof",
    "activeP3P4OriginalBinaryGameplayProof",
    "rebuildParityProof",
    "noNoticeableDifferenceProof",
    "installedGameMutation",
    "originalExecutableMutation",
)
REQUIRED_PROOF_REQUIREMENTS = (
    "copied-executable A/B byte verification under app-owned proof root",
    "restore verification before and after any attempted alternate immediate",
    "physical gamepad or equivalent DirectInput runtime device present on the host",
    "exact managed copied BEA PID and CDB attachment",
    "zero keyboard SendInput/keybd_event/PostMessage positive-stimulus counters for the DirectInput stimulus window",
    "no-input negative control",
    "per-configuration regression across controller configs 1-4",
)


class DeadzoneRuntimeAbReadinessError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DeadzoneRuntimeAbReadinessError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise DeadzoneRuntimeAbReadinessError(f"invalid JSON: {path}: {exc}") from exc
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def validate_contract_payload(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == SCHEMA, "schema mismatch")
    require(payload.get("scope") == "directinput-deadzone-runtime-a-b-readiness-not-runtime-proof", "scope mismatch")

    candidate = payload.get("candidate")
    require(isinstance(candidate, dict), "missing candidate")
    require(candidate.get("id") == "platform_input_directinput_deadzone_0x96", "candidate id mismatch")
    require(candidate.get("functionVa") == "0x00513120", "function VA mismatch")
    require(candidate.get("instructionVa") == "0x00513167", "instruction VA mismatch")
    require(candidate.get("instructionFileOffset") == "0x113167", "instruction file offset mismatch")
    require(candidate.get("immediateVa") == "0x0051316D", "immediate VA mismatch")
    require(candidate.get("immediateFileOffset") == "0x11316D", "immediate file offset mismatch")
    require(candidate.get("baselineImmediateValue") == "0x96", "baseline immediate mismatch")
    require(candidate.get("baselineInstructionBytes") == "C7 85 E0 30 03 00 96 00 00 00", "instruction bytes mismatch")
    require(candidate.get("byteExportProof") == "winui-directinput-deadzone-byte-export.v1", "byte-export proof mismatch")

    readiness = payload.get("currentReadiness")
    require(isinstance(readiness, dict), "missing currentReadiness")
    require(readiness.get("status") == "blocked_no_present_gamepad", "current readiness must stay blocked without hardware")
    require(readiness.get("presentGamepadCandidateCount") == 0, "present gamepad count must be zero for this readiness contract")
    require(readiness.get("registryGamepadCandidateCount") == 0, "registry gamepad count must be zero for this readiness contract")
    require(readiness.get("hardwarePresenceIsOnlyPrecondition") is True, "hardware precondition boundary missing")

    requirements = payload.get("requiredBeforeAnyPatchRow")
    require(isinstance(requirements, list), "missing requiredBeforeAnyPatchRow")
    requirement_text = "\n".join(str(item) for item in requirements)
    for token in REQUIRED_PROOF_REQUIREMENTS:
        require(token in requirement_text, f"missing proof requirement: {token}")

    plan = payload.get("proofPlan")
    require(isinstance(plan, list), "missing proofPlan")
    plan_ids = [row.get("id") for row in plan if isinstance(row, dict)]
    require(plan_ids == ["baseline-a", "candidate-b", "restore"], "proofPlan ids mismatch")

    claims = payload.get("claimBooleans")
    require(isinstance(claims, dict), "missing claimBooleans")
    for key in FALSE_CLAIMS:
        require(claims.get(key) is False, f"claim must be false: {key}")

    non_claims = payload.get("nonClaims")
    require(isinstance(non_claims, list), "missing nonClaims")
    non_claim_text = "\n".join(str(item).lower() for item in non_claims)
    for token in (
        "not a patch bench row",
        "not a player-facing deadzone option",
        "not runtime directinput proof",
        "not physical gamepad proof",
        "not improved control-feel proof",
        "not online multiplayer proof",
    ):
        require(token in non_claim_text, f"missing non-claim: {token}")

    boundary = str(payload.get("claimBoundary", "")).lower()
    for token in ("blocked by no present gamepad", "patch-row", "runtime", "improved-feel", "online"):
        require(token in boundary, f"claim boundary missing token: {token}")

    return {
        "schema": payload["schema"],
        "status": readiness["status"],
        "presentGamepadCandidateCount": readiness["presentGamepadCandidateCount"],
        "registryGamepadCandidateCount": readiness["registryGamepadCandidateCount"],
        "addsPatchRow": claims["addsPatchRow"],
        "runtimeAbProof": claims["runtimeAbProof"],
        "physicalGamepadProof": claims["physicalGamepadProof"],
        "improvedControlFeelProof": claims["improvedControlFeelProof"],
    }


def validate_gamepad_artifact(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    require(payload.get("schemaVersion") == GAMEPAD_SCHEMA, "gamepad artifact schema mismatch")
    require(payload.get("status") in {"blocked_no_present_gamepad", "ready_for_physical_gamepad_runtime_attempt"}, "unexpected gamepad status")
    require(isinstance(payload.get("presentGamepadCandidateCount"), int), "missing presentGamepadCandidateCount")
    require(isinstance(payload.get("registryGamepadCandidateCount"), int), "missing registryGamepadCandidateCount")
    require(payload.get("physicalGamepadRuntimeProofReady") is not True, "readiness artifact must not be treated as runtime proof")
    require("precondition" in str(payload.get("claimBoundary", "")).lower(), "gamepad claim boundary missing precondition wording")
    return {
        "schemaVersion": payload["schemaVersion"],
        "status": payload["status"],
        "presentGamepadCandidateCount": payload["presentGamepadCandidateCount"],
        "registryGamepadCandidateCount": payload["registryGamepadCandidateCount"],
        "physicalGamepadRuntimeProofReady": payload["physicalGamepadRuntimeProofReady"],
    }


def validate_repository() -> dict[str, Any]:
    summary = validate_contract_payload(read_json(CONTRACT))
    require(read_text(CONTRACT) == read_text(CONTRACT_MIRROR), "contract lore mirror mismatch")

    candidate = read_json(CANDIDATE_MAP)
    require(candidate.get("recommendedNextRung", {}).get("id") == "directinput-deadzone-runtime-a-b-proof", "candidate map next rung mismatch")
    require(candidate.get("recommendedNextRung", {}).get("addsPatchRow") is False, "candidate map next rung must not add patch row")

    readiness = read_text(READINESS)
    for token in (
        "DirectInput Deadzone Runtime A/B Readiness Note",
        "blocked_no_present_gamepad",
        "0x00513167",
        "0x113167",
        "0x0051316D",
        "0x11316D",
        "runtimeAbProof=false",
        "physicalGamepadProof=false",
        "directInputRuntimeProof=false",
        "improvedControlFeelProof=false",
        "not a player-facing deadzone option",
    ):
        require(token in readiness, f"readiness note missing token: {token}")

    byte_export = read_text(BYTE_EXPORT_READINESS)
    require("static clean-specimen byte export complete; runtime blocked" in byte_export, "byte-export readiness boundary changed unexpectedly")

    register = read_text(REGISTER)
    for token in (
        "DirectInput deadzone runtime A/B readiness",
        "blocked_no_present_gamepad",
        "0 runtime-proven control-feel byte rows",
        "no player-facing deadzone patch row",
    ):
        require(token in register, f"register missing token: {token}")
    require(read_text(REGISTER) == read_text(REGISTER_MIRROR), "register lore mirror mismatch")

    scripts = read_json(PACKAGE_JSON).get("scripts")
    require(isinstance(scripts, dict), "package scripts missing")
    require(scripts.get("test:winui-directinput-deadzone-runtime-ab-readiness") == EXPECTED_SCRIPT, "package script mismatch")
    aggregate = scripts.get("test:winui-copied-profile-runtime", "")
    require("test:winui-directinput-deadzone-runtime-ab-readiness" in aggregate, "aggregate runtime script missing deadzone runtime A/B readiness")

    catalog = read_json(PATCH_CATALOG).get("patches")
    require(isinstance(catalog, list), "patch catalog missing patch rows")
    matches = []
    for row in catalog:
        if not isinstance(row, dict):
            continue
        blob = json.dumps(row, sort_keys=True).lower()
        if "deadzone" in blob or "platforminput" in blob:
            matches.append(row.get("id", "<missing-id>"))
    require(not matches, f"patch catalog must not contain deadzone/PlatformInput rows yet: {matches}")
    return summary


def run_self_test() -> None:
    payload = {
        "schema": SCHEMA,
        "scope": "directinput-deadzone-runtime-a-b-readiness-not-runtime-proof",
        "candidate": {
            "id": "platform_input_directinput_deadzone_0x96",
            "functionVa": "0x00513120",
            "instructionVa": "0x00513167",
            "instructionFileOffset": "0x113167",
            "immediateVa": "0x0051316D",
            "immediateFileOffset": "0x11316D",
            "baselineImmediateValue": "0x96",
            "baselineInstructionBytes": "C7 85 E0 30 03 00 96 00 00 00",
            "byteExportProof": "winui-directinput-deadzone-byte-export.v1",
        },
        "currentReadiness": {
            "status": "blocked_no_present_gamepad",
            "presentGamepadCandidateCount": 0,
            "registryGamepadCandidateCount": 0,
            "hardwarePresenceIsOnlyPrecondition": True,
        },
        "requiredBeforeAnyPatchRow": list(REQUIRED_PROOF_REQUIREMENTS),
        "proofPlan": [{"id": "baseline-a"}, {"id": "candidate-b"}, {"id": "restore"}],
        "claimBooleans": {key: False for key in FALSE_CLAIMS},
        "nonClaims": [
            "not a Patch Bench row",
            "not a player-facing deadzone option",
            "not runtime DirectInput proof",
            "not physical gamepad proof",
            "not improved control-feel proof",
            "not online multiplayer proof",
        ],
        "claimBoundary": "blocked by no present gamepad; patch-row, runtime, improved-feel, and online claims stay false",
    }
    validate_contract_payload(payload)

    bad = json.loads(json.dumps(payload))
    bad["claimBooleans"]["runtimeAbProof"] = True
    try:
        validate_contract_payload(bad)
    except DeadzoneRuntimeAbReadinessError:
        pass
    else:
        raise DeadzoneRuntimeAbReadinessError("self-test expected runtimeAbProof=true to fail")

    bad = json.loads(json.dumps(payload))
    bad["currentReadiness"]["status"] = "ready_for_physical_gamepad_runtime_attempt"
    bad["currentReadiness"]["presentGamepadCandidateCount"] = 1
    try:
        validate_contract_payload(bad)
    except DeadzoneRuntimeAbReadinessError:
        pass
    else:
        raise DeadzoneRuntimeAbReadinessError("self-test expected ready hardware to require a new contract")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--gamepad-artifact", type=Path)
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print("WinUI DirectInput deadzone runtime A/B readiness self-test: PASS")
            return 0
        if args.check:
            print(json.dumps(validate_repository(), indent=2, sort_keys=True))
            return 0
        if args.gamepad_artifact:
            print(json.dumps(validate_gamepad_artifact(args.gamepad_artifact), indent=2, sort_keys=True))
            return 0
        raise DeadzoneRuntimeAbReadinessError("--self-test, --check, or --gamepad-artifact is required")
    except DeadzoneRuntimeAbReadinessError as exc:
        print(f"WinUI DirectInput deadzone runtime A/B readiness check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
