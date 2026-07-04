#!/usr/bin/env python3
"""Validate Wave1078 TerrainGuide vtable review read-back artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1078-terrainguide-vtable-review"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-082337_post_wave1078_terrainguide_vtable_review_verified"
TARGET = "0x004f1ee0"
TARGET_NAME = "CTerrainGuide__VFunc03_UpdateGuidanceState_004f1ee0"
TARGET_SIGNATURE = "void __fastcall CTerrainGuide__VFunc03_UpdateGuidanceState_004f1ee0(void * this)"

COMMON_TAGS = {
    "static-reaudit",
    "terrainguide-vtable-review-wave1078",
    "wave1078-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "terrainguide",
    "vtable-slot",
    "vtable-slot-3",
    "signature-hardened",
    "comment-hardened",
}

DOC_TOKENS = (
    "Wave1078",
    "terrainguide-vtable-review-wave1078",
    "0x004f1ee0 CTerrainGuide__VFunc03_UpdateGuidanceState_004f1ee0",
    "0x005df4ec",
    "0x005df4f8",
    "0x004f2120",
    "0x004f2140 CText__ResetCoreFields",
    "812/1408 = 57.67%",
    "1372/1560 = 87.95%",
    "500/500 = 100.00%",
    "6261/6261 = 100.00%",
    BACKUP_PATH,
)

DOCS = [
    ROOT / "release" / "readiness" / "ghidra_terrainguide_vtable_review_wave1078_2026-06-02.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Guide.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

PACKAGE_JSON = ROOT / "package.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "exact source virtual name proven",
    "all systems complete",
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


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if unescape_tsv(row.get("comment", "")).strip())
    strict_clean = sum(
        1
        for row in rows
        if unescape_tsv(row.get("comment", "")).strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "pre-vtable-slots.tsv": 16,
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 94,
        "pre-instructions-around.tsv": 791,
        "pre-decompile/index.tsv": 7,
        "pre-slot3-wide.tsv": 277,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-body-instructions.tsv": 170,
        "post-decompile/index.tsv": 1,
        "post-vtable-slots.tsv": 16,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    require(pre_metadata.get(TARGET, {}).get("status") == "MISSING", "pre metadata did not record missing target", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    row = metadata.get(TARGET)
    require(row is not None, "missing post metadata row", failures)
    if row is not None:
        comment = row.get("comment", "")
        require(row.get("name") == TARGET_NAME, "post metadata name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, f"post signature mismatch: {row.get('signature')}", failures)
        require(row.get("status") == "OK", "post metadata status mismatch", failures)
        for token in (
            "Wave1078 boundary recovery",
            "0x005df4ec",
            "0x005df4f8",
            "owner+0x14c",
            "0x004f2120",
            "0x004f2140 CText__ResetCoreFields",
            "separate proof",
        ):
            require(token in comment, f"missing comment token: {token}", failures)

    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    tag_row = tags.get(TARGET)
    require(tag_row is not None, "missing post tags row", failures)
    if tag_row is not None:
        actual = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual), f"missing common tags: {COMMON_TAGS - actual}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    require(
        len(xrefs) == 1
        and normalize_address(xrefs[0].get("target_addr", "")) == TARGET
        and normalize_address(xrefs[0].get("from_addr", "")) == "0x005df4f8"
        and xrefs[0].get("ref_type") == "DATA",
        "post xref row mismatch",
        failures,
    )

    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    dec = decompile.get(TARGET)
    require(dec is not None, "missing post decompile row", failures)
    if dec is not None:
        require(dec.get("name") == TARGET_NAME, "decompile name mismatch", failures)
        require(dec.get("signature") == TARGET_SIGNATURE, "decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    vtable_rows = read_tsv(BASE / "post-vtable-slots.tsv")
    slot3 = next((row for row in vtable_rows if row.get("vtable") == "005df4ec" and row.get("slot_index") == "3"), None)
    require(slot3 is not None, "missing post TerrainGuide slot 3 row", failures)
    if slot3 is not None:
        require(slot3.get("slot_addr") == "005df4f8", "slot 3 address mismatch", failures)
        require(slot3.get("function_entry") == "004f1ee0", "slot 3 function entry mismatch", failures)
        require(slot3.get("function_name") == TARGET_NAME, "slot 3 function name mismatch", failures)
        require(slot3.get("status") == "OK", "slot 3 status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0",
        "apply.log": "updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0",
        "apply-final-dry.log": "updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-body-instructions.log": "Wrote 170 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-vtable-slots.log": "targets=1 rows=16",
        "export-functions-quality-wave1078.log": "total_functions=6261 commented_functions=6261",
        "wave1078_queue_probe.log": "Total functions: 6261",
    }
    aliases = {
        "export-functions-quality-wave1078.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1078.log",
        "wave1078_queue_probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave1078_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6261, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["legacyWeakNameCount"] == 0, "legacy weak count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain owner count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6261, "quality TSV row count mismatch", failures)
    require(commented == 6261, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6261, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174754695, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_ledgers(failures: list[str]) -> None:
    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-terrainguide-vtable-review-wave1078")
        == r"py -3 tools\ghidra_terrainguide_vtable_review_wave1078_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1078-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1078 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1078 TerrainGuide vtable review" for row in ledger_rows), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1078 TerrainGuide vtable review" and row.get("attempt_id") == 20660 for row in attempts),
        "missing attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs_and_ledgers(failures)

    if failures:
        print("Wave1078 TerrainGuide vtable review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1078 TerrainGuide vtable review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
