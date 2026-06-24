#!/usr/bin/env python3
"""Preflight physical gamepad readiness for local-multiplayer runtime proof."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness" / "local_multiplayer_gamepad_readiness_2026-06-18.md"
CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
PACKAGE_JSON = ROOT / "package.json"
CONTROLLER_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "frontend" / "controller-system.md"
PLATFORM_INPUT_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PlatformInput.cpp" / "_index.md"
CONTROLLER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"

SCHEMA = "winui-safe-copy-local-multiplayer-gamepad-readiness.v1"

GAMEPAD_HINTS = (
    "hid-compliant game controller",
    "game controller",
    "gamepad",
    "joystick",
    "xbox",
    "xinput",
    "dualsense",
    "dualshock",
    "wireless controller",
    "steam controller",
    "8bitdo",
    "playstation",
    "nintendo switch",
)

FALSE_POSITIVE_HINTS = (
    "host controller",
    "audio controller",
    "network controller",
    "memory controller",
    "storage controller",
    "system controller",
    "usb composite device",
    "consumer control device",
    "vendor-defined device",
    "keyboard",
    "mouse",
    "touchpad",
    "bluetooth adapter",
    "wireless radio controls",
)


class ReadinessError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadinessError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def row_text(row: dict[str, Any]) -> str:
    return " ".join(normalize_text(value) for value in row.values()).lower()


def has_gamepad_hint(text: str) -> bool:
    return any(hint in text for hint in GAMEPAD_HINTS)


def has_false_positive_hint(text: str) -> bool:
    return any(hint in text for hint in FALSE_POSITIVE_HINTS)


def classify_pnp_device(row: dict[str, Any]) -> dict[str, Any]:
    text = row_text(row)
    candidate = has_gamepad_hint(text) and not has_false_positive_hint(text)
    return {
        "candidate": candidate,
        "status": normalize_text(row.get("Status")),
        "class": normalize_text(row.get("Class")),
        "friendlyName": normalize_text(row.get("FriendlyName") or row.get("Name")),
        "instanceId": normalize_text(row.get("InstanceId") or row.get("PNPDeviceID")),
        "reason": "gamepad-like present PnP device" if candidate else "not gamepad-like or excluded generic device",
    }


def classify_registry_row(row: dict[str, Any]) -> dict[str, Any]:
    oem_name = normalize_text(row.get("OEMName"))
    key = normalize_text(row.get("Key"))
    text = f"{oem_name} {key}".lower()
    candidate = bool(oem_name) and has_gamepad_hint(text) and not has_false_positive_hint(text)
    return {
        "candidate": candidate,
        "root": normalize_text(row.get("Root")),
        "key": key,
        "oemName": oem_name,
        "reason": "named joystick OEM registry row" if candidate else "blank or not gamepad-like registry row",
    }


def summarize_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    pnp_rows = inventory.get("pnpDevices")
    registry_rows = inventory.get("joystickRegistry")
    require(isinstance(pnp_rows, list), "inventory missing pnpDevices list")
    require(isinstance(registry_rows, list), "inventory missing joystickRegistry list")

    classified_pnp = [classify_pnp_device(row) for row in pnp_rows if isinstance(row, dict)]
    classified_registry = [classify_registry_row(row) for row in registry_rows if isinstance(row, dict)]
    present_candidates = [row for row in classified_pnp if row["candidate"]]
    registry_candidates = [row for row in classified_registry if row["candidate"]]
    ready = bool(present_candidates)
    status = "ready_for_physical_gamepad_runtime_attempt" if ready else "blocked_no_present_gamepad"
    return {
        "schemaVersion": SCHEMA,
        "collectedAtUtc": inventory.get("collectedAtUtc") or datetime.now(timezone.utc).isoformat(),
        "status": status,
        "physicalGamepadRuntimeProofReady": ready,
        "presentGamepadCandidates": present_candidates,
        "registryGamepadCandidates": registry_candidates,
        "presentGamepadCandidateCount": len(present_candidates),
        "registryGamepadCandidateCount": len(registry_candidates),
        "pnpDeviceCount": len(classified_pnp),
        "joystickRegistryRowCount": len(classified_registry),
        "claimBoundary": (
            "This is a workstation readiness preflight only. Hardware presence is a precondition, not BEA DirectInput "
            "polling proof, not virtual-controller routing proof, not visible movement proof, and not online multiplayer proof."
        ),
        "nextRuntimeProofRequires": [
            "copied profile launch with installed/source file hashes unchanged",
            "exact managed BEA PID and CDB attachment",
            "CDB rows at 0x00513370 PlatformInput__PollPadState",
            "CDB rows at CPCController joy accessors such as 0x005147f0 or 0x00514640..0x005146d0",
            "zero keyboard SendInput/keybd_event/PostMessage positive-stimulus counters",
            "downstream 0x0042e4d0 CController__SendButtonAction and 0x004d3110 CPlayer__ReceiveButtonActionState rows",
            "negative no-input control",
        ],
        "classifiedPnpDevices": classified_pnp,
        "classifiedJoystickRegistry": classified_registry,
    }


def collect_windows_inventory() -> dict[str, Any]:
    script = r"""
