#!/usr/bin/env python3
"""Validate a safe-copy control-feel diagnostics artifact matrix."""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_MOUSE_SENSITIVITY = 2.25
MOUSE_SENSITIVITY_OFFSET = 0x26C2
CONTROLLER_CONFIG_P1_OFFSET = 0x24B6
CONTROLLER_CONFIG_P2_OFFSET = 0x24BA


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    display_name: str
    controller_config: int
    requires_persisted_config: bool = False
    requires_mouse_sensitivity: bool = False
    allows_no_control_mutation: bool = False


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "baseline_config1",
        "Baseline config 1",
        controller_config=1,
        allows_no_control_mutation=True,
    ),
    Scenario(
        "sharpened_config1",
        "Sensitivity test config 1",
        controller_config=1,
        requires_persisted_config=True,
        requires_mouse_sensitivity=True,
    ),
    Scenario(
        "swapped_config2",
        "Swapped sticks config 2",
        controller_config=2,
        requires_persisted_config=True,
    ),
    Scenario(
        "alternate_config3",
        "Alternate morph/jets config 3",
        controller_config=3,
        requires_persisted_config=True,
    ),
    Scenario(
        "swapped_alternate_config4",
        "Swapped sticks plus alternate morph/jets config 4",
        controller_config=4,
        requires_persisted_config=True,
    ),
)


class MatrixError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MatrixError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    require(isinstance(payload, dict), f"{path} root must be a JSON object.")
    return payload


def object_at(value: Any, key: str, *, nullable: bool = False) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        raise MatrixError(f"Parent for {key} must be an object.")
    child = value.get(key)
    if nullable and child is None:
        return None
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: Any, key: str) -> list[Any]:
    if not isinstance(value, dict):
        raise MatrixError(f"Parent for {key} must be an object.")
    child = value.get(key)
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def bool_at(value: Any, key: str) -> bool:
    if not isinstance(value, dict):
        raise MatrixError(f"Parent for {key} must be an object.")
    child = value.get(key)
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return child


def number_at(value: Any, key: str) -> float:
    if not isinstance(value, dict):
        raise MatrixError(f"Parent for {key} must be an object.")
    child = value.get(key)
    require(isinstance(child, (int, float)), f"Missing number: {key}")
    return float(child)


def string_at(value: Any, key: str) -> str:
    if not isinstance(value, dict):
        raise MatrixError(f"Parent for {key} must be an object.")
    child = value.get(key)
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def launch_arguments(payload: dict[str, Any]) -> list[str]:
    launch = object_at(payload, "launch")
    assert launch is not None
    args = list_at(launch, "arguments")
    require(all(isinstance(arg, str) for arg in args), "launch.arguments must contain only strings.")
    requested = list_at(launch, "requestedArguments")
    require(requested == args, "launch.requestedArguments and launch.arguments must match.")
    return [str(arg) for arg in args]


def configuration_value(arguments: list[str]) -> int:
    lowered = [arg.lower() for arg in arguments]
    require("-configuration" in lowered, "Launch arguments must include -configuration.")
    index = lowered.index("-configuration")
    require(index + 1 < len(arguments), "-configuration must have a following value.")
    try:
        value = int(arguments[index + 1])
    except ValueError as exc:
        raise MatrixError("-configuration value must be numeric.") from exc
    require(1 <= value <= 4, "-configuration value must be between 1 and 4.")
    return value


def range_intersects_offset(diff_range: Any, offset_to_check: int) -> bool:
    if not isinstance(diff_range, dict):
        return False
    offset = diff_range.get("offset")
    length = diff_range.get("length")
    if not isinstance(offset, int) or not isinstance(length, int):
        return False
    return offset <= offset_to_check + 3 and offset + length > offset_to_check


def capture_has_visual_proof(capture: dict[str, Any]) -> bool:
    if capture.get("foregroundMatchesTarget") is True:
        return True
    occlusion = capture.get("occlusion")
    return (
        isinstance(occlusion, dict)
        and occlusion.get("checked") is True
        and occlusion.get("targetFound") is True
        and occlusion.get("occlusionFree") is True
        and occlusion.get("occludingWindowCount") == 0
    )


def validate_capture_visibility(payload: dict[str, Any]) -> int:
    captures = list_at(payload, "captures")
    visual_count = 0
    for capture in captures:
        if not isinstance(capture, dict):
            continue
        status = str(capture.get("status", "")).lower()
        if status == "captured" and capture_has_visual_proof(capture):
            visual_count += 1
    return visual_count


