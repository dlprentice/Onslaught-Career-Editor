#!/usr/bin/env python3
"""Validate a safe-copy music CGame caller diagnostic artifact.

The diagnostic does not prove audible playback. It classifies whether a
level-100 CMusic selection could have come from CGame__PlayMusicForCurrentLevel
even when the one-shot CGame entry breakpoint is absent.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "safe-copy-music-cgame-caller-diagnostic-observer.cdb.txt"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
C_GAME_SELECTOR_START = 0x0046DC00
C_GAME_SELECTOR_END_EXCLUSIVE = 0x0046DC30
C_GAME_RESTART_LOOP_START = 0x0046DC30
C_GAME_RUN_LEVEL_START = 0x0046E240
C_GAME_RESTART_LOOP_DIRECT_MUSIC_RETURN = 0x0046E0BF
LEVEL_ID = 100
SELECTION_ID = 2


class DiagnosticError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DiagnosticError(message)


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(payload, dict), "Artifact must be a JSON object.")
    return payload


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
    return bool(child)


def int_at(value: Any, key: str) -> int:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return str(child)


def sha_pair_unchanged(value: dict[str, Any], before_key: str, after_key: str, label: str) -> None:
    before = string_at(value, before_key).lower()
    after = string_at(value, after_key).lower()
    require(bool(re.fullmatch(r"[0-9a-f]{64}", before)), f"{label} before hash must be SHA-256.")
    require(bool(re.fullmatch(r"[0-9a-f]{64}", after)), f"{label} after hash must be SHA-256.")
    require(before == after, f"{label} before/after hashes differ.")


def parse_hex(value: str) -> int:
    return int(value, 16)


def extract_log_path(observer: dict[str, Any]) -> Path:
    result = object_at(observer, "result")
    candidate = result.get("logPath") or observer.get("logPath")
    require(isinstance(candidate, str) and candidate, "CDB log path is missing.")
    path = Path(candidate)
    require(path.is_file(), f"CDB log path is missing: {path}")
    return path


def parse_log(log_text: str) -> dict[str, Any]:
    require("MUSIC_CGAME_DIAG_PROBE_ARMED" in log_text, "Diagnostic probe-arm marker missing.")
    game_rows = []
    caller_rows = []
    kick_rows = []
    open_rows = []
    read_rows = []
    for line in log_text.splitlines():
        if match := re.search(
            r"CGame__PlayMusicForCurrentLevel this=([0-9a-fA-F]+) level=(-?\d+) raw=([0-9a-fA-F]+)",
            line,
            re.IGNORECASE,
        ):
            game_rows.append(
                {
                    "this": parse_hex(match.group(1)),
                    "level": int(match.group(2)),
                    "raw": parse_hex(match.group(3)),
                }
            )
        if match := re.search(
            r"CMusic__PlaySelectionCaller this=([0-9a-fA-F]+) caller=([0-9a-fA-F]+) "
            r"globalGame=([0-9a-fA-F]+) globalLevel=(-?\d+) globalRaw=([0-9a-fA-F]+) "
            r"selection=(-?\d+) fade=(-?\d+) playing=(\d+) head=([0-9a-fA-F]+) current=([0-9a-fA-F]+)",
            line,
            re.IGNORECASE,
        ):
            caller = parse_hex(match.group(2))
            caller_rows.append(
                {
                    "this": parse_hex(match.group(1)),
                    "caller": caller,
                    "callerInCGameSelector": C_GAME_SELECTOR_START <= caller < C_GAME_SELECTOR_END_EXCLUSIVE,
                    "callerInRestartLoop": C_GAME_RESTART_LOOP_START <= caller < C_GAME_RUN_LEVEL_START,
                    "callerIsRestartLoopDirectMusicReturn": caller == C_GAME_RESTART_LOOP_DIRECT_MUSIC_RETURN,
                    "globalGame": parse_hex(match.group(3)),
                    "globalLevel": int(match.group(4)),
                    "globalRaw": parse_hex(match.group(5)),
                    "selection": int(match.group(6)),
                    "fade": int(match.group(7)),
                    "playing": int(match.group(8)),
                    "head": parse_hex(match.group(9)),
                    "current": parse_hex(match.group(10)),
                }
            )
        if "PCPlatform__KickAsyncMusicStreamRead" in line:
            kick_rows.append(line)
        if "COggFileRead__OpenFileAndPrimeDecoder" in line:
            open_rows.append(line)
        if match := re.search(r"COggFileRead__ReadDecodedPcm .*? request=(\d+) ", line, re.IGNORECASE):
            read_rows.append(int(match.group(1)))
    require(caller_rows or game_rows, "Diagnostic log has neither CGame nor CMusic caller rows.")
    game_level_rows = [row for row in game_rows if row["level"] == LEVEL_ID]
    level_selection_rows = [
        row
        for row in caller_rows
        if row["globalLevel"] == LEVEL_ID and row["selection"] == SELECTION_ID
    ]
    cgame_caller_rows = [row for row in level_selection_rows if row["callerInCGameSelector"]]
    restart_direct_rows = [row for row in level_selection_rows if row["callerIsRestartLoopDirectMusicReturn"]]
    if game_level_rows:
        classification = "cgame-entry-row-observed"
    elif restart_direct_rows:
        classification = "restart-loop-direct-level100-music-selection-observed"
    elif cgame_caller_rows:
        classification = "cgame-entry-row-missing-but-playselection-return-address-inside-cgame-selector"
    elif level_selection_rows:
        classification = "level100-selection-observed-from-non-cgame-return-address"
    else:
        classification = "no-level100-selection-caller-row"
    return {
        "classification": classification,
        "gameMusicRows": len(game_rows),
        "gameMusicLevel100Rows": len(game_level_rows),
        "playSelectionCallerRows": len(caller_rows),
        "level100SelectionRows": len(level_selection_rows),
        "cgameSelectorCallerRows": len(cgame_caller_rows),
        "restartLoopDirectRows": len(restart_direct_rows),
        "asyncKickRows": len(kick_rows),
        "oggOpenRows": len(open_rows),
        "oggReadRows": len(read_rows),
        "maxDecodeRequest": max(read_rows) if read_rows else 0,
        "callerRows": caller_rows,
    }


def validate_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")
    require(payload.get("runtimeAudibleOutputProof") is not True, "Diagnostic artifact must not claim audible output proof.")
    source = object_at(payload, "source")
    sha_pair_unchanged(source, "installedHashBefore", "installedHashAfter", "Installed BEA.exe")
    require(bool_at(source, "installedHashUnchanged"), "Installed BEA.exe hash changed.")
    sha_pair_unchanged(source, "overrideHashBefore", "overrideHashAfter", "Clean executable override")
    require(bool_at(source, "overrideHashUnchanged"), "Clean executable override hash changed.")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "Source defaultoptions/savegames changed.")
    safe_copy = object_at(payload, "safeCopy")
    patch_keys = {str(item) for item in list_at(safe_copy, "patchKeys")}
    require(BASE_PATCH_KEYS.issubset(patch_keys), "Required safe-copy patch keys are missing.")
    launch = object_at(payload, "launch")
    require(bool_at(launch, "observedAlive"), "Copied BEA process was not observed alive.")
    launch_args = [str(item).lower() for item in list_at(launch, "arguments")]
    require("-level" in launch_args, "Diagnostic requires a -level launch argument.")
    level_index = launch_args.index("-level")
    require(level_index + 1 < len(launch_args), "-level is missing its value.")
    require(launch_args[level_index + 1] == str(LEVEL_ID), f"Diagnostic requires level {LEVEL_ID}.")
    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "Preexisting BEA process was observed.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")
    observer = object_at(payload, "cdbObserver")
    require(bool_at(observer, "enabled"), "CDB observer must be enabled.")
    command_file = str(observer.get("commandFile") or "")
    require(command_file.replace("/", "\\").lower().endswith(EXPECTED_COMMAND_FILE), "Unexpected CDB command file.")
    result = object_at(observer, "result")
    cleanup = object_at(observer, "cleanup")
    require(str(result.get("status", "")).lower() == "attached", "CDB observer did not attach.")
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB observer cleanup did not complete safely.")
    log_text = extract_log_path(observer).read_text(encoding="utf-8", errors="replace")
    parsed = parse_log(log_text)
    boundary = str(payload.get("claimBoundary", ""))
    require("audible playback" in boundary.lower(), "Claim boundary must still reject audible playback proof.")
    return {
        "schema": EXPECTED_SCHEMA,
        "diagnostic": "music-cgame-caller",
        "classification": parsed["classification"],
        "gameMusicRows": parsed["gameMusicRows"],
        "gameMusicLevel100Rows": parsed["gameMusicLevel100Rows"],
        "playSelectionCallerRows": parsed["playSelectionCallerRows"],
        "level100SelectionRows": parsed["level100SelectionRows"],
        "cgameSelectorCallerRows": parsed["cgameSelectorCallerRows"],
        "restartLoopDirectRows": parsed["restartLoopDirectRows"],
        "asyncKickRows": parsed["asyncKickRows"],
        "oggOpenRows": parsed["oggOpenRows"],
        "oggReadRows": parsed["oggReadRows"],
        "maxDecodeRequest": parsed["maxDecodeRequest"],
        "cgameSelectorRange": {
            "start": f"0x{C_GAME_SELECTOR_START:08x}",
            "endExclusive": f"0x{C_GAME_SELECTOR_END_EXCLUSIVE:08x}",
        },
        "restartLoopRange": {
            "start": f"0x{C_GAME_RESTART_LOOP_START:08x}",
            "endExclusive": f"0x{C_GAME_RUN_LEVEL_START:08x}",
            "directMusicCallReturn": f"0x{C_GAME_RESTART_LOOP_DIRECT_MUSIC_RETURN:08x}",
        },
        "runtimeAudibleOutputProof": False,
        "claimBoundary": (
            "Diagnostic only. A CMusic return address inside CGame selector/restart-loop code is evidence "
            "about CDB attach timing/call provenance, not audible playback, volume, loop, all-cue, gameplay, "
            "or rebuild proof."
        ),
    }


def fixture(log_path: Path, *, cgame_row: bool, cgame_caller: bool) -> dict[str, Any]:
    lines = ["MUSIC_CGAME_DIAG_PROBE_ARMED"]
    if cgame_row:
        lines.append("CGame__PlayMusicForCurrentLevel this=008a9a98 level=100 raw=00000064")
    caller = f"{C_GAME_RESTART_LOOP_DIRECT_MUSIC_RETURN:08x}" if cgame_caller else "0051a97b"
    lines.extend(
        [
            f"CMusic__PlaySelectionCaller this=00889a48 caller={caller} globalGame=008a9a98 globalLevel=100 globalRaw=00000064 selection=2 fade=0 playing=0 head=04400000 current=00000000",
            r"PCPlatform__KickAsyncMusicStreamRead path=data\music\BEA_04(Master).ogg",
            r"COggFileRead__OpenFileAndPrimeDecoder this=0440a000 path=data\music\BEA_04(Master).ogg",
            "COggFileRead__ReadDecodedPcm this=0440a000 request=4096 out=04500000 outBytes=0019f4b0",
        ]
    )
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashBefore": "1" * 64,
            "installedHashAfter": "1" * 64,
            "installedHashUnchanged": True,
            "overrideHashBefore": "2" * 64,
            "overrideHashAfter": "2" * 64,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {"patchKeys": ["resolution_gate", "force_windowed"]},
        "launch": {
            "observedAlive": True,
            "arguments": ["-skipfmv", "-level", "100"],
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "stop": {"Success": True},
        "cdbObserver": {
            "enabled": True,
            "commandFile": f"tools/runtime-probes/{EXPECTED_COMMAND_FILE}",
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path)},
            "cleanup": {"status": "stopped"},
        },
        "claimBoundary": "Diagnostic only; does not prove audible playback, gameplay parity, or rebuild parity.",
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="music-cgame-diagnostic-") as temp_dir:
        root = Path(temp_dir)
        log_path = root / "windbg.log"
        summary = validate_artifact(fixture(log_path, cgame_row=True, cgame_caller=True))
        require(summary["classification"] == "cgame-entry-row-observed", "Expected direct CGame row classification.")
        summary = validate_artifact(fixture(log_path, cgame_row=False, cgame_caller=True))
        require(
            summary["classification"] == "restart-loop-direct-level100-music-selection-observed",
            "Expected restart-loop direct music selection classification.",
        )
        # An inside-wrapper return address remains a useful synthetic guard for the attach-timing class.
        synthetic_wrapper = fixture(log_path, cgame_row=False, cgame_caller=True)
        log_path.write_text(
            "\n".join(
                [
                    "MUSIC_CGAME_DIAG_PROBE_ARMED",
                    "CMusic__PlaySelectionCaller this=00889a48 caller=0046dc2c globalGame=008a9a98 globalLevel=100 globalRaw=00000064 selection=2 fade=0 playing=0 head=04400000 current=00000000",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        synthetic_wrapper["cdbObserver"]["result"]["logPath"] = str(log_path)
        synthetic_wrapper["cdbObserver"]["logPath"] = str(log_path)
        summary = validate_artifact(synthetic_wrapper)
        require(
            summary["classification"] == "cgame-entry-row-missing-but-playselection-return-address-inside-cgame-selector",
            "Expected attach-timing candidate classification.",
        )
        summary = validate_artifact(fixture(log_path, cgame_row=False, cgame_caller=False))
        require(
            summary["classification"] == "level100-selection-observed-from-non-cgame-return-address",
            "Expected non-CGame caller classification.",
        )
        bad = fixture(log_path, cgame_row=False, cgame_caller=True)
        bad["runtimeAudibleOutputProof"] = True
        try:
            validate_artifact(bad)
        except DiagnosticError:
            pass
        else:
            raise DiagnosticError("Self-test expected audible-output claim to fail.")
        missing_marker = fixture(log_path, cgame_row=False, cgame_caller=True)
        log_path.write_text("CMusic__PlaySelectionCaller this=00889a48 caller=0046dc22 globalGame=008a9a98 globalLevel=100 globalRaw=00000064 selection=2 fade=0 playing=0 head=04400000 current=00000000\n", encoding="utf-8")
        try:
            validate_artifact(missing_marker)
        except DiagnosticError:
            pass
        else:
            raise DiagnosticError("Self-test expected missing probe-arm marker to fail.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Live runtime smoke JSON artifact")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            run_self_test()
            print("WinUI safe-copy music CGame caller diagnostic checker self-test: PASS")
            return 0
        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        print(json.dumps(validate_artifact(read_json(Path(args.artifact))), indent=2, sort_keys=True))
        return 0
    except DiagnosticError as exc:
        print(f"WinUI safe-copy music CGame caller diagnostic check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
