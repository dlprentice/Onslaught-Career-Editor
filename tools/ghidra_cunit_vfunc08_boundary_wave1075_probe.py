#!/usr/bin/env python3
"""Validate Wave1075 CUnit vfunc08 boundary read-back artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1075-raw-boundary-candidate"
TARGET = "0x004dfa40"
TARGET_NAME = "CUnit__VFunc08_InitAndAddToWorld"
TARGET_SIGNATURE = "void __thiscall CUnit__VFunc08_InitAndAddToWorld(void * this, void * init)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified"

CORE_DOCS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "release" / "readiness" / "ghidra_cunit_vfunc08_boundary_wave1075_2026-06-02.md",
    ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1075_recheck_2026-06-02.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md",
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

COMMON_TAGS = {
    "static-reaudit",
    "cunit-vfunc08-boundary-wave1075",
    "wave1075-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "cunit",
    "vtable-slot",
    "unit-init",
    "world-occupancy",
    "static-shadow",
    "signature-hardened",
    "comment-hardened",
}

DOC_TOKENS = (
    "Wave1075",
    "cunit-vfunc08-boundary-wave1075",
    "0x004dfa40 CUnit__VFunc08_InitAndAddToWorld",
    "0x005dfd40",
    "0x005dfd60",
    "0x004dfa47",
    "0x004dfa9a",
    "0x004dfaa0",
    "CUnit__Init",
    "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
    "812/1408 = 57.67%",
    "1359/1560 = 87.12%",
    "500/500 = 100.00%",
    "6248/6248 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime init/add-to-world behavior proven",
    "exact source virtual name proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
    "all systems complete",
)


def norm(address: str) -> str:
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
        "pre-diagnose.tsv": 1,
        "pre-metadata.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 161,
        "pre-decompile/index.tsv": 1,
        "context-diagnose.tsv": 6,
        "context-metadata.tsv": 6,
        "context-xrefs.tsv": 24,
        "context-instructions.tsv": 438,
        "context-decompile/index.tsv": 6,
        "pointer-005dfd40.tsv": 64,
        "pointer-00622680.tsv": 64,
        "post-diagnose.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-body-instructions.tsv": 23,
        "post-decompile/index.tsv": 1,
        "post-vtable-slots.tsv": 64,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_diag = {norm(row["address"]): row for row in read_tsv(BASE / "context-diagnose.tsv")}
    require(pre_diag[TARGET]["status"] == "INSTRUCTION_NO_FUNCTION", "pre 0x004dfa40 should be no-function", failures)
    require(pre_diag["0x004dfa47"]["status"] == "INSTRUCTION_NO_FUNCTION", "pre 0x004dfa47 should be no-function", failures)

    pre_xrefs = read_tsv(BASE / "context-xrefs.tsv")
    require(any(norm(row["target_addr"]) == TARGET and norm(row["from_addr"]) == "0x005dfd60" and row["ref_type"] == "DATA" for row in pre_xrefs), "missing pre DATA xref from vtable slot", failures)
    require(any(norm(row["target_addr"]) == "0x004dfa47" and row["from_addr"] == "<none>" for row in pre_xrefs), "0x004dfa47 should have no direct xref", failures)

    pointer_rows = read_tsv(BASE / "pointer-005dfd40.tsv")
    require(any(row["slot"] == "8" and norm(row["entry_addr"]) == "0x005dfd60" and norm(row["ptr"]) == TARGET for row in pointer_rows), "pointer table slot 8 mismatch", failures)

    post_meta = read_tsv(BASE / "post-metadata.tsv")[0]
    require(norm(post_meta["address"]) == TARGET, "post metadata address mismatch", failures)
    require(post_meta["name"] == TARGET_NAME, "post metadata name mismatch", failures)
    require(post_meta["signature"] == TARGET_SIGNATURE, "post signature mismatch", failures)
    for token in ("Wave1075 boundary recovery", "0x005dfd40", "0x005dfd60", "CUnit__Init", "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk", "separate proof"):
        require(token in post_meta.get("comment", ""), f"missing post comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(COMMON_TAGS.issubset(tags), f"post tags missing: {COMMON_TAGS - tags}", failures)

    post_xref = read_tsv(BASE / "post-xrefs.tsv")[0]
    require(norm(post_xref["target_addr"]) == TARGET, "post xref target mismatch", failures)
    require(norm(post_xref["from_addr"]) == "0x005dfd60", "post xref from mismatch", failures)
    require(post_xref["ref_type"] == "DATA", "post xref type mismatch", failures)

    body = read_tsv(BASE / "post-body-instructions.tsv")
    require(body[0]["instruction_addr"] == "0x004dfa40", "post body start mismatch", failures)
    require(body[-1]["instruction_addr"] == "0x004dfa9a", "post body end mismatch", failures)
    require(all(row["function_name"] == TARGET_NAME for row in body), "post body function name mismatch", failures)
    require(not any(row["instruction_addr"] == "0x004dfaa0" for row in body), "post body absorbed next function", failures)

    decompile = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decompile["name"] == TARGET_NAME, "post decompile name mismatch", failures)
    require(decompile["signature"] == TARGET_SIGNATURE, "post decompile signature mismatch", failures)
    require(decompile["status"] == "OK", "post decompile status mismatch", failures)

    slot = next(row for row in read_tsv(BASE / "post-vtable-slots.tsv") if row["slot_index"] == "8")
    require(norm(slot["pointer_addr"]) == TARGET, "post vtable pointer mismatch", failures)
    require(slot["function_name"] == TARGET_NAME, "post vtable function mismatch", failures)
    require(slot["status"] == "OK", "post vtable status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-body-instructions.log": "Wrote 23 function-body instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=64",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6248, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    by_address = {norm(row["address"]): row for row in rows}
    require(len(rows) == 6248, "quality TSV row count mismatch", failures)
    require(strict_clean_count(rows) == 6248, "strict clean count mismatch", failures)
    require(by_address.get(TARGET, {}).get("name") == TARGET_NAME, "quality target name mismatch", failures)
    require(by_address.get(TARGET, {}).get("signature") == TARGET_SIGNATURE, "quality target signature mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174721927 or backup.get("totalBytes") == 174721927.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in CORE_DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-cunit-vfunc08-boundary-wave1075") == r"py -3 tools\ghidra_cunit_vfunc08_boundary_wave1075_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1075-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1075 --check", "missing aggregate package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1075 CUnit vfunc08 boundary" for row in ledger_rows), "missing Wave1075 ledger row", failures)
    require(any(row.get("task") == "Wave1075 CUnit vfunc08 boundary" and row.get("attempt_id") == 20657 for row in attempts), "missing Wave1075 attempt row", failures)


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
        print("Wave1075 CUnit vfunc08 boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1075 CUnit vfunc08 boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
