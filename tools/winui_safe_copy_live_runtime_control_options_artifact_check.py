#!/usr/bin/env python3
"""Validate a safe-copy live runtime control-options proof artifact."""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
SUPPORTED_MOUSE_SENSITIVITIES = (1.5, 2.25, 3.0)
MOUSE_SENSITIVITY_OFFSET = 0x26C2
CONTROLLER_CONFIG_P1_OFFSET = 0x24B6
CONTROLLER_CONFIG_P2_OFFSET = 0x24BA


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "Artifact root must be a JSON object.")
    return value


def object_at(value: Any, key: str) -> dict[str, Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: Any, key: str) -> list[Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def bool_at(value: Any, key: str) -> bool:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return child


def number_at(value: Any, key: str) -> float:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, (int, float)), f"Missing number: {key}")
    return float(child)


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def arg_list(value: Any, key: str) -> list[str]:
    args = list_at(value, key)
    require(all(isinstance(arg, str) for arg in args), f"{key} must contain only strings.")
    return [str(arg) for arg in args]


def configuration_value(arguments: list[str]) -> int:
    lowered = [arg.lower() for arg in arguments]
    require("-configuration" in lowered, "Launch arguments must include -configuration.")
    index = lowered.index("-configuration")
    require(index + 1 < len(arguments), "-configuration must have a following value.")
    try:
        value = int(arguments[index + 1])
    except ValueError as exc:
        raise ArtifactError("-configuration value must be numeric.") from exc
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


def is_supported_mouse_sensitivity(value: float) -> bool:
    return any(math.isclose(value, preset, rel_tol=0.0, abs_tol=0.0001) for preset in SUPPORTED_MOUSE_SENSITIVITIES)


def validate_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")

    source = object_at(payload, "source")
    source_options = object_at(source, "saveAndOptions")
    require(bool_at(source_options, "unchanged"), "Source defaultoptions/savegames hashes changed.")

    safe_copy = object_at(payload, "safeCopy")
    control = object_at(safe_copy, "controlOptions")
    requested_sharper_mouse_look = bool_at(control, "requestedSharperMouseLook")
    requested_persisted_controller_config = bool(control.get("requestedPersistedControllerConfig", False))
    require(
        requested_sharper_mouse_look or requested_persisted_controller_config,
        "Artifact did not request a safe-copy control options mutation.",
    )
    require(
        string_at(control, "proofLever") in {
            "copied-defaultoptions-mouse-sensitivity-only",
            "copied-defaultoptions-controller-config-only",
            "copied-defaultoptions-mouse-sensitivity-and-controller-config",
        },
        "Control proof lever must identify the copied defaultoptions mutation class.",
    )
    require(bool_at(control, "changedAfterPrepare"), "Copied defaultoptions hash did not change after prepare.")
    require(
        string_at(control, "hashAfterPrepare") != string_at(control, "hashBeforeLaunch"),
        "Copied defaultoptions before/after hashes are identical.",
    )
    changed_ranges = list_at(control, "changedRanges")
    mouse_sensitivity = None
    if requested_sharper_mouse_look:
        mouse_sensitivity = number_at(control, "MouseSensitivity")
        require(
            is_supported_mouse_sensitivity(mouse_sensitivity),
            "Mouse sensitivity read-back was not one of the bounded presets 1.5, 2.25, or 3.0.",
        )
        require(
            any(range_intersects_offset(item, MOUSE_SENSITIVITY_OFFSET) for item in changed_ranges),
            "Changed byte ranges do not intersect defaultoptions mouse sensitivity offset 0x26c2.",
        )

    requested_controller_config = None
    if requested_persisted_controller_config:
        value = control.get("requestedControllerConfig")
        require(isinstance(value, int), "Persisted controller config artifact must record requestedControllerConfig.")
        requested_controller_config = int(value)
        require(1 <= requested_controller_config <= 4, "Persisted controller config must be between 1 and 4.")
        require(
            int(number_at(control, "observedControllerConfigP1")) == requested_controller_config,
            "Observed P1 controller config did not match requested persisted config.",
        )
        require(
            int(number_at(control, "observedControllerConfigP2")) == requested_controller_config,
            "Observed P2 controller config did not match requested persisted config.",
        )
        if requested_controller_config != 1:
            require(
                any(range_intersects_offset(item, CONTROLLER_CONFIG_P1_OFFSET) for item in changed_ranges),
                "Changed byte ranges do not intersect P1 controller config offset 0x24b6.",
            )
            require(
                any(range_intersects_offset(item, CONTROLLER_CONFIG_P2_OFFSET) for item in changed_ranges),
                "Changed byte ranges do not intersect P2 controller config offset 0x24ba.",
            )
    backups = list_at(control, "backups")
    require(len(backups) >= 1, "Control-options patch did not report a local backup.")
    note = string_at(control, "note")
    if requested_persisted_controller_config:
        require(
            "persisted into the copied defaultoptions.bea" in note,
            "Control-options note must identify persisted copied defaultoptions controller config.",
        )
    else:
        require(
            "not a copied defaultoptions.bea controller-config patch" in note,
            "Control-options note must keep launch configuration separate from defaultoptions controller config.",
        )

    launch = object_at(payload, "launch")
    requested_arguments = arg_list(launch, "requestedArguments")
    launched_arguments = arg_list(launch, "arguments")
    require(requested_arguments == launched_arguments, "Launch requestedArguments and arguments differ.")
    config = configuration_value(launched_arguments)

    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")

    boundary = string_at(payload, "claimBoundary")
    require(
        "do not prove improved runtime control feel" in boundary,
        "Claim boundary must reject runtime control-feel proof.",
    )

    return {
        "schema": EXPECTED_SCHEMA,
        "controllerConfiguration": config,
        "persistedControllerConfig": requested_controller_config,
        "mouseSensitivity": mouse_sensitivity,
        "changedRangeCount": len(changed_ranges),
        "backupCount": len(backups),
        "sourceSaveOptionsUnchanged": True,
        "noBeaAfterStop": True,
    }


