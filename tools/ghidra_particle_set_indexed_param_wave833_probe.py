#!/usr/bin/env python3
"""Validate Wave833 particle SetIndexedParam read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave833-particle-set-indexed-param"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_particle_set_indexed_param_wave833_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-233838_post_wave833_particle_set_indexed_param_verified"
TARGET_ADDR = "0x004f5b70"
TARGET_NAME = "CParticleDescriptor__SetIndexedParam"
TARGET_SIGNATURE = "void __thiscall CParticleDescriptor__SetIndexedParam(void * this, int field_index, int field_value)"
NEXT_HEAD = "0x004f7d30 FromWCHAR"

COMMON_TAGS = {
    "static-reaudit",
    "particle-set-indexed-param-wave833",
    "wave833-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "particle-descriptor",
    "token-archive",
    "indexed-field-setter",
    "phantom-param-corrected",
    "ret-0x8",
}

COMMENT_TOKENS = (
    "Wave833 static read-back",
    "CParticleDescriptor__SetIndexedParam",
    "ESP+0x4",
    "ESP+0x8",
    "this+0x0c+(field_index*4)",
    "RET 0x8",
    "unused_flags",
    "0x004c57d4",
    "0x004c57e9",
    "CParticleDescriptor__Load",
    "0x004f5b80 CTokenArchive__RegisterReferenceFixup",
)

CORE_ANCHORS = (
    "Wave833 particle SetIndexedParam",
    "particle-set-indexed-param-wave833",
    "0x004f5b70 CParticleDescriptor__SetIndexedParam",
    TARGET_SIGNATURE,
    "unused_flags",
    "RET 0x8",
    "0x004c57d4",
    "0x004c57e9",
    "0x004f5b80 CTokenArchive__RegisterReferenceFixup",
    "5655/6098 = 92.74%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime particle parsing behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
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


def strict_clean_count(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 15,
        "pre-instructions.tsv": 49,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 10,
        "pre-context-decompile/index.tsv": 10,
        "pre-xref-site-instructions.tsv": 315,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 15,
        "post-instructions.tsv": 49,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 10,
        "post-context-decompile/index.tsv": 10,
        "post-xref-site-instructions.tsv": 315,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    row = metadata.get(TARGET_ADDR)
    require(row is not None, "missing target metadata", failures)
    if row is not None:
        require(row.get("name") == TARGET_NAME, "target name mismatch", failures)
        require(row.get("signature") == TARGET_SIGNATURE, "target signature mismatch", failures)
        require(row.get("status") == "OK", "target metadata status mismatch", failures)
        comment = row.get("comment", "")
        for token in COMMENT_TOKENS:
            require(token in comment, f"missing target comment token: {token}", failures)

    tag_row = tags.get(TARGET_ADDR)
    require(tag_row is not None, "missing target tags", failures)
    if tag_row is not None:
        actual_tags = set(tag_row.get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(actual_tags), f"missing target tags: {COMMON_TAGS - actual_tags}", failures)
        require(tag_row.get("status") == "OK", "target tag status mismatch", failures)

    dec = decompile.get(TARGET_ADDR)
    require(dec is not None, "missing target decompile index", failures)
    if dec is not None:
        require(dec.get("signature") == TARGET_SIGNATURE, "decompile signature mismatch", failures)
        require(dec.get("status") == "OK", "decompile status mismatch", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    actual_xrefs = {normalize_address(row["from_addr"]) for row in xrefs}
    for expected in ("0x004c57d4", "0x004c57e9", "0x004c538e", "0x004c06a0", "0x004c217a", "0x004c3254"):
        require(expected in actual_xrefs, f"missing xref from {expected}", failures)

    site_text = read_text(BASE / "post-xref-site-instructions.tsv")
    for token in (
        "PUSH\tEAX",
        "PUSH\tECX",
        "MOV\tECX, EDI",
        "CALL\t0x004f5b70",
        "LEA\tEAX, [ESI + 0x6c]",
        "LEA\tEDX, [ESI + 0x70]",
        "LEA\tEDX, [EDI + 0x5c]",
    ):
        require(token in site_text, f"missing xref-site token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 15 rows",
        "post-instructions.log": "Wrote 49 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-xref-site-instructions.log": "Wrote 315 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5655",
        "queue-probe.log": "Commentless functions: 443",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave833.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave833_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BAD:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 443, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(not queue["priorityQueues"]["commentlessHighSignal"], "high-signal queue should be empty", failures)
    require(not queue["priorityQueues"]["signature"], "signature queue should be empty", failures)
    require(not queue["priorityQueues"]["nameConfidence"], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5655, "quality TSV commented count mismatch", failures)
    require(strict_clean_count(rows) == 5655, "strict clean count mismatch", failures)
    require(raw is not None and raw.get("address") == "0x004f7d30", "raw commentless head mismatch", failures)
    require(raw is not None and raw.get("name") == "FromWCHAR", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171772807 or backup.get("totalBytes") == 171772807.0, "backup byte count mismatch", failures)
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
        PARTICLE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-particle-set-indexed-param-wave833")
        == r"py -3 tools\ghidra_particle_set_indexed_param_wave833_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave833 particle SetIndexedParam" for row in ledger_rows), "missing Wave833 ledger row", failures)
    require(
        any(row.get("task") == "Wave833 particle SetIndexedParam" and row.get("attempt_id") == 20488 for row in attempts),
        "missing Wave833 attempt row",
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
        print("Wave833 particle SetIndexedParam probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave833 particle SetIndexedParam probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
