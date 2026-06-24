#!/usr/bin/env python3
"""Validate Wave580 IScript camera/objective Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave580-iscript-camera-objective-00533b70"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_camera_objective_wave580_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

COMMON_TAGS = {
    "static-reaudit",
    "iscript-camera-objective-wave580",
    "retail-binary-evidence",
    "mission-script",
    "iscript",
    "command-handler",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x00533b70": {
        "name": "IScript__Create3PointPanCamera",
        "signature": "void __stdcall IScript__Create3PointPanCamera(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "pan-camera", "camera", "thing-input", "vector-input", "script-command-registry"},
        "comment_tokens": ("Create3PointPanCamera(thing,pos0,pos1,pos2,duration)", "0x0064fa9c", "CGame__SetCurrentCamera"),
        "decompile_file": "00533b70_IScript__Create3PointPanCamera.c",
        "decompile_tokens": ("script_args", "CSPtrSet__AddToTail", "CBSpline__ctor", "CPanCamera__ctor", "CGame__SetCurrentCamera"),
    },
    "0x00533eb0": {
        "name": "IScript__Create4PointPanCamera",
        "signature": "void __stdcall IScript__Create4PointPanCamera(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "pan-camera", "camera", "thing-input", "vector-input", "script-command-registry"},
        "comment_tokens": ("Create4PointPanCamera(thing,pos0,pos1,pos2,pos3,duration)", "0x0064fad8", "CGame__SetCurrentCamera"),
        "decompile_file": "00533eb0_IScript__Create4PointPanCamera.c",
        "decompile_tokens": ("script_args", "Vec3__SetXYZ", "CBSpline__ctor", "CPanCamera__ctor", "CGame__SetCurrentCamera"),
    },
    "0x005343e0": {
        "name": "IScript__PrimaryObjectiveComplete",
        "signature": "void __stdcall IScript__PrimaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "objective-state", "primary-objective", "objective-complete", "msl-command", "script-command-registry"},
        "comment_tokens": ("PrimaryObjectiveComplete(objective_index,text_id)", "DAT_008a9ae0", "state 1"),
        "decompile_file": "005343e0_IScript__PrimaryObjectiveComplete.c",
        "decompile_tokens": ("DAT_008a9ae0", "DAT_008a9adc", "= 1"),
    },
    "0x00534410": {
        "name": "IScript__SecondaryObjectiveComplete",
        "signature": "void __stdcall IScript__SecondaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "objective-state", "secondary-objective", "objective-complete", "msl-command", "script-command-registry"},
        "comment_tokens": ("SecondaryObjectiveComplete(objective_index,text_id)", "DAT_008a9b30", "state 1"),
        "decompile_file": "00534410_IScript__SecondaryObjectiveComplete.c",
        "decompile_tokens": ("DAT_008a9b30", "DAT_008a9b2c", "= 1"),
    },
    "0x00534440": {
        "name": "IScript__PrimaryObjectiveFailed",
        "signature": "void __stdcall IScript__PrimaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "objective-state", "primary-objective", "objective-failed", "msl-command", "script-command-registry"},
        "comment_tokens": ("PrimaryObjectiveFailed(objective_index,text_id)", "DAT_008a9ae0", "state 2"),
        "decompile_file": "00534440_IScript__PrimaryObjectiveFailed.c",
        "decompile_tokens": ("DAT_008a9ae0", "DAT_008a9adc", "= 2"),
    },
    "0x00534470": {
        "name": "IScript__SecondaryObjectiveFailed",
        "signature": "void __stdcall IScript__SecondaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)",
        "tags": COMMON_TAGS | {"fixed-script-abi", "objective-state", "secondary-objective", "objective-failed", "msl-command", "script-command-registry"},
        "comment_tokens": ("SecondaryObjectiveFailed(objective_index,text_id)", "DAT_008a9b30", "state 2"),
        "decompile_file": "00534470_IScript__SecondaryObjectiveFailed.c",
        "decompile_tokens": ("DAT_008a9b30", "DAT_008a9b2c", "= 2"),
    },
}


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def row_count(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values: dict[str, int] = {}
    for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1)):
        values[key] = int(value)
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def require_doc_tokens(path: Path, tokens: tuple[str, ...], failures: list[str]) -> None:
    try:
        text = read_text(path)
    except FileNotFoundError:
        failures.append(f"missing doc: {path}")
        return
    require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)


def run_check() -> list[str]:
    failures: list[str] = []

    require_log_summary(
        BASE / "wave580_apply_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave580_apply.log",
        {"updated": 6, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "wave580_apply_final_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_counts = {
        "post_metadata.tsv": 6,
        "post_tags.tsv": 6,
        "post_xrefs.tsv": 6,
        "post_target_instructions.tsv": 5454,
        "post_decompile/index.tsv": 6,
        "post_vtables.tsv": 36,
    }
    for relative_path, expected in expected_counts.items():
        actual = row_count(BASE / relative_path)
        if actual != expected:
            failures.append(f"{relative_path} row count mismatch: {actual} != {expected}")

    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
    decomp_index = read_tsv(BASE / "post_decompile" / "index.tsv")
    xrefs = read_text(BASE / "post_xrefs.tsv")
    instructions = read_text(BASE / "post_target_instructions.tsv")
    vtables = read_text(BASE / "post_vtables.tsv")

    require_tokens("xrefs", xrefs, ("ScriptCommandRegistry__InitBuiltins", "IScript__Create3PointPanCamera", "IScript__SecondaryObjectiveFailed"), failures)
    require_tokens("instructions", instructions, ("RET\t0xc", "0x64fa9c", "0x64fad8", "0x8a9a98", "0x8a9adc", "0x8a9b2c"), failures)
    require_tokens("vtables", vtables, ("005e4ea4", "CFloatDataType__Add", "005e4af8", "CIntDataType__Add", "005e4d50", "CBoolDataType__Assign"), failures)

    overclaim_tokens = (
        "runtime behavior proven",
        "runtime mission-script behavior proven",
        "runtime mission-objective UI behavior proven",
        "source identity proven",
        "rebuild parity proven",
        "fully RE'ed",
        "fully REed",
    )
    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post_metadata.tsv")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} metadata status is {row['status']}")
        if row["name"] != spec["name"]:
            failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
        if row["signature"] != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
        require_tokens(f"{address} comment", row["comment"], spec["comment_tokens"], failures)
        for bad_token in overclaim_tokens:
            if bad_token in row["comment"]:
                failures.append(f"{address} comment overclaims: {bad_token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post_tags.tsv")
        else:
            actual_tags = set(filter(None, tag_row["tags"].split(";")))
            missing = sorted(spec["tags"] - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {missing}")

        decomp_row = decomp_index.get(address)
        if decomp_row is None:
            failures.append(f"{address} missing from post_decompile/index.tsv")
        elif decomp_row["status"] != "OK":
            failures.append(f"{address} decompile status is {decomp_row['status']}")
        decomp_text = read_text(BASE / "post_decompile" / spec["decompile_file"])
        require_tokens(f"{address} decompile", decomp_text, spec["decompile_tokens"], failures)

    queue = json.loads(read_text(QUEUE_JSON))
    if queue.get("status") != "PASS":
        failures.append("queue status is not PASS")
    signals = queue.get("qualitySignals", {})
    expected_signals = {
        "commentlessFunctionCount": 3154,
        "undefinedSignatureCount": 1418,
        "paramSignatureCount": 1127,
    }
    for key, expected in expected_signals.items():
        actual = signals.get(key)
        if actual != expected:
            failures.append(f"queue {key} mismatch: {actual} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x005345d0" or head.get("name") != "IScript__GetVectorLength":
        failures.append(f"unexpected next queue head: {head}")

    backup = json.loads(read_text(BASE / "wave580_backup_summary.json"))
    if backup.get("status") != "PASS":
        failures.append("backup status is not PASS")
    if backup.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {backup.get('fileCount')} != 19")
    if int(backup.get("totalBytes", 0)) != 160500615:
        failures.append(f"backup totalBytes mismatch: {backup.get('totalBytes')} != 160500615")
    if backup.get("diffCount") != 0:
        failures.append(f"backup diffCount mismatch: {backup.get('diffCount')} != 0")
    if backup.get("manifestSha256") != "83E6EF0DFB8B3CE5A29E8A55C7F02A8DD40A3C6E8A1BAD5826A0722E4496C0B1":
        failures.append("backup manifest hash mismatch")

    require_doc_tokens(
        PUBLIC_NOTE,
        (
            "Wave580 IScript Camera/Objective Static Read-Back",
            "IScript__Create3PointPanCamera",
            "IScript__SecondaryObjectiveFailed",
            "2939/6093 = 48.24%",
            "runtime mission-script behavior remains unproven",
            "script corpus coverage remains unproven",
        ),
        failures,
    )
    require_doc_tokens(
        ISCRIPT_DOC,
        (
            "Wave580 Static Read-Back",
            "IScript__Create4PointPanCamera",
            "DAT_008a9b2c",
            "0x005345d0",
        ),
        failures,
    )
    require_doc_tokens(
        FUNCTION_INDEX,
        (
            "Wave580",
            "IScript__Create3PointPanCamera",
            "0x005345d0 IScript__GetVectorLength",
        ),
        failures,
    )
    require_doc_tokens(
        GHIDRA_REFERENCE,
        (
            "MissionScript IScript Camera/Objective Handlers",
            "Wave580",
            "CPanCamera__ctor",
            "2939/6093 = 48.24%",
        ),
        failures,
    )
    require_doc_tokens(
        CAMPAIGN,
        (
            "Wave 580: IScript Camera/Objective Command Handlers",
            "5454",
            "strict clean-signature proxy `2890/6093 = 47.43%`",
        ),
        failures,
    )
    require_doc_tokens(BACKLOG, ("Ghidra IScript camera/objective Wave580", "160500615", "83E6EF0D"), failures)
    require_tokens("ledger", read_text(LEDGER), ("iscript_camera_objective Wave580", "0x00533b70,0x00533eb0", "strict clean-signature proxy 2890/6093 = 47.43%"), failures)
    require_tokens("attempt_log", read_text(ATTEMPT_LOG), ('"attempt_id":20235', "iscript_camera_objective Wave580", "Post-Wave580 queue telemetry"), failures)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Run validation checks")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()
    failures = run_check()
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failureCount": len(failures),
        "failures": failures,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave580 IScript camera/objective probe: {result['status']}")
        for failure in failures:
            print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