def validate_scenario(scenario: Scenario, payload: dict[str, Any], *, require_visual: bool) -> dict[str, Any]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, f"{scenario.scenario_id}: unexpected artifact schema.")

    source = object_at(payload, "source")
    assert source is not None
    source_options = object_at(source, "saveAndOptions")
    assert source_options is not None
    require(bool_at(source_options, "unchanged"), f"{scenario.scenario_id}: source defaultoptions/savegames hashes changed.")

    process_baseline = object_at(payload, "processBaseline")
    assert process_baseline is not None
    require(bool_at(process_baseline, "noPreexistingBea"), f"{scenario.scenario_id}: BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), f"{scenario.scenario_id}: BEA process remained after stop.")

    stop = object_at(payload, "stop")
    assert stop is not None
    require(bool_at(stop, "Success"), f"{scenario.scenario_id}: managed stop did not succeed.")

    config = configuration_value(launch_arguments(payload))
    require(
        config == scenario.controller_config,
        f"{scenario.scenario_id}: expected -configuration {scenario.controller_config}, got {config}.",
    )

    safe_copy = object_at(payload, "safeCopy")
    assert safe_copy is not None
    control = object_at(safe_copy, "controlOptions", nullable=True)
    if control is None:
        require(
            scenario.allows_no_control_mutation,
            f"{scenario.scenario_id}: copied defaultoptions controlOptions proof is required.",
        )
    else:
        changed_ranges = list_at(control, "changedRanges")
        if scenario.requires_mouse_sensitivity:
            require(bool_at(control, "requestedSharperMouseLook"), f"{scenario.scenario_id}: sharpened mouse look was not requested.")
            require(
                math.isclose(number_at(control, "MouseSensitivity"), EXPECTED_MOUSE_SENSITIVITY, rel_tol=0.0, abs_tol=0.0001),
                f"{scenario.scenario_id}: mouse sensitivity read-back was not 2.25.",
            )
            require(
                any(range_intersects_offset(item, MOUSE_SENSITIVITY_OFFSET) for item in changed_ranges),
                f"{scenario.scenario_id}: changed byte ranges do not intersect mouse sensitivity offset 0x26c2.",
            )

        if scenario.requires_persisted_config:
            require(
                bool_at(control, "requestedPersistedControllerConfig"),
                f"{scenario.scenario_id}: persisted copied defaultoptions controller config was not requested.",
            )
            require(
                int(number_at(control, "requestedControllerConfig")) == scenario.controller_config,
                f"{scenario.scenario_id}: requested persisted controller config mismatch.",
            )
            require(
                int(number_at(control, "observedControllerConfigP1")) == scenario.controller_config,
                f"{scenario.scenario_id}: observed P1 controller config mismatch.",
            )
            require(
                int(number_at(control, "observedControllerConfigP2")) == scenario.controller_config,
                f"{scenario.scenario_id}: observed P2 controller config mismatch.",
            )
            if scenario.controller_config != 1:
                require(
                    any(range_intersects_offset(item, CONTROLLER_CONFIG_P1_OFFSET) for item in changed_ranges),
                    f"{scenario.scenario_id}: changed byte ranges do not intersect P1 controller config offset 0x24b6.",
                )
                require(
                    any(range_intersects_offset(item, CONTROLLER_CONFIG_P2_OFFSET) for item in changed_ranges),
                    f"{scenario.scenario_id}: changed byte ranges do not intersect P2 controller config offset 0x24ba.",
                )

    visual_count = validate_capture_visibility(payload)
    if require_visual:
        require(visual_count > 0, f"{scenario.scenario_id}: no foreground-matched or z-order occlusion-free capture found.")

    boundary = string_at(payload, "claimBoundary")
    require(
        "do not prove improved runtime control feel" in boundary,
        f"{scenario.scenario_id}: claim boundary must reject improved runtime control-feel proof.",
    )

    return {
        "scenarioId": scenario.scenario_id,
        "controllerConfiguration": config,
        "controlOptionsProof": control is not None,
        "visualCaptureCount": visual_count,
    }


def validate_matrix(assignments: dict[str, Path], *, require_visual: bool) -> dict[str, Any]:
    expected_ids = {scenario.scenario_id for scenario in SCENARIOS}
    actual_ids = set(assignments)
    missing = sorted(expected_ids - actual_ids)
    extra = sorted(actual_ids - expected_ids)
    require(not missing, f"Missing control-feel diagnostic scenarios: {', '.join(missing)}.")
    require(not extra, f"Unknown control-feel diagnostic scenarios: {', '.join(extra)}.")

    summaries = []
    for scenario in SCENARIOS:
        summaries.append(validate_scenario(scenario, read_json(assignments[scenario.scenario_id]), require_visual=require_visual))

    return {
        "schema": "winui-control-feel-diagnostics-matrix.v1",
        "matrixComplete": True,
        "visualRequired": require_visual,
        "scenarioCount": len(summaries),
        "scenarios": summaries,
        "claimBoundary": "This matrix proves safe-copy launch/options materialization and optional unoccluded capture coverage only; it does not prove improved control feel, deadzone behavior, look curves, camera response, gameplay parity, or rebuild parity.",
    }


def scenario_plan() -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        launch_arguments = ["-skipfmv", "-configuration", str(scenario.controller_config)]
        scenarios.append(
            {
                "scenarioId": scenario.scenario_id,
                "displayName": scenario.display_name,
                "launchArguments": launch_arguments,
                "requiresPersistedControllerConfig": scenario.requires_persisted_config,
                "expectedControllerConfiguration": scenario.controller_config,
                "requiresMouseSensitivity": scenario.requires_mouse_sensitivity,
                "expectedMouseSensitivity": EXPECTED_MOUSE_SENSITIVITY if scenario.requires_mouse_sensitivity else None,
                "allowsNoControlMutation": scenario.allows_no_control_mutation,
                "requiredArtifactKey": f"--artifact {scenario.scenario_id}=<live-safe-copy-runtime-smoke.json>",
                "runtimeEvidenceRequiredForControlFeelClaim": True,
            }
        )

    return {
        "schema": "winui-control-feel-diagnostics-plan.v1",
        "scenarioCount": len(scenarios),
        "scenarios": scenarios,
        "recommendedValidationCommand": "py -3 tools\\winui_control_feel_diagnostics_matrix.py "
        + " ".join(scenario["requiredArtifactKey"] for scenario in scenarios)
        + " --require-visual",
        "claimBoundary": "This plan defines safe-copy control diagnostics artifacts to collect; it does not prove improved control feel, deadzone behavior, look curves, camera response, gameplay parity, online multiplayer, or rebuild parity.",
    }


def base_fixture(
    config: int,
    *,
    control: dict[str, Any] | None,
    foreground: bool = False,
    occlusion_free: bool = False,
) -> dict[str, Any]:
    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "saveAndOptions": {
                "unchanged": True,
            },
        },
        "safeCopy": {
            "controlOptions": control,
        },
        "launch": {
            "requestedArguments": ["-skipfmv", "-configuration", str(config)],
            "arguments": ["-skipfmv", "-configuration", str(config)],
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "stop": {
            "Success": True,
        },
        "captures": [
            {
                "status": "captured",
                "foregroundMatchesTarget": foreground,
                "occlusion": {
                    "checked": True,
                    "targetFound": True,
                    "occlusionFree": occlusion_free,
                    "occludingWindowCount": 0 if occlusion_free else 1,
                },
            }
        ],
        "claimBoundary": "Optional control options do not prove improved runtime control feel.",
    }