def valid_fixture() -> dict[str, Any]:
    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "saveAndOptions": {
                "unchanged": True,
            },
        },
        "safeCopy": {
            "controlOptions": {
                "requestedSharperMouseLook": True,
                "requestedPersistedControllerConfig": False,
                "requestedControllerConfig": None,
                "proofLever": "copied-defaultoptions-mouse-sensitivity-only",
                "MouseSensitivity": 2.25,
                "observedControllerConfigP1": 1,
                "observedControllerConfigP2": 1,
                "hashAfterPrepare": "a" * 64,
                "hashBeforeLaunch": "b" * 64,
                "changedAfterPrepare": True,
                "changedRanges": [
                    {
                        "offset": 0x26C4,
                        "offsetHex": "0x26c4",
                        "length": 2,
                        "beforeHex": "803f",
                        "afterHex": "1040",
                    }
                ],
                "backups": [
                    {
                        "relativePath": "defaultoptions.bea.20260617-134112.bak",
                        "size": 10004,
                        "sha256": "c" * 64,
                    }
                ],
                "note": "Controller configuration is not a copied defaultoptions.bea controller-config patch.",
            },
        },
        "launch": {
            "requestedArguments": ["-skipfmv", "-configuration", "2"],
            "arguments": ["-skipfmv", "-configuration", "2"],
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "stop": {
            "Success": True,
        },
        "claimBoundary": "Optional control options do not prove improved runtime control feel.",
    }


def run_self_test() -> None:
    fixture = valid_fixture()
    summary = validate_artifact(fixture)
    require(summary["controllerConfiguration"] == 2, "Self-test did not read controller configuration.")

    persisted = valid_fixture()
    persisted["safeCopy"]["controlOptions"].update(
        {
            "requestedPersistedControllerConfig": True,
            "requestedControllerConfig": 2,
            "proofLever": "copied-defaultoptions-mouse-sensitivity-and-controller-config",
            "observedControllerConfigP1": 2,
            "observedControllerConfigP2": 2,
            "note": "Controller configuration was also persisted into the copied defaultoptions.bea for both players; launch -configuration remains separate.",
        }
    )
    persisted["safeCopy"]["controlOptions"]["changedRanges"].append(
        {
            "offset": 0x24B6,
            "offsetHex": "0x24b6",
            "length": 8,
            "beforeHex": "0100000001000000",
            "afterHex": "0200000002000000",
        }
    )
    persisted_summary = validate_artifact(persisted)
    require(persisted_summary["persistedControllerConfig"] == 2, "Self-test did not read persisted controller config.")

    persisted_default = valid_fixture()
    persisted_default["safeCopy"]["controlOptions"].update(
        {
            "requestedPersistedControllerConfig": True,
            "requestedControllerConfig": 1,
            "proofLever": "copied-defaultoptions-mouse-sensitivity-and-controller-config",
            "observedControllerConfigP1": 1,
            "observedControllerConfigP2": 1,
            "note": "Controller configuration was also persisted into the copied defaultoptions.bea for both players; launch -configuration remains separate.",
        }
    )
    persisted_default_summary = validate_artifact(persisted_default)
    require(persisted_default_summary["persistedControllerConfig"] == 1, "Self-test did not allow default persisted controller config.")

    bad = json.loads(json.dumps(fixture))
    bad["safeCopy"]["controlOptions"]["changedAfterPrepare"] = False
    try:
        validate_artifact(bad)
    except ArtifactError:
        pass
    else:
        raise ArtifactError("Self-test expected changedAfterPrepare=false to fail.")

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "artifact.json"
        path.write_text(json.dumps(fixture), encoding="utf-8")
        validate_artifact(read_json(path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Path to live-safe-copy-runtime-smoke.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print("WinUI safe-copy control-options artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(read_json(Path(args.artifact)))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy control-options artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