$ErrorActionPreference = 'SilentlyContinue'
$pnp = Get-PnpDevice -PresentOnly | Select-Object Status,Class,FriendlyName,InstanceId
$roots = @(
  'HKCU:\System\CurrentControlSet\Control\MediaProperties\PrivateProperties\Joystick\OEM',
  'HKLM:\SYSTEM\CurrentControlSet\Control\MediaProperties\PrivateProperties\Joystick\OEM'
)
$joy = foreach ($root in $roots) {
  if (Test-Path $root) {
    Get-ChildItem $root | ForEach-Object {
      $props = Get-ItemProperty -LiteralPath $_.PSPath
      [pscustomobject]@{
        Root = $root
        Key = $_.PSChildName
        OEMName = $props.OEMName
        OEMData = [string]$props.OEMData
      }
    }
  }
}
[pscustomobject]@{
  collectedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
  pnpDevices = @($pnp)
  joystickRegistry = @($joy)
} | ConvertTo-Json -Depth 5
"""
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=False,
        capture_output=True,
        text=True,
    )
    require(completed.returncode == 0, f"PowerShell inventory failed: {completed.stderr.strip()}")
    return json.loads(completed.stdout)


def check_token(path: Path, token: str, failures: list[str]) -> None:
    if token not in read_text(path):
        failures.append(f"{path} missing token: {token}")


def check_docs() -> None:
    failures: list[str] = []
    readiness_tokens = (
        "Local Multiplayer Physical Gamepad Readiness Note",
        "1 readiness/preflight artifact; 0 physical DirectInput/gamepad runtime proof artifacts",
        "hardware detection is a precondition, not BEA polling proof",
        "blocked_no_present_gamepad",
        "0x00513120 PlatformInput__InitDirectInput",
        "0x00513370 PlatformInput__PollPadState",
        "0x005147f0 CPCController__GetJoyButtonOn",
        "0x00514640 CPCController__GetJoyAnalogueLeftX",
        "0x0042e4d0 CController__SendButtonAction",
        "0x004d3110 CPlayer__ReceiveButtonActionState",
        "zero keyboard SendInput/keybd_event/PostMessage positive-stimulus counters",
        "not online multiplayer proof",
    )
    contract_tokens = (
        "Local multiplayer physical gamepad readiness preflight",
        "1 readiness/preflight artifact; 0 physical DirectInput/gamepad runtime proof artifacts",
        "hardware detection is a precondition, not BEA polling proof",
        "tools\\winui_safe_copy_local_multiplayer_gamepad_readiness.py",
        "blocked_no_present_gamepad",
        "Physical DirectInput/gamepad routing remains open",
    )
    register_tokens = (
        "1 gamepad-readiness preflight; 0 physical DirectInput/gamepad runtime proof artifacts",
        "hardware presence is only a precondition",
        "physical gamepad isolation",
    )
    capability_tokens = (
        "gamepad-readiness preflight",
        "blocked_no_present_gamepad",
        "0 physical DirectInput/gamepad runtime proof artifacts",
    )
    for token in readiness_tokens:
        check_token(READINESS, token, failures)
    for token in contract_tokens:
        check_token(CONTRACT, token, failures)
    for token in register_tokens:
        check_token(REGISTER, token, failures)
    for token in capability_tokens:
        check_token(CAPABILITIES, token, failures)
    for token in ("0x00513120", "PlatformInput__InitDirectInput", "0x00513370", "PlatformInput__PollPadState"):
        check_token(PLATFORM_INPUT_INDEX, token, failures)
    for token in (
        "CPCController__GetJoyButtonOn",
        "CPCController__GetJoyAnalogueLeftX",
    ):
        check_token(CONTROLLER_SYSTEM, token, failures)
        check_token(CONTROLLER_INDEX, token, failures)
    check_token(CONTROLLER_INDEX, "CController__SendButtonAction", failures)
    check_token(CONTROLLER_SYSTEM, "SendButtonAction", failures)

    package_scripts = json.loads(read_text(PACKAGE_JSON)).get("scripts", {})
    expected = r"py -3 tools\winui_safe_copy_local_multiplayer_gamepad_readiness.py --check"
    if package_scripts.get("test:winui-safe-copy-local-multiplayer-gamepad-readiness") != expected:
        failures.append("missing package gamepad-readiness script")
    if read_text(CONTRACT) != read_text(CONTRACT_MIRROR):
        failures.append("local multiplayer contract lore mirror mismatch")
    if read_text(CAPABILITIES) != read_text(CAPABILITIES_MIRROR):
        failures.append("current capabilities lore mirror mismatch")
    if failures:
        raise ReadinessError("\n".join(failures))


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fixture = {
            "collectedAtUtc": "2026-06-18T00:00:00Z",
            "pnpDevices": [
                {"Status": "OK", "Class": "HIDClass", "FriendlyName": "HID-compliant game controller", "InstanceId": "HID\\VID_045E&PID_02FF"},
                {"Status": "OK", "Class": "System", "FriendlyName": "USB xHCI Compliant Host Controller", "InstanceId": "PCI\\VEN_FAKE"},
            ],
            "joystickRegistry": [],
        }
        summary = summarize_inventory(fixture)
        require(summary["physicalGamepadRuntimeProofReady"] is True, "fixture game controller should be ready")
        require(summary["presentGamepadCandidateCount"] == 1, "fixture should have one present gamepad candidate")

        blank_registry = {
            "collectedAtUtc": "2026-06-18T00:00:00Z",
            "pnpDevices": [
                {"Status": "OK", "Class": "HIDClass", "FriendlyName": "HID-compliant vendor-defined device", "InstanceId": "HID\\VID_FAKE"},
                {"Status": "OK", "Class": "System", "FriendlyName": "High Definition Audio Controller", "InstanceId": "PCI\\VEN_FAKE"},
            ],
            "joystickRegistry": [{"Root": "HKCU", "Key": "VID_045E&PID_0000", "OEMName": ""}],
        }
        summary = summarize_inventory(blank_registry)
        require(summary["physicalGamepadRuntimeProofReady"] is False, "blank/generic fixture should not be ready")
        require(summary["status"] == "blocked_no_present_gamepad", "blank/generic fixture should be blocked")

        output = Path(tmp) / "summary.json"
        output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        require(json.loads(output.read_text(encoding="utf-8"))["schemaVersion"] == SCHEMA, "summary should round-trip JSON")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", action="store_true", help="collect and summarize live Windows controller inventory")
    parser.add_argument("--output", type=Path, help="optional path for --inventory summary JSON")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true", help="run self-test and doc/package wiring checks")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer gamepad readiness self-test: PASS")
        return 0
    if args.check:
        self_test()
        check_docs()
        print("WinUI safe-copy local multiplayer gamepad readiness check: PASS")
        return 0
    if args.inventory:
        summary = summarize_inventory(collect_windows_inventory())
        text = json.dumps(summary, indent=2, sort_keys=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    raise SystemExit("use --self-test, --check, or --inventory")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReadinessError as exc:
        print(f"WinUI safe-copy local multiplayer gamepad readiness check: FAIL: {exc}")
        raise SystemExit(2)
