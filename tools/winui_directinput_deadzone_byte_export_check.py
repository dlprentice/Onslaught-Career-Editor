#!/usr/bin/env python3
"""Validate the DirectInput deadzone byte-export proof boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe.original.backup")
DEFAULT_ARTIFACT = (
    ROOT
    / "subagents"
    / "winui-control-feel"
    / "directinput-deadzone-byte-export-20260619"
    / "directinput-deadzone-byte-export.json"
)
READINESS = ROOT / "release" / "readiness" / "winui_directinput_deadzone_byte_export_2026-06-19.md"
CANDIDATE_MAP = ROOT / "roadmap" / "original-binary-control-feel-candidate-map.v1.json"
CANDIDATE_MAP_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-control-feel-candidate-map.v1.json"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
PACKAGE_JSON = ROOT / "package.json"
PATCH_CATALOG = ROOT / "patches" / "catalog" / "patches.v2.json"

SCHEMA = "winui-directinput-deadzone-byte-export.v1"
EXPECTED_HASH = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_SIZE = 2_506_752
IMAGE_BASE = 0x400000
FUNCTION_VA = 0x00513120
NEXT_FUNCTION_VA = 0x00513370
INSTRUCTION_VA = 0x00513167
IMMEDIATE_VA = 0x0051316D
INSTRUCTION_BYTES = bytes.fromhex("c7 85 e0 30 03 00 96 00 00 00")
IMMEDIATE_BYTES = bytes.fromhex("96 00 00 00")
EXPECTED_SCRIPT = (
    r"py -3 tools\winui_directinput_deadzone_byte_export_check_test.py && "
    r"py -3 tools\winui_directinput_deadzone_byte_export_check.py --self-test && "
    r"py -3 tools\winui_directinput_deadzone_byte_export_check.py --check"
)


class DeadzoneByteExportError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DeadzoneByteExportError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def va_to_file_offset(va: int) -> int:
    return va - IMAGE_BASE


def hex_bytes(value: bytes) -> str:
    return " ".join(f"{byte:02x}" for byte in value)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise DeadzoneByteExportError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DeadzoneByteExportError(f"invalid JSON: {path}: {exc}") from exc
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def build_export(exe_path: Path) -> dict[str, Any]:
    require(exe_path.is_file(), f"clean specimen not found: {exe_path}")
    data = exe_path.read_bytes()
    file_size = len(data)
    file_hash = sha256_bytes(data)
    require(file_size == EXPECTED_SIZE, f"clean specimen size mismatch: {file_size}")
    require(file_hash == EXPECTED_HASH, f"clean specimen SHA-256 mismatch: {file_hash}")

    function_offset = va_to_file_offset(FUNCTION_VA)
    next_function_offset = va_to_file_offset(NEXT_FUNCTION_VA)
    instruction_offset = va_to_file_offset(INSTRUCTION_VA)
    immediate_offset = va_to_file_offset(IMMEDIATE_VA)
    instruction = data[instruction_offset : instruction_offset + len(INSTRUCTION_BYTES)]
    immediate = data[immediate_offset : immediate_offset + len(IMMEDIATE_BYTES)]
    function_window = data[function_offset:next_function_offset]
    focused_start = va_to_file_offset(0x00513150)
    focused_end = va_to_file_offset(0x00513180)
    focused_window = data[focused_start:focused_end]

    require(instruction == INSTRUCTION_BYTES, f"instruction bytes mismatch: {hex_bytes(instruction)}")
    require(immediate == IMMEDIATE_BYTES, f"immediate bytes mismatch: {hex_bytes(immediate)}")

    return {
        "schema": SCHEMA,
        "date": "2026-06-19",
        "scope": "static clean-specimen byte export only",
        "sourceSpecimen": {
            "sha256": file_hash,
            "size": file_size,
            "canonicalCleanSteamRetail": True,
            "installedGameMutation": False,
            "originalExecutableMutation": False,
        },
        "addressConversion": {
            "imageBase": f"0x{IMAGE_BASE:08x}",
            "rule": "file_offset = VA - 0x400000 for .text in the known Steam retail BEA.exe",
            "functionVa": f"0x{FUNCTION_VA:08x}",
            "functionFileOffset": f"0x{function_offset:06x}",
            "nextFunctionVa": f"0x{NEXT_FUNCTION_VA:08x}",
            "nextFunctionFileOffset": f"0x{next_function_offset:06x}",
        },
        "candidateInstruction": {
            "functionName": "PlatformInput__InitDirectInput",
            "instructionVa": f"0x{INSTRUCTION_VA:08x}",
            "instructionFileOffset": f"0x{instruction_offset:06x}",
            "instructionTextFromWave848": "MOV dword ptr [EBP + 0x330e0], 0x96",
            "instructionBytes": hex_bytes(instruction),
            "expectedInstructionBytes": hex_bytes(INSTRUCTION_BYTES),
            "immediateVa": f"0x{IMMEDIATE_VA:08x}",
            "immediateFileOffset": f"0x{immediate_offset:06x}",
            "immediateBytes": hex_bytes(immediate),
            "immediateLittleEndianValue": 0x96,
            "fieldTextFromWave848": "this+0x330e0 runtime field; not a file offset",
            "fileBackedImmediate": True,
        },
        "windows": {
            "functionWindowStartOffset": f"0x{function_offset:06x}",
            "functionWindowEndOffsetExclusive": f"0x{next_function_offset:06x}",
            "functionWindowLength": len(function_window),
            "functionWindowSha256": sha256_bytes(function_window),
            "focusedWindowStartOffset": f"0x{focused_start:06x}",
            "focusedWindowEndOffsetExclusive": f"0x{focused_end:06x}",
            "focusedWindowLength": len(focused_window),
            "focusedWindowHex": hex_bytes(focused_window),
            "focusedWindowSha256": sha256_bytes(focused_window),
        },
        "unprovenAlternateValues": [
            {"value": "0x00", "bytes": "00 00 00 00", "status": "unproven-not-recommended"},
            {"value": "0x32", "bytes": "32 00 00 00", "status": "unproven-not-recommended"},
            {"value": "0x64", "bytes": "64 00 00 00", "status": "unproven-not-recommended"},
        ],
        "claimBooleans": {
            "addsPatchRow": False,
            "visiblePatchRowAdded": False,
            "runtimeProof": False,
            "improvedControlFeelProof": False,
            "physicalGamepadProof": False,
            "directInputRuntimeProof": False,
            "copiedExecutablePatchProof": False,
            "wallClockLatencyProof": False,
            "trueOnlineMultiplayerProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "nextProofRequirements": [
            "copied-executable A/B byte verification before any patch row",
            "restore verification before any patch row",
            "physical gamepad or equivalent DirectInput runtime proof",
            "no-input negative control",
            "DirectInput poll/accessor evidence",
            "downstream virtual-controller and player-state evidence",
            "per-configuration regression across controller configs 1-4",
        ],
        "claimBoundary": (
            "This proves the documented 0x96 DirectInput deadzone setup value is a file-backed immediate in the "
            "canonical clean Steam retail BEA.exe. It does not add a patch row, does not prove runtime DirectInput "
            "behavior, does not prove physical gamepad behavior, does not prove improved control feel, and does not "
            "prove online, rebuild, or no-noticeable-difference parity."
        ),
    }


def validate_export_payload(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == SCHEMA, "schema mismatch")
    source = payload.get("sourceSpecimen")
    require(isinstance(source, dict), "missing sourceSpecimen")
    require(source.get("sha256") == EXPECTED_HASH, "source hash mismatch")
    require(source.get("size") == EXPECTED_SIZE, "source size mismatch")
    require(source.get("installedGameMutation") is False, "installed game mutation must be false")
    require(source.get("originalExecutableMutation") is False, "original executable mutation must be false")

    conversion = payload.get("addressConversion")
    require(isinstance(conversion, dict), "missing addressConversion")
    require(conversion.get("functionVa") == "0x00513120", "function VA mismatch")
    require(conversion.get("functionFileOffset") == "0x113120", "function file offset mismatch")

    row = payload.get("candidateInstruction")
    require(isinstance(row, dict), "missing candidateInstruction")
    require(row.get("instructionVa") == "0x00513167", "instruction VA mismatch")
    require(row.get("instructionFileOffset") == "0x113167", "instruction file offset mismatch")
    require(row.get("instructionBytes") == hex_bytes(INSTRUCTION_BYTES), "instruction bytes mismatch")
    require(row.get("immediateVa") == "0x0051316d", "immediate VA mismatch")
    require(row.get("immediateFileOffset") == "0x11316d", "immediate file offset mismatch")
    require(row.get("immediateBytes") == hex_bytes(IMMEDIATE_BYTES), "immediate bytes mismatch")
    require(row.get("immediateLittleEndianValue") == 0x96, "immediate value mismatch")
    require(row.get("fileBackedImmediate") is True, "file-backed immediate proof missing")
    require("not a file offset" in str(row.get("fieldTextFromWave848", "")), "runtime field caveat missing")

    windows = payload.get("windows")
    require(isinstance(windows, dict), "missing windows")
    require(windows.get("functionWindowLength") == 0x250, "function window length mismatch")
    require(isinstance(windows.get("focusedWindowSha256"), str) and len(windows["focusedWindowSha256"]) == 64, "focused hash missing")

    claims = payload.get("claimBooleans")
    require(isinstance(claims, dict), "missing claimBooleans")
    for key, value in claims.items():
        require(value is False, f"claim must be false: {key}")

    alternates = payload.get("unprovenAlternateValues")
    require(isinstance(alternates, list) and alternates, "missing unproven alternates")
    for alternate in alternates:
        require(isinstance(alternate, dict), "alternate rows must be objects")
        require(alternate.get("status") == "unproven-not-recommended", "alternate values must remain unproven")

    boundary = str(payload.get("claimBoundary", "")).lower()
    for token in (
        "file-backed immediate",
        "does not add a patch row",
        "does not prove runtime directinput behavior",
        "does not prove physical gamepad behavior",
        "does not prove improved control feel",
    ):
        require(token in boundary, f"claim boundary missing token: {token}")

    return {
        "schema": payload["schema"],
        "functionVa": conversion["functionVa"],
        "instructionVa": row["instructionVa"],
        "instructionFileOffset": row["instructionFileOffset"],
        "immediateFileOffset": row["immediateFileOffset"],
        "instructionBytes": row["instructionBytes"],
        "fileBackedImmediate": row["fileBackedImmediate"],
        "addsPatchRow": claims["addsPatchRow"],
        "runtimeProof": claims["runtimeProof"],
        "physicalGamepadProof": claims["physicalGamepadProof"],
    }


def deadzone_patch_catalog_rows() -> list[str]:
    rows = read_json(PATCH_CATALOG).get("patches")
    require(isinstance(rows, list), "patch catalog missing patches list")
    matches: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        blob = json.dumps(row, sort_keys=True).lower()
        if "deadzone" in blob or "platforminput" in blob:
            matches.append(str(row.get("id", "<missing-id>")))
    return matches


def validate_repository() -> None:
    readiness = read_text(READINESS)
    for token in (
        "DirectInput Deadzone Byte Export Readiness Note",
        "0x00513167",
        "0x113167",
        "0x0051316D",
        "0x11316D",
        "C7 85 E0 30 03 00 96 00 00 00",
        "addsPatchRow=false",
        "runtimeProof=false",
        "physicalGamepadProof=false",
        "improvedControlFeelProof=false",
        "no Patch Bench row",
        "no player-facing deadzone claim",
    ):
        require(token in readiness, f"readiness note missing token: {token}")

    candidate = read_json(CANDIDATE_MAP)
    require(candidate.get("schema") == "original-binary-control-feel-candidate-map.v1", "candidate map schema mismatch")
    rows = candidate.get("candidates")
    require(isinstance(rows, list), "candidate map missing candidates")
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    deadzone = by_id.get("platform_input_directinput_deadzone_0x96")
    require(isinstance(deadzone, dict), "deadzone candidate missing")
    require(deadzone.get("classification") == "file_backed_static_candidate_runtime_blocked", "deadzone classification not normalized")
    deadzone_text = json.dumps(deadzone, sort_keys=True).lower()
    for token in ("0x00513167", "0x113167", "0x11316d", "file-backed", "runtime blocked", "not patchable yet"):
        require(token in deadzone_text, f"deadzone candidate missing token: {token}")
    next_rung = candidate.get("recommendedNextRung")
    require(isinstance(next_rung, dict), "missing recommendedNextRung")
    require(next_rung.get("addsPatchRow") is False, "next rung must not add patch row")
    require("runtime" in str(next_rung.get("id", "")).lower(), "next rung should now be runtime/readiness oriented")
    require(read_text(CANDIDATE_MAP) == read_text(CANDIDATE_MAP_MIRROR), "candidate map lore mirror mismatch")

    register = read_text(REGISTER)
    for token in (
        "1 file-backed static DirectInput deadzone byte-export candidate",
        "0 runtime-proven control-feel byte rows",
        "directinput-deadzone-runtime-a-b-proof",
        "no player-facing deadzone patch row",
    ):
        require(token in register, f"register missing token: {token}")
    require(read_text(REGISTER) == read_text(REGISTER_MIRROR), "register lore mirror mismatch")

    scripts = read_json(PACKAGE_JSON).get("scripts")
    require(isinstance(scripts, dict), "package scripts missing")
    require(scripts.get("test:winui-directinput-deadzone-byte-export") == EXPECTED_SCRIPT, "package script mismatch")
    aggregate = scripts.get("test:winui-copied-profile-runtime", "")
    require("test:winui-directinput-deadzone-byte-export" in aggregate, "aggregate runtime script missing deadzone byte export check")

    matches = deadzone_patch_catalog_rows()
    require(not matches, f"patch catalog must not contain deadzone/PlatformInput rows yet: {matches}")


def validate_current_exe(exe_path: Path, artifact_path: Path | None = None) -> dict[str, Any]:
    summary = validate_export_payload(build_export(exe_path))
    if artifact_path is not None and artifact_path.is_file():
        artifact = read_json(artifact_path)
        artifact_summary = validate_export_payload(artifact)
        require(artifact_summary["instructionBytes"] == summary["instructionBytes"], "artifact instruction bytes mismatch")
        require(artifact_summary["immediateFileOffset"] == summary["immediateFileOffset"], "artifact immediate offset mismatch")
    return summary


def export_artifact(exe_path: Path, artifact_path: Path) -> dict[str, Any]:
    payload = build_export(exe_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return validate_export_payload(payload)


def run_self_test() -> None:
    payload = {
        "schema": SCHEMA,
        "sourceSpecimen": {
            "sha256": EXPECTED_HASH,
            "size": EXPECTED_SIZE,
            "installedGameMutation": False,
            "originalExecutableMutation": False,
        },
        "addressConversion": {
            "functionVa": "0x00513120",
            "functionFileOffset": "0x113120",
        },
        "candidateInstruction": {
            "instructionVa": "0x00513167",
            "instructionFileOffset": "0x113167",
            "instructionBytes": hex_bytes(INSTRUCTION_BYTES),
            "immediateVa": "0x0051316d",
            "immediateFileOffset": "0x11316d",
            "immediateBytes": hex_bytes(IMMEDIATE_BYTES),
            "immediateLittleEndianValue": 0x96,
            "fileBackedImmediate": True,
            "fieldTextFromWave848": "this+0x330e0 runtime field; not a file offset",
        },
        "windows": {
            "functionWindowLength": 0x250,
            "focusedWindowSha256": "0" * 64,
        },
        "unprovenAlternateValues": [{"value": "0x64", "bytes": "64 00 00 00", "status": "unproven-not-recommended"}],
        "claimBooleans": {
            "addsPatchRow": False,
            "visiblePatchRowAdded": False,
            "runtimeProof": False,
            "improvedControlFeelProof": False,
            "physicalGamepadProof": False,
            "directInputRuntimeProof": False,
        },
        "claimBoundary": (
            "file-backed immediate; does not add a patch row; does not prove runtime DirectInput behavior; "
            "does not prove physical gamepad behavior; does not prove improved control feel"
        ),
    }
    validate_export_payload(payload)
    bad = json.loads(json.dumps(payload))
    bad["claimBooleans"]["runtimeProof"] = True
    try:
        validate_export_payload(bad)
    except DeadzoneByteExportError:
        pass
    else:
        raise DeadzoneByteExportError("self-test expected runtimeProof=true to fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        fixture = Path(temp_dir) / "artifact.json"
        fixture.write_text(json.dumps(payload), encoding="utf-8")
        validate_export_payload(read_json(fixture))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
            print("WinUI DirectInput deadzone byte-export checker self-test: PASS")
            return 0
        if args.export:
            print(json.dumps(export_artifact(args.exe, args.artifact), indent=2, sort_keys=True))
            return 0
        if args.check:
            validate_repository()
            print(json.dumps(validate_current_exe(args.exe, args.artifact), indent=2, sort_keys=True))
            return 0
        raise DeadzoneByteExportError("--self-test, --export, or --check is required")
    except DeadzoneByteExportError as exc:
        print(f"WinUI DirectInput deadzone byte-export check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
