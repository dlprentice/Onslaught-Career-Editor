#!/usr/bin/env python3
"""Validate Wave1048 CUnit tail linked-vfunc read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1048-cunit-tail-linked-vfunc-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cunit_tail_linked_vfunc_review_wave1048_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1048_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-131919_post_wave1048_cunit_tail_linked_vfunc_review_verified"

FORWARDER_SIG = "int __thiscall {name}(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)"

TARGETS = {
    "0x004fce40": {
        "name": "CUnit__ForwardAttachedNodeVFunc14IfPresent",
        "signature": FORWARDER_SIG.format(name="CUnit__ForwardAttachedNodeVFunc14IfPresent"),
        "comment_tokens": ("this+0x208", "+0x14", "RET 0x10", "0x0044610a"),
        "tag_tokens": ("unit-attached-node-forwarders-wave838", "wave838-readback-verified", "vfunc-14"),
        "calls": 6,
        "data": 0,
    },
    "0x004fce80": {
        "name": "CUnit__ForwardAttachedNodeVFunc18IfPresent",
        "signature": FORWARDER_SIG.format(name="CUnit__ForwardAttachedNodeVFunc18IfPresent"),
        "comment_tokens": ("this+0x208", "+0x18", "0x0047a38a", "RET 0x10"),
        "tag_tokens": ("unit-attached-node-forwarders-wave838", "wave838-readback-verified", "vfunc-18"),
        "calls": 6,
        "data": 0,
    },
    "0x004fcec0": {
        "name": "CUnit__ForwardAttachedNodeVFunc1CIfPresent",
        "signature": FORWARDER_SIG.format(name="CUnit__ForwardAttachedNodeVFunc1CIfPresent"),
        "comment_tokens": ("this+0x208", "+0x1c", "CSquadNormal", "RET 0x10"),
        "tag_tokens": ("unit-attached-node-forwarders-wave838", "wave838-readback-verified", "vfunc-1c"),
        "calls": 7,
        "data": 0,
    },
    "0x004fd5e0": {
        "name": "CUnit__VFunc26_GetRecentSegmentDamageMeter",
        "signature": "int __thiscall CUnit__VFunc26_GetRecentSegmentDamageMeter(void * this, int segment_index)",
        "comment_tokens": ("+0x170", "this+0x210", "+0x214", "0..100"),
        "tag_tokens": ("unit-support-tail-wave540", "unit-vfunc-slot-26"),
        "calls": 1,
        "data": 32,
    },
    "0x004fd6a0": {
        "name": "CUnit__VFunc22_ActivateLinkedTargetsAndChildren",
        "signature": "void __fastcall CUnit__VFunc22_ActivateLinkedTargetsAndChildren(void * this)",
        "comment_tokens": ("this+0x214", "this+0x148", "this+0x19c", "+0x58"),
        "tag_tokens": ("unit-support-tail-wave540", "unit-vfunc-slot-22"),
        "calls": 3,
        "data": 28,
    },
    "0x004fd700": {
        "name": "CUnit__VFunc23_DeactivateLinkedTargetsAndChildren",
        "signature": "void __fastcall CUnit__VFunc23_DeactivateLinkedTargetsAndChildren(void * this)",
        "comment_tokens": ("this+0x214", "this+0x148", "this+0x19c", "+0x5c"),
        "tag_tokens": ("unit-support-tail-wave540", "unit-vfunc-slot-23"),
        "calls": 1,
        "data": 32,
    },
}

VTABLE_EXPECTATIONS = {
    ("0x005d8d1c", "98"): "0x004fd5e0",
    ("0x005d8d1c", "124"): "0x004fd6a0",
    ("0x005d8d1c", "125"): "0x004fd700",
    ("0x005e0b30", "22"): "0x004fd6a0",
    ("0x005e0b30", "23"): "0x004fd700",
    ("0x005e297c", "22"): "0x004fd6a0",
    ("0x005e297c", "23"): "0x004fd700",
    ("0x005e32d4", "22"): "0x004fd6a0",
    ("0x005e32d4", "23"): "0x004fd700",
}

DOC_TOKENS = (
    "Wave1048",
    "cunit-tail-linked-vfunc-review-wave1048",
    "0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent",
    "0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent",
    "0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent",
    "0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter",
    "0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren",
    "0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren",
    "CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex",
    "CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex",
    "0x005d8d1c",
    "0x005e0b30",
    "0x005e297c",
    "0x005e32d4",
    "744/1408 = 52.84%",
    "1002/1509 = 66.40%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 6,
        "tags.tsv": 6,
        "xrefs.tsv": 116,
        "instructions.tsv": 175,
        "decompile/index.tsv": 6,
        "context-metadata.tsv": 10,
        "context-tags.tsv": 10,
        "context-xrefs.tsv": 78,
        "context-instructions.tsv": 596,
        "context-decompile/index.tsv": 10,
        "vtable-slots.tsv": 528,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "xrefs.tsv")
    xref_counts = Counter((normalize_address(row["target_addr"]), row["ref_type"]) for row in xrefs)

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in expected["comment_tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require({"static-reaudit", "retail-binary-evidence"}.issubset(actual_tags), f"common tags missing at {address}", failures)
            for token in expected["tag_tokens"]:
                require(token in actual_tags, f"missing tag at {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(
            xref_counts[(address, "UNCONDITIONAL_CALL")] == expected["calls"],
            f"call xref count mismatch at {address}",
            failures,
        )
        require(xref_counts[(address, "DATA")] == expected["data"], f"DATA xref count mismatch at {address}", failures)

    decompile_tokens = {
        "decompile/004fd5e0_CUnit__VFunc26_GetRecentSegmentDamageMeter.c": (
            "CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex",
            "CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex",
        ),
        "decompile/004fd6a0_CUnit__VFunc22_ActivateLinkedTargetsAndChildren.c": ("+ 0x148", "+ 0x19c", "0x58"),
        "decompile/004fd700_CUnit__VFunc23_DeactivateLinkedTargetsAndChildren.c": ("+ 0x148", "+ 0x19c", "0x5c"),
    }
    for relative, tokens in decompile_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing decompile token in {relative}: {token}", failures)

    vtable_rows = {
        (normalize_address(row["vtable"]), row["slot_index"]): normalize_address(row["pointer_addr"])
        for row in read_tsv(BASE / "vtable-slots.tsv")
    }
    for key, expected_pointer in VTABLE_EXPECTATIONS.items():
        normalized_key = (normalize_address(key[0]), key[1])
        require(vtable_rows.get(normalized_key) == expected_pointer, f"vtable slot mismatch: {key}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=6 found=6 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "xrefs.log": "Wrote 116 rows",
        "instructions.log": "Wrote 175 function-body instruction rows",
        "decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=10 found=10 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "context-xrefs.log": "Wrote 78 rows",
        "context-instructions.log": "Wrote 596 function-body instruction rows",
        "context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=4 rows=528",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save success in {relative}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174590855 or backup.get("totalBytes") == 174590855.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        UNIT_DOC,
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

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cunit-tail-linked-vfunc-review-wave1048")
        == r"py -3 tools\ghidra_cunit_tail_linked_vfunc_review_wave1048_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1048-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1048 --check",
        "missing aggregate package script",
        failures,
    )

    task = "Wave1048 cunit tail linked vfunc review"
    require(any(row.get("task") == task for row in read_jsonl(LEDGER)), "missing Wave1048 ledger row", failures)
    require(any(row.get("task") == task and row.get("attempt_id") == 20630 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave1048 attempt row", failures)


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
        print("Wave1048 CUnit tail linked-vfunc review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1048 CUnit tail linked-vfunc review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
