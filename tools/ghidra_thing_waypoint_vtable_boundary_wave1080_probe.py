#!/usr/bin/env python3
"""Validate Wave1080 Thing/Waypoint vtable-boundary read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1080-tga-image-table-residual-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_thing_waypoint_vtable_boundary_wave1080_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
WAYPOINT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WaypointManager.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-095224_post_wave1080_thing_waypoint_vtable_boundary_verified"

TARGETS = {
    "0x004013f0": (
        "SharedVFunc__ReturnColorFF000080_004013f0",
        "int __thiscall SharedVFunc__ReturnColorFF000080_004013f0(void * this)",
        ("0xff000080", "CThing/CWaypoint", "CInfantryAI"),
    ),
    "0x00401400": (
        "SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400",
        "float __thiscall SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400(void * this)",
        ("this+0x28", "0x005d8568", "vtable slot +0x18"),
    ),
    "0x004014d0": (
        "SharedVFunc__ReturnField64Offset10OrMinusOne_004014d0",
        "int __thiscall SharedVFunc__ReturnField64Offset10OrMinusOne_004014d0(void * this)",
        ("this+0x64+0x10", "returns -1", "CInfantryAI"),
    ),
    "0x004014f0": (
        "SharedVFunc__ReturnField68_004014f0",
        "void * __thiscall SharedVFunc__ReturnField68_004014f0(void * this)",
        ("this+0x68", "CThing/CWaypoint", "CInfantryAI"),
    ),
    "0x00401500": (
        "SharedVFunc__ReturnField64Offset14OrZero_00401500",
        "int __thiscall SharedVFunc__ReturnField64Offset14OrZero_00401500(void * this)",
        ("this+0x64+0x14", "returns zero", "CThing/CWaypoint"),
    ),
    "0x004040a0": (
        "SharedVFunc__CopyVector14ToOut_004040a0",
        "void __thiscall SharedVFunc__CopyVector14ToOut_004040a0(void * this, void * out_vec4)",
        ("this+0x14", "RET 0x4", "output buffer"),
    ),
    "0x004040d0": (
        "SharedVFunc__CopyBlock34ToOut_004040d0",
        "void __thiscall SharedVFunc__CopyBlock34ToOut_004040d0(void * this, void * out_block30)",
        ("0x30 bytes", "this+0x34", "output buffer"),
    ),
    "0x00405910": (
        "SharedVFunc__ReturnMinusOne_00405910",
        "int __thiscall SharedVFunc__ReturnMinusOne_00405910(void * this)",
        ("returns -1", "CThing-family", "CInfantryAI"),
    ),
    "0x00405920": (
        "SharedVFunc__ReturnOneRet4_00405920",
        "int __thiscall SharedVFunc__ReturnOneRet4_00405920(void * this, void * unused_arg)",
        ("returns one", "RET 0x4", "CThing-family"),
    ),
    "0x004bfb50": (
        "CWaypoint__GetClassNameString_004bfb50",
        "char * __thiscall CWaypoint__GetClassNameString_004bfb50(void * this)",
        ("0x00630c58", "CWaypoint", "constant-string"),
    ),
    "0x004bfb60": (
        "CWaypoint__SetThingTypeMask1001_004bfb60",
        "void __thiscall CWaypoint__SetThingTypeMask1001_004bfb60(void * this, int type_mask)",
        ("0x1001", "this+0x34", "RET 0x4"),
    ),
    "0x004f3460": (
        "CThing__GetClassNameString_004f3460",
        "char * __thiscall CThing__GetClassNameString_004f3460(void * this)",
        ("0x00633174", "CThing", "constant-string"),
    ),
    "0x004f3470": (
        "CThing__SetThingTypeMaskOr1_004f3470",
        "void __thiscall CThing__SetThingTypeMaskOr1_004f3470(void * this, int type_mask)",
        ("low byte", "this+0x34", "RET 0x4"),
    ),
    "0x0052db60": (
        "CWaypoint__GetTypeId12_0052db60",
        "int __thiscall CWaypoint__GetTypeId12_0052db60(void * this)",
        ("returns constant 0x12", "0x0052db70", "CWaypoint"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "thing-waypoint-vtable-boundary-wave1080",
    "wave1080-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "signature-hardened",
    "comment-hardened",
    "vtable-slot",
    "thing-family",
}

DOC_TOKENS = (
    "Wave1080",
    "thing-waypoint-vtable-boundary-wave1080",
    "0x004013f0 SharedVFunc__ReturnColorFF000080_004013f0",
    "0x00401400 SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400",
    "0x004040a0 SharedVFunc__CopyVector14ToOut_004040a0",
    "0x004bfb50 CWaypoint__GetClassNameString_004bfb50",
    "0x004f3460 CThing__GetClassNameString_004f3460",
    "0x0052db60 CWaypoint__GetTypeId12_0052db60",
    "0x005df550",
    "0x005dd278",
    "0x005dbf14",
    "812/1408 = 57.67%",
    "1387/1560 = 88.91%",
    "500/500 = 100.00%",
    "6276/6276 = 100.00%",
    BACKUP_PATH,
    "boundary recovery",
)

OVERCLAIM_TOKENS = (
    "runtime object behavior proven",
    "runtime waypoint behavior proven",
    "runtime cthing behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-vtable-slots.tsv": 60,
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 178,
        "pre-instructions.tsv": 3,
        "pre-decompile/index.tsv": 3,
        "pre-true-vtable-slots.tsv": 240,
        "pre-true-code-metadata.tsv": 31,
        "pre-true-code-xrefs.tsv": 979,
        "pre-true-code-instructions-around.tsv": 3379,
        "pre-vtable-type-candidates.tsv": 2232,
        "post-metadata.tsv": 14,
        "post-tags.tsv": 14,
        "post-xrefs.tsv": 584,
        "post-instructions.tsv": 67,
        "post-decompile/index.tsv": 14,
        "post-true-vtable-slots.tsv": 240,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    strings = {
        "string-00633174.tsv": "CThing",
        "string-00630c58.tsv": "CWaypoint",
        "string-00622c60.tsv": "CActor",
    }
    for relative, expected in strings.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    pre_missing = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-true-code-metadata.tsv")}
    for address in TARGETS:
        row = pre_missing.get(address)
        require(row is not None and row.get("status") == "MISSING", f"pre metadata did not show missing target: {address}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave1080", "Static retail Ghidra", *comment_tokens):
                require(token in row.get("comment", ""), f"missing metadata comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index row for {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    slot_rows = read_tsv(BASE / "post-true-vtable-slots.tsv")
    resolved = [row for row in slot_rows if normalize_address(row.get("pointer_addr", "")) in TARGETS]
    unresolved = [row for row in slot_rows if row.get("status") != "OK"]
    require(len(resolved) == 32, "resolved Wave1080 vtable-slot occurrence count mismatch", failures)
    require(len(unresolved) == 40, "deferred unresolved true-vtable-slot count mismatch", failures)
    for row in resolved:
        address = normalize_address(row.get("pointer_addr", ""))
        require(row.get("function_name") == TARGETS[address][0], f"slot function name mismatch at {address}", failures)
        require(row.get("status") == "OK", f"slot status mismatch at {address}", failures)

    instruction_text = "\n".join(
        f"{row.get('instruction_addr')} {row.get('mnemonic')} {row.get('operands')}" for row in read_tsv(BASE / "post-instructions.tsv")
    )
    for token in (
        "0x004013f0 MOV EAX, 0xff000080",
        "0x00401409 JMP dword ptr [EAX + 0x18]",
        "0x004040ac MOV dword ptr [EDX], ESI",
        "0x004bfb50 MOV EAX, 0x630c58",
        "0x004f3460 MOV EAX, 0x633174",
        "0x0052db60 MOV EAX, 0x12",
    ):
        require(token in instruction_text, f"missing post-instruction token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=14 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=14 skipped=0 created=14 would_create=0 renamed=0 would_rename=0 signature_updated=14 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=14 found=14 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=14 missing=0",
        "post-xrefs.log": "Wrote 584 rows",
        "post-instructions.log": "Wrote 67 function-body instruction rows",
        "post-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "post-true-vtable-slots.log": "rows=240",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADNAME:", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    quality_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1080.log")
    queue_text = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1080_queue_probe.log")
    require("total_functions=6276 commented_functions=6276" in quality_text, "quality refresh token mismatch", failures)
    require("Total functions: 6276" in queue_text, "queue probe total mismatch", failures)
    require("Commentless functions: 0" in queue_text, "queue probe commentless mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6276, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "queue param_N mismatch", failures)
    require(quality["legacyWeakNameCount"] == 0, "queue weak-name mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "queue uncertain-owner mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6276, "quality TSV row count mismatch", failures)
    require(commented == 6276, "quality TSV commented mismatch", failures)
    require(strict_clean == 6276, "quality TSV strict-clean mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174787463, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        THING_DOC,
        WAYPOINT_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1080-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1080 --check",
        "missing Wave1080 cumulative recheck script",
        failures,
    )
    require(
        scripts.get("test:ghidra-thing-waypoint-vtable-boundary-wave1080")
        == r"py -3 tools\ghidra_thing_waypoint_vtable_boundary_wave1080_probe.py --check",
        "missing Wave1080 focused package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1080 Thing/Waypoint vtable boundary" for row in ledger_rows), "missing Wave1080 ledger row", failures)
    require(
        any(row.get("task") == "Wave1080 Thing/Waypoint vtable boundary" and row.get("attempt_id") == 20662 for row in attempts),
        "missing Wave1080 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1080 Thing/Waypoint vtable boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1080 Thing/Waypoint vtable boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
