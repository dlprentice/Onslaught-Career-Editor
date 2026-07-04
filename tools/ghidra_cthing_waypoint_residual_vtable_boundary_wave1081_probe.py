#!/usr/bin/env python3
"""Validate Wave1081 CThing/Waypoint residual vtable-boundary artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1081-cthing-waypoint-residual-vtable-boundary"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cthing_waypoint_residual_vtable_boundary_wave1081_2026-06-02.md"
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

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-103048_post_wave1081_cthing_waypoint_residual_vtable_boundary_verified"
WAVE_TAG = "cthing-waypoint-residual-vtable-boundary-wave1081"

TARGETS = {
    "0x004bfa00": (
        "SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00",
        "void __thiscall SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00(void * this, void * out_block30)",
        ("0x00829dd0", "0x30 bytes", "slot +0x04"),
    ),
    "0x004bfa20": (
        "SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa20",
        "void __thiscall SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa20(void * this, void * out_block30)",
        ("0x00829dd0", "0x30 bytes", "slot +0x88"),
    ),
    "0x004bfa40": (
        "SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa40",
        "void __thiscall SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa40(void * this, void * out_block30)",
        ("0x00829dd0", "0x30 bytes", "slot +0xf4"),
    ),
    "0x004f3760": (
        "CThing__AddShutdownEvent_004f3760",
        "void __thiscall CThing__AddShutdownEvent_004f3760(void * this)",
        ("this+0x2c bit 0x1", "0x0044b370", "0x7d0"),
    ),
    "0x004f37a0": (
        "CThing__StartDieProcess_004f37a0",
        "int __thiscall CThing__StartDieProcess_004f37a0(void * this)",
        ("this+0x2c bit 0x4", "vtable slot +0x38", "StartDieProcess"),
    ),
    "0x004f3d20": (
        "SharedVFunc__ForwardField28Slot10OrNull_004f3d20",
        "void * __thiscall SharedVFunc__ForwardField28Slot10OrNull_004f3d20(void * this)",
        ("this+0x28", "vtable slot +0x10", "CInfantryAI"),
    ),
    "0x0043e9c0": (
        "SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0",
        "void __thiscall SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0(void * this, void * out_block10)",
        ("0x0066ea10", "0x0066ea1c", "CThing__GetRenderPos"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    WAVE_TAG,
    "wave1081-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "signature-hardened",
    "comment-hardened",
    "vtable-slot",
    "thing-family",
}

EXPECTED_XREF_COUNTS = {
    "0x0043e9c0": 19,
    "0x004bfa00": 2,
    "0x004bfa20": 3,
    "0x004bfa40": 3,
    "0x004f3760": 3,
    "0x004f37a0": 3,
    "0x004f3d20": 62,
}

EXPECTED_BODY_COUNTS = {
    "0x0043e9c0": ("0x0043e9e9", 11),
    "0x004bfa00": ("0x004bfa16", 10),
    "0x004bfa20": ("0x004bfa36", 10),
    "0x004bfa40": ("0x004bfa56", 10),
    "0x004f3760": ("0x004f3793", 18),
    "0x004f37a0": ("0x004f37bb", 11),
    "0x004f3d20": ("0x004f3d2e", 7),
}

EXPECTED_VTABLE_ROWS = {
    ("005df550", "1", "0x004bfa00"),
    ("005df550", "21", "0x004f3d20"),
    ("005df550", "34", "0x004bfa20"),
    ("005df550", "44", "0x004f3760"),
    ("005df550", "57", "0x0043e9c0"),
    ("005df550", "61", "0x004bfa40"),
    ("005df550", "80", "0x004f37a0"),
    ("005dd278", "1", "0x004bfa00"),
    ("005dd278", "21", "0x004f3d20"),
    ("005dd278", "34", "0x004bfa20"),
    ("005dd278", "44", "0x004f3760"),
    ("005dd278", "57", "0x0043e9c0"),
    ("005dd278", "61", "0x004bfa40"),
    ("005dd278", "80", "0x004f37a0"),
    ("005dbf14", "70", "0x004f3d20"),
}

DOC_TOKENS = (
    "Wave1081",
    WAVE_TAG,
    "0x004bfa00 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00",
    "0x004f3760 CThing__AddShutdownEvent_004f3760",
    "0x004f37a0 CThing__StartDieProcess_004f37a0",
    "0x004f3d20 SharedVFunc__ForwardField28Slot10OrNull_004f3d20",
    "0x0043e9c0 SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0",
    "0x005df550",
    "0x005dd278",
    "0x005dbf14",
    "812/1408 = 57.67%",
    "1394/1560 = 89.36%",
    "500/500 = 100.00%",
    "6283/6283 = 100.00%",
    BACKUP_PATH,
    "boundary recovery",
)

OVERCLAIM_TOKENS = (
    "runtime object behavior proven",
    "runtime waypoint behavior proven",
    "runtime event delivery proven",
    "runtime death-process behavior proven",
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
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 95,
        "pre-instructions-around.tsv": 399,
        "pre-decompile/index.tsv": 7,
        "pre-vtable-slots.tsv": 288,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 95,
        "post-instructions.tsv": 77,
        "post-decompile/index.tsv": 7,
        "post-vtable-slots.tsv": 288,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_missing = {normalize_address(row["address"]) for row in read_tsv(BASE / "pre-metadata.tsv") if row.get("status") == "MISSING"}
    require(pre_missing == set(TARGETS), "pre metadata missing-target set mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave1081", "vtable-boundary recovery", "Static retail Ghidra") + comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_counts: dict[str, int] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        target = normalize_address(row["target_addr"])
        xref_counts[target] = xref_counts.get(target, 0) + 1
        require(row.get("ref_type") == "DATA", f"non-DATA xref at {target}", failures)
    require(xref_counts == EXPECTED_XREF_COUNTS, "post xref counts mismatch", failures)

    body_rows_by_target: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(BASE / "post-instructions.tsv"):
        body_rows_by_target.setdefault(normalize_address(row["target_addr"]), []).append(row)
    for address, (last_addr, expected_count) in EXPECTED_BODY_COUNTS.items():
        rows = body_rows_by_target.get(address, [])
        require(len(rows) == expected_count, f"instruction count mismatch at {address}", failures)
        if rows:
            require(rows[-1].get("instruction_addr") == last_addr, f"last instruction mismatch at {address}", failures)
            require(rows[-1].get("flow_type") == "TERMINATOR", f"last instruction is not terminator at {address}", failures)

    pre_status = {row["status"] for row in read_tsv(BASE / "pre-vtable-slots.tsv")}
    post_slots = read_tsv(BASE / "post-vtable-slots.tsv")
    post_status_counts: dict[str, int] = {}
    for row in post_slots:
        post_status_counts[row["status"]] = post_status_counts.get(row["status"], 0) + 1
    require(pre_status == {"OK", "NO_FUNCTION_AT_POINTER"}, "pre vtable status set mismatch", failures)
    require(post_status_counts == {"OK": 259, "NO_FUNCTION_AT_POINTER": 29}, "post vtable status counts mismatch", failures)

    post_slot_lookup = {
        (row["vtable"], row["slot_index"], normalize_address(row["pointer_addr"])): row
        for row in post_slots
    }
    for key in EXPECTED_VTABLE_ROWS:
        row = post_slot_lookup.get(key)
        require(row is not None, f"missing recovered vtable row: {key}", failures)
        if row is not None:
            expected_name = TARGETS[key[2]][0]
            require(row.get("status") == "OK", f"recovered vtable row not OK: {key}", failures)
            require(row.get("function_name") == expected_name, f"recovered vtable name mismatch: {key}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 created=7 would_create=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 95 rows",
        "post-instructions.log": "Wrote 77 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=3 rows=288",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save report in {relative}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6283, "queue total mismatch", failures)
    for key in (
        "legacyWeakNameCount",
        "commentlessFunctionCount",
        "undefinedSignatureCount",
        "paramSignatureCount",
        "uncertainOwnerNameCount",
        "helperAddressNameCount",
        "wrapperAddressNameCount",
    ):
        require(quality.get(key) == 0, f"queue quality signal not zero: {key}", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6283, "quality TSV row count mismatch", failures)
    require(commented == 6283, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6283, "quality TSV strict-clean count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (174787463, 174787463.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
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
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cthing-waypoint-residual-vtable-boundary-wave1081")
        == r"py -3 tools\ghidra_cthing_waypoint_residual_vtable_boundary_wave1081_probe.py --check",
        "missing package focused script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1081-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1081 --check",
        "missing package aggregate script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1081 CThing/Waypoint residual vtable boundary" for row in ledger_rows), "missing Wave1081 ledger row", failures)
    require(any(row.get("task") == "Wave1081 CThing/Waypoint residual vtable boundary" for row in attempts), "missing Wave1081 attempt row", failures)


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
        print("Wave1081 CThing/Waypoint residual vtable-boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1081 CThing/Waypoint residual vtable-boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