def control_fixture(config: int, *, sharpen: bool) -> dict[str, Any]:
    changed_ranges: list[dict[str, Any]] = []
    if sharpen:
        changed_ranges.append(
            {
                "offset": 0x26C4,
                "offsetHex": "0x26c4",
                "length": 2,
                "beforeHex": "803f",
                "afterHex": "1040",
            }
        )
    if config != 1:
        changed_ranges.append(
            {
                "offset": 0x24B6,
                "offsetHex": "0x24b6",
                "length": 8,
                "beforeHex": "0100000001000000",
                "afterHex": f"{config:02x}000000{config:02x}000000",
            }
        )

    return {
        "requestedSharperMouseLook": sharpen,
        "requestedPersistedControllerConfig": True,
        "requestedControllerConfig": config,
        "MouseSensitivity": EXPECTED_MOUSE_SENSITIVITY if sharpen else 1.0,
        "observedControllerConfigP1": config,
        "observedControllerConfigP2": config,
        "changedRanges": changed_ranges,
    }


def run_self_test() -> None:
    plan = scenario_plan()
    require(plan["schema"] == "winui-control-feel-diagnostics-plan.v1", "Self-test plan schema mismatch.")
    require(plan["scenarioCount"] == len(SCENARIOS), "Self-test plan scenario count mismatch.")
    planned_ids = {row["scenarioId"] for row in plan["scenarios"]}
    require(planned_ids == {scenario.scenario_id for scenario in SCENARIOS}, "Self-test plan scenario ids mismatch.")
    require("--require-visual" in plan["recommendedValidationCommand"], "Self-test plan must recommend visual validation.")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        fixtures = {
            "baseline_config1": base_fixture(1, control=None),
            "sharpened_config1": base_fixture(1, control=control_fixture(1, sharpen=True)),
            "swapped_config2": base_fixture(2, control=control_fixture(2, sharpen=False)),
            "alternate_config3": base_fixture(3, control=control_fixture(3, sharpen=False)),
            "swapped_alternate_config4": base_fixture(4, control=control_fixture(4, sharpen=False)),
        }
        assignments: dict[str, Path] = {}
        for scenario_id, payload in fixtures.items():
            path = root / f"{scenario_id}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            assignments[scenario_id] = path

        summary = validate_matrix(assignments, require_visual=False)
        require(summary["scenarioCount"] == len(SCENARIOS), "Self-test matrix scenario count mismatch.")

        try:
            validate_matrix({key: value for key, value in assignments.items() if key != "baseline_config1"}, require_visual=False)
        except MatrixError:
            pass
        else:
            raise MatrixError("Self-test expected missing baseline_config1 to fail.")

        try:
            validate_matrix(assignments, require_visual=True)
        except MatrixError:
            pass
        else:
            raise MatrixError("Self-test expected require_visual to fail without foreground captures.")

        occlusion_free = base_fixture(1, control=None, occlusion_free=True)
        occlusion_free_path = root / "baseline_occlusion_free.json"
        occlusion_free_path.write_text(json.dumps(occlusion_free), encoding="utf-8")
        assignments["baseline_config1"] = occlusion_free_path
        try:
            validate_matrix(assignments, require_visual=True)
        except MatrixError:
            pass
        else:
            raise MatrixError("Self-test expected require_visual to fail until every scenario has visual proof.")

        visible_assignments: dict[str, Path] = {}
        for scenario in SCENARIOS:
            path = root / f"{scenario.scenario_id}.visible.json"
            if scenario.scenario_id == "baseline_config1":
                payload = base_fixture(1, control=None, occlusion_free=True)
            elif scenario.scenario_id == "sharpened_config1":
                payload = base_fixture(1, control=control_fixture(1, sharpen=True), occlusion_free=True)
            else:
                payload = base_fixture(scenario.controller_config, control=control_fixture(scenario.controller_config, sharpen=False), occlusion_free=True)
            path.write_text(json.dumps(payload), encoding="utf-8")
            visible_assignments[scenario.scenario_id] = path
        validate_matrix(visible_assignments, require_visual=True)


def parse_assignment(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("--artifact must be SCENARIO_ID=PATH.")
    scenario_id, path = raw.split("=", 1)
    scenario_id = scenario_id.strip()
    if not scenario_id:
        raise argparse.ArgumentTypeError("Scenario id may not be empty.")
    return scenario_id, Path(path.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", action="append", default=[], type=parse_assignment, help="Scenario assignment in the form scenario_id=live-safe-copy-runtime-smoke.json")
    parser.add_argument("--require-visual", action="store_true", help="Require at least one foreground-matched capture per scenario.")
    parser.add_argument("--plan", action="store_true", help="Print the five-scenario control-feel diagnostics collection plan.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.plan:
            print(json.dumps(scenario_plan(), indent=2, sort_keys=True))
            return 0

        if args.self_test:
            run_self_test()
            print("WinUI control-feel diagnostics matrix self-test: PASS")
            return 0

        assignments = dict(args.artifact)
        require(bool(assignments), "Provide --artifact scenario_id=path entries or --self-test.")
        print(json.dumps(validate_matrix(assignments, require_visual=args.require_visual), indent=2, sort_keys=True))
        return 0
    except MatrixError as exc:
        print(f"WinUI control-feel diagnostics matrix check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
