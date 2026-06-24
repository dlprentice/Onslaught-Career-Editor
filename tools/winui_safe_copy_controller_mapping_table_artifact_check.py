#!/usr/bin/env python3
"""Validate CDB-backed safe-copy controller mapping-table artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
EXPECTED_COMMAND_FILE = "controller-mapping-table-observer.cdb.txt"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
ROW_STRIDE_DWORDS = 8
ENTRY_ALIGNED_BASE = 0x008892D8
ENTRY_ID_VIEW_BASE = 0x008892DC
TABLE_DUMP_WORDS = 0x220
BUTTON_PAUSE = 56
KEY_ONCE = 8
KEY_ON = 9
O_KEY_ARGS = {0x4F, 0x18}


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), "artifact must be a JSON object")
    return value


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def bool_at(value: dict[str, Any], key: str) -> bool:
    child = value.get(key)
    require(isinstance(child, bool), f"missing boolean: {key}")
    return bool(child)


def string_at(value: dict[str, Any], key: str) -> str:
    child = value.get(key)
    require(isinstance(child, str), f"missing string: {key}")
    return child


def string_list_at(value: dict[str, Any], key: str) -> list[str]:
    values = list_at(value, key)
    require(all(isinstance(item, str) for item in values), f"{key} must contain only strings")
    return [str(item) for item in values]


def signed32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def capture_has_visual_proof(item: dict[str, Any]) -> bool:
    if item.get("visualProof") is True or item.get("foregroundMatchesTarget") is True:
        return True
    occlusion = item.get("occlusion")
    return (
        isinstance(occlusion, dict)
        and occlusion.get("checked") is True
        and occlusion.get("targetFound") is True
        and occlusion.get("occlusionFree") is True
        and occlusion.get("occludingWindowCount") == 0
    )


def visual_capture_count(captures: list[Any]) -> int:
    return sum(1 for item in captures if isinstance(item, dict) and capture_has_visual_proof(item))


DD_LINE_RE = re.compile(r"^(?P<address>[0-9a-f`]{8,17})\s+(?P<values>(?:[0-9a-f]{8}\s*){1,8})$", re.IGNORECASE)


def parse_dd_words(text: str, base: int = ENTRY_ID_VIEW_BASE) -> list[int]:
    words_by_address: dict[int, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = DD_LINE_RE.match(line)
        if not match:
            continue
        address = int(match.group("address").replace("`", ""), 16)
        values = [int(value, 16) for value in match.group("values").split()]
        for offset, value in enumerate(values):
            words_by_address[address + offset * 4] = value

    words: list[int] = []
    for index in range(TABLE_DUMP_WORDS):
        address = base + index * 4
        if address not in words_by_address:
            break
        words.append(words_by_address[address])
    return words


def decode_mapping_rows(words: list[int]) -> tuple[list[dict[str, Any]], bool]:
    require(len(words) >= ROW_STRIDE_DWORDS, "mapping table dump did not include one full row")
    rows: list[dict[str, Any]] = []
    sentinel_found = False
    for index in range(0, len(words) - ROW_STRIDE_DWORDS + 1, ROW_STRIDE_DWORDS):
        row_words = words[index : index + ROW_STRIDE_DWORDS]
        entry_id = signed32(row_words[0])
        if entry_id == -1:
            sentinel_found = True
            break
        rows.append(
            {
                "index": index // ROW_STRIDE_DWORDS,
                "entryId": entry_id,
                "button": entry_id,
                "raw": [f"{value & 0xFFFFFFFF:08x}" for value in row_words],
                "slot0": decode_slot(row_words[1], row_words[2], row_words[3]),
                "slot1": decode_slot(row_words[4], row_words[5], row_words[6]),
                "nextEntryActiveFromShiftedView": signed32(row_words[7]),
            }
        )
    return rows, sentinel_found


def decode_slot(input_code: int, push_type: int, key_arg: int) -> dict[str, Any]:
    key_arg &= 0xFFFFFFFF
    return {
        "inputCode": signed32(input_code),
        "pushType": signed32(push_type),
        "keyArg": signed32(key_arg),
    }


def pause_o_slots(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for row in rows:
        if row["entryId"] != BUTTON_PAUSE:
            continue
        for slot_name in ("slot0", "slot1"):
            slot = row[slot_name]
            if slot["pushType"] in {KEY_ONCE, KEY_ON} and slot["keyArg"] in O_KEY_ARGS:
                hits.append(
                    {
                        "row": row["index"],
                        "slot": slot_name,
                        "pushType": slot["pushType"],
                        "keyArg": slot["keyArg"],
                    }
                )
    return hits


def classify_o_pause(rows: list[dict[str, Any]], hits: list[dict[str, Any]]) -> str:
    if hits:
        return "runtime-table-o-pause-slot-present"
    if any(row["entryId"] == BUTTON_PAUSE for row in rows):
        return "runtime-table-pause-row-present-without-o-slot"
    return "runtime-table-no-o-pause-row"


def observer_log_path(artifact: dict[str, Any]) -> Path:
    observer = object_at(artifact, "cdbObserver")
    require(bool_at(observer, "enabled"), "CDB observer was not enabled")
    command_file = string_at(observer, "commandFile").replace("/", "\\").lower()
    require(command_file.endswith(EXPECTED_COMMAND_FILE), "unexpected CDB observer command file")
    result = object_at(observer, "result")
    cleanup = object_at(observer, "cleanup")
    require(result.get("status") == "attached", "CDB observer did not attach")
    require(bool_at(result, "logExists"), "CDB log was not created")
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB cleanup did not finish")
    candidate = result.get("logPath") or observer.get("logPath")
    require(isinstance(candidate, str) and candidate, "CDB log path is missing")
    path = Path(candidate)
    require(path.is_file(), f"CDB log path is missing: {path}")
    return path


def validate_common(artifact: dict[str, Any], min_capture_count: int) -> Path:
    require(artifact.get("schemaVersion") == EXPECTED_SCHEMA, "unexpected artifact schema")
    source = object_at(artifact, "source")
    require(bool_at(source, "installedHashUnchanged"), "installed BEA.exe hash changed")
    require(bool_at(source, "overrideHashUnchanged"), "clean override BEA.exe hash changed")
    require(bool_at(object_at(source, "saveAndOptions"), "unchanged"), "source save/options changed")

    safe_copy = object_at(artifact, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "safe copy did not apply windowed compatibility patch keys")

    launch = object_at(artifact, "launch")
    require(bool_at(launch, "observedAlive"), "copied BEA process was not observed alive")
    baseline = object_at(artifact, "processBaseline")
    require(bool_at(baseline, "noPreexistingBea"), "preexisting BEA process was present")
    require(bool_at(baseline, "noBeaAfterStop"), "BEA process remained after stop")
    require(bool_at(object_at(artifact, "stop"), "Success"), "managed copied-game stop failed")

    captures = list_at(artifact, "captures")
    require(len(captures) >= min_capture_count, f"capture count below {min_capture_count}")
    require(visual_capture_count(captures) >= min_capture_count, "not enough visual-proof captures")
    return observer_log_path(artifact)


def validate_artifact(path: Path, min_capture_count: int = 1) -> dict[str, Any]:
    artifact = read_json(path)
    log_path = validate_common(artifact, min_capture_count)
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    require("safe-copy controller mapping table observer" in log_text, "mapping-table observer marker missing")
    words = parse_dd_words(log_text)
    require(len(words) >= ROW_STRIDE_DWORDS, "mapping-table dd output not found")
    rows, sentinel_found = decode_mapping_rows(words)
    require(sentinel_found, "mapping-table sentinel was not found in dumped row range")
    hits = pause_o_slots(rows)
    return {
        "schema": "winui-safe-copy-controller-mapping-table-diagnostic.v1",
        "artifact": str(path),
        "cdbLog": str(log_path),
        "mappingTable": {
            "entryAlignedBase": f"0x{ENTRY_ALIGNED_BASE:08x}",
            "entryIdViewBase": f"0x{ENTRY_ID_VIEW_BASE:08x}",
            "rowStrideDwords": ROW_STRIDE_DWORDS,
            "dumpedDwords": len(words),
            "rowCount": len(rows),
            "sentinelFound": sentinel_found,
            "pauseRows": [row for row in rows if row["entryId"] == BUTTON_PAUSE],
            "oPauseSlots": hits,
        },
        "oPauseClassification": classify_o_pause(rows, hits),
        "claim": "safe-copy exact-PID CDB observer dumped and decoded the live retail CController__DoMappings row window",
        "claimBoundary": (
            "Diagnostic only. This proves one copied-runtime memory table observation from the live "
            "CController__DoMappings row window, not O pause behavior, defaultoptions/save persistence, "
            "free-camera pause safety, control feel, gameplay safety, online networking, rebuild parity, "
            "or no-noticeable-difference parity."
        ),
    }


def dd_lines(words: list[int], base: int = ENTRY_ID_VIEW_BASE) -> str:
    lines: list[str] = []
    for index in range(0, len(words), 8):
        chunk = words[index : index + 8]
        address = base + index * 4
        lines.append(f"{address:08x}  " + " ".join(f"{value & 0xFFFFFFFF:08x}" for value in chunk))
    return "\n".join(lines) + "\n"


def make_artifact(root: Path, *, include_o_pause: bool) -> Path:
    log_path = root / "windbg.log"
    rows = [
        [1, 0, KEY_ONCE, 0x21, 0, KEY_ONCE, 0x21, 0],
        [BUTTON_PAUSE, 0, KEY_ONCE, 0x18 if include_o_pause else 0x00000001, 0xFFFFFFFF, 0, 0, 0],
        [0xFFFFFFFF, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0xFFFFFFFF, 0, 0xFFFFFFFF, 0],
    ]
    words = [value for row in rows for value in row]
    log_path.write_text("=== safe-copy controller mapping table observer ===\n" + dd_lines(words), encoding="utf-8")
    artifact = {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {"unchanged": True},
        },
        "safeCopy": {"patchKeys": sorted(BASE_PATCH_KEYS)},
        "launch": {"observedAlive": True},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "captures": [{"status": "captured", "fileSize": 1024, "visualProof": True}],
        "cdbObserver": {
            "enabled": True,
            "commandFile": f"tools/runtime-probes/{EXPECTED_COMMAND_FILE}",
            "result": {"status": "attached", "logExists": True, "logPath": str(log_path)},
            "cleanup": {"status": "stopped"},
        },
    }
    path = root / "artifact.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        summary = validate_artifact(make_artifact(Path(temp_dir), include_o_pause=True))
        require(summary["oPauseClassification"] == "runtime-table-o-pause-slot-present", "expected positive O pause slot")

    with tempfile.TemporaryDirectory() as temp_dir:
        summary = validate_artifact(make_artifact(Path(temp_dir), include_o_pause=False))
        require(summary["oPauseClassification"] == "runtime-table-pause-row-present-without-o-slot", "expected pause row without O slot")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive")
        if args.self_test:
            self_test()
            print("WinUI safe-copy controller mapping-table artifact checker self-test: PASS")
            return 0
        require(args.artifact is not None, "artifact is required unless --self-test is used")
        print(json.dumps(validate_artifact(args.artifact, args.min_capture_count), indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI safe-copy controller mapping-table artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
