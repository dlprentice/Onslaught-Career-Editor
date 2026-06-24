#!/usr/bin/env python3
"""Validate the original-binary control-feel candidate map."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "roadmap" / "original-binary-control-feel-candidate-map.v1.json"
EXPECTED_SCHEMA = "original-binary-control-feel-candidate-map.v1"
REQUIRED_CANDIDATES = {
    "copied_defaultoptions_mouse_sensitivity": "already_materialized_options_edit",
    "copied_defaultoptions_controller_config": "already_materialized_options_edit",
    "platform_input_directinput_deadzone_0x96": "file_backed_static_candidate_runtime_blocked",
    "controller_mapping_engine": "needs_runtime_trace",
    "mouse_look_angle_update": "needs_runtime_trace",
    "player_receive_button_action_observer": "observer_only",
}
BOUNDARY_FALSE_FIELDS = (
    "visiblePatchRowAdded",
    "improvedControlFeelProof",
    "physicalGamepadProof",
    "wallClockLatencyProof",
)
REQUIRED_RISK_LEVELS = ("highest", "high", "medium-high", "lower")
REQUIRED_BOUNDARY_TOKENS = (
    "adds no visible patch row",
    "performs no runtime proof",
    "does not mutate the installed game or original BEA.exe",
    "does not prove improved control feel",
    "physical gamepad",
    "wall-clock",
    "true online multiplayer",
    "active P3/P4 original-binary gameplay",
    "rebuild parity",
    "no-noticeable-difference parity",
)


class CandidateMapError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateMapError(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CandidateMapError(f"missing candidate map: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CandidateMapError(f"invalid JSON in {path}: {exc}") from exc
    require(isinstance(payload, dict), "candidate map root must be an object")
    return payload


def require_string(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str) and child, f"missing string field: {key}")
    return child


def require_list(value: Any, key: str) -> list[Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, list), f"missing list field: {key}")
    return child


def validate_candidate(row: dict[str, Any], expected_classification: str) -> None:
    candidate_id = require_string(row, "id")
    require(require_string(row, "classification") == expected_classification, f"{candidate_id} classification mismatch")
    require(require_string(row, "status"), f"{candidate_id} missing status")
    require(require_string(row, "recommendedAction"), f"{candidate_id} missing recommendedAction")
    require(require_list(row, "staticAnchors"), f"{candidate_id} missing static anchors")
    require(require_list(row, "evidenceRefs"), f"{candidate_id} missing evidence refs")
    require(require_list(row, "requiredProofs"), f"{candidate_id} missing required proofs")
    require(require_list(row, "nonClaims"), f"{candidate_id} missing non-claims")


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == EXPECTED_SCHEMA, "schema mismatch")
    require(payload.get("scope") == "copied-profile original-binary control-feel candidates", "scope mismatch")
    for field in BOUNDARY_FALSE_FIELDS:
        require(payload.get(field) is False, f"{field} must be false")
    require(payload.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted gameplay slots mismatch")
    require(payload.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots mismatch")

    risk_model = require_list(payload, "riskModel")
    risks = set()
    for row in risk_model:
        require(isinstance(row, dict), "riskModel rows must be objects")
        risks.add(require_string(row, "risk"))
        require(require_list(row, "targets"), f"{row.get('risk', '<unknown>')} risk row missing targets")
        require(require_string(row, "reason"), f"{row.get('risk', '<unknown>')} risk row missing reason")
        require(require_string(row, "allowedNextAction"), f"{row.get('risk', '<unknown>')} risk row missing allowedNextAction")
    for required_risk in REQUIRED_RISK_LEVELS:
        require(required_risk in risks, f"riskModel missing {required_risk} row")

    candidates = require_list(payload, "candidates")
    require(len(candidates) == len(REQUIRED_CANDIDATES), f"candidate list must contain exactly {len(REQUIRED_CANDIDATES)} rows")
    require(payload.get("candidateCount") == len(candidates), "candidateCount mismatch")
    by_id: dict[str, dict[str, Any]] = {}
    for row in candidates:
        require(isinstance(row, dict), "candidate rows must be objects")
        candidate_id = require_string(row, "id")
        require(candidate_id not in by_id, f"duplicate candidate id: {candidate_id}")
        by_id[candidate_id] = row
    for candidate_id, classification in REQUIRED_CANDIDATES.items():
        require(candidate_id in by_id, f"missing candidate: {candidate_id}")
        validate_candidate(by_id[candidate_id], classification)

    deadzone = by_id["platform_input_directinput_deadzone_0x96"]
    deadzone_text = json.dumps(deadzone, sort_keys=True).lower()
    require("0x00513120" in deadzone_text, "deadzone candidate missing PlatformInput address")
    require("0x00513167" in deadzone_text, "deadzone candidate missing file-backed instruction address")
    require("0x113167" in deadzone_text, "deadzone candidate missing instruction file offset")
    require("0x11316d" in deadzone_text, "deadzone candidate missing immediate file offset")
    require("0x96" in deadzone_text, "deadzone candidate missing 0x96 constant")
    require("file-backed" in deadzone_text, "deadzone candidate missing file-backed boundary")
    require("runtime blocked" in deadzone_text, "deadzone candidate missing runtime-blocked boundary")
    require("physical gamepad" in deadzone_text, "deadzone candidate must require physical gamepad proof")
    require("not patchable yet" in deadzone_text, "deadzone candidate must preserve not-patchable-yet boundary")

    mouse_look_text = json.dumps(by_id["mouse_look_angle_update"], sort_keys=True)
    require("0x00407540" in mouse_look_text, "mouse-look candidate missing function address")
    require("0x006254f4" in mouse_look_text, "mouse-look candidate missing g_MouseSensitivity")

    next_rung = payload.get("recommendedNextRung")
    require(isinstance(next_rung, dict), "missing recommendedNextRung")
    require(next_rung.get("id") == "directinput-deadzone-runtime-a-b-proof", "recommended next rung mismatch")
    require(next_rung.get("addsPatchRow") is False, "recommended next rung must not add patch row")

    boundary = require_string(payload, "claimBoundary")
    boundary_lower = boundary.lower()
    for token in REQUIRED_BOUNDARY_TOKENS:
        require(token.lower() in boundary_lower, f"claim boundary missing token: {token}")

    return {
        "schema": payload["schema"],
        "candidateCount": len(candidates),
        "riskModelRows": len(risk_model),
        "recommendedNextRung": next_rung["id"],
        "visiblePatchRowAdded": payload["visiblePatchRowAdded"],
        "improvedControlFeelProof": payload["improvedControlFeelProof"],
        "physicalGamepadProof": payload["physicalGamepadProof"],
        "acceptedOriginalBinaryGameplaySlots": payload["acceptedOriginalBinaryGameplaySlots"],
        "metadataOnlySlots": payload["metadataOnlySlots"],
    }


def validate_map(path: Path = MAP_PATH) -> dict[str, Any]:
    return validate_payload(read_json(path))


def run_self_test() -> None:
    payload = {
        "schema": EXPECTED_SCHEMA,
        "scope": "copied-profile original-binary control-feel candidates",
        "visiblePatchRowAdded": False,
        "improvedControlFeelProof": False,
        "physicalGamepadProof": False,
        "wallClockLatencyProof": False,
        "acceptedOriginalBinaryGameplaySlots": ["P1", "P2"],
        "metadataOnlySlots": ["P3", "P4"],
        "candidateCount": len(REQUIRED_CANDIDATES),
        "riskModel": [
            {
                "risk": risk,
                "targets": ["test-target"],
                "reason": "test reason",
                "allowedNextAction": "test next action"
            }
            for risk in REQUIRED_RISK_LEVELS
        ],
        "candidates": [
            {
                "id": candidate_id,
                "label": candidate_id,
                "classification": classification,
                "status": "test",
                "staticAnchors": [{"address": "0x00513120" if "deadzone" in candidate_id else "0x00407540"}],
                "evidenceRefs": ["test"],
                "requiredProofs": ["physical gamepad proof" if "deadzone" in candidate_id else "test"],
                "nonClaims": ["test"],
                "recommendedAction": "test"
            }
            for candidate_id, classification in REQUIRED_CANDIDATES.items()
        ],
        "recommendedNextRung": {"id": "directinput-deadzone-runtime-a-b-proof", "addsPatchRow": False},
        "claimBoundary": "This map adds no visible patch row, performs no runtime proof, does not mutate the installed game or original BEA.exe, and does not prove improved control feel, physical gamepad behavior, wall-clock latency, true online multiplayer, active P3/P4 original-binary gameplay, rebuild parity, or no-noticeable-difference parity."
    }
    for row in payload["candidates"]:
        if row["id"] == "platform_input_directinput_deadzone_0x96":
            row["staticAnchors"].append({"value": "0x96"})
            row["staticAnchors"].append({"address": "0x00513167", "fileOffset": "0x113167"})
            row["staticAnchors"].append({"address": "0x0051316D", "fileOffset": "0x11316D"})
            row["nonClaims"].append("not patchable yet")
            row["status"] = "file-backed static candidate; runtime blocked"
            row["recommendedAction"] = "file-backed candidate remains runtime blocked"
        if row["id"] == "mouse_look_angle_update":
            row["staticAnchors"].append({"address": "0x006254f4"})
    validate_payload(payload)

    bad_payload = json.loads(json.dumps(payload))
    bad_payload["candidates"][2]["classification"] = "already_patchable"
    try:
        validate_payload(bad_payload)
    except CandidateMapError:
        pass
    else:
        raise CandidateMapError("self-test expected bad classification to fail")

    bad_payload = json.loads(json.dumps(payload))
    bad_payload["visiblePatchRowAdded"] = True
    try:
        validate_payload(bad_payload)
    except CandidateMapError:
        pass
    else:
        raise CandidateMapError("self-test expected visible patch row claim to fail")

    bad_payload = json.loads(json.dumps(payload))
    bad_payload["riskModel"] = [row for row in bad_payload["riskModel"] if row["risk"] != "highest"]
    try:
        validate_payload(bad_payload)
    except CandidateMapError:
        pass
    else:
        raise CandidateMapError("self-test expected missing risk row to fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        missing_path = Path(temp_dir) / "missing.json"
        try:
            validate_map(missing_path)
        except CandidateMapError:
            pass
        else:
            raise CandidateMapError("self-test expected missing map to fail")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print("WinUI control-feel candidate map probe self-test: PASS")
            return 0
        if not args.check:
            raise CandidateMapError("--check or --self-test is required")
        print(json.dumps(validate_map(), indent=2, sort_keys=True))
        return 0
    except CandidateMapError as exc:
        print(f"WinUI control-feel candidate map probe: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
