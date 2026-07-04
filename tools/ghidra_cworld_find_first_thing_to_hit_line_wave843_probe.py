#!/usr/bin/env python3
"""Validate Wave843 CWorld FindFirstThingToHitLine read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave843-oid-trace-line-target-hit"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cworld_find_first_thing_to_hit_line_wave843_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WORLD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

ADDRESS = "0x0050b030"
OLD_NAME = "OID__TraceLineAndSelectBestTargetHit"
NAME = "CWorld__FindFirstThingToHitLine"
SIGNATURE = (
    "int __thiscall CWorld__FindFirstThingToHitLine(void * this, undefined4 line_00, undefined4 line_04, "
    "undefined4 line_08, undefined4 line_0c, undefined4 line_10, undefined4 line_14, undefined4 line_18, "
    "undefined4 line_1c, undefined4 line_20, undefined4 line_24, undefined4 line_28, undefined4 line_2c, "
    "undefined4 line_30, void * ignored_owner, void * hit_result, int stop_on_first_valid_hit, "
    "int child_trace_mode, int collision_mode, uint reject_flags, int heightfield_trace_flags, "
    "uint required_thing_flags)"
)
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-043624_post_wave843_cworld_find_first_thing_to_hit_line_verified"
NEXT_HEAD = "0x0050b9c0 CWorld__LoadWorld"

EXPECTED_TAGS = {
    "static-reaudit",
    "cworld-find-first-thing-to-hit-line-wave843",
    "wave843-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "rename-applied",
    "cworld",
    "line-trace",
    "mapwho",
    "heightfield",
    "thiscall-ret54",
}

CORE_DOC_TOKENS = (
    "Wave843 CWorld FindFirstThingToHitLine",
    "cworld-find-first-thing-to-hit-line-wave843",
    "0x0050b030 CWorld__FindFirstThingToHitLine",
    SIGNATURE,
    "OID__TraceLineAndSelectBestTargetHit",
    "WORLD.FindFirstThingToHitLine",
    "DAT_00855090",
    "RET 0x54",
    "0x34-byte by-value CLine-style stack copy",
    "CHeightField__TraceLineAgainstHeightfield",
    "CMapWho__GetFirstEntryWithinLine",
    "CMapWho__GetNextEntryWithinLine",
    "CThing__GetPersistentCollisionSeekingThing",
    "5667/6098 = 92.93%",
    NEXT_HEAD,
    BACKUP_PATH,
)

COMMENT_TOKENS = (
    "Wave843 static read-back/signature/comment hardening",
    "renamed from OID__TraceLineAndSelectBestTargetHit",
    "WORLD.FindFirstThingToHitLine",
    "DAT_00855090",
    "RET 0x54",
    "0x34-byte by-value CLine-style stack copy",
    "CHeightField__TraceLineAgainstHeightfield",
    "CMapWho__GetFirstEntryWithinLine",
    "CMapWho__GetNextEntryWithinLine",
    "CThing__GetPersistentCollisionSeekingThing",
    "stop_on_first_valid_hit",
    "Static retail Ghidra evidence only",
)

EXPECTED_XREFS = {
    "0x0053eafb": "CDXEngine__Render",
    "0x0040bf1d": "CBattleEngine__HandleAutoAim",
    "0x00499cfd": "CMCMech__GetFootHeight",
    "0x0040954e": "CMonitor__Process",
    "0x0040b023": "CBattleEngine__CalcUnitOverCrossHair",
    "0x00426be0": "CCollisionSeekingRound__CreateEffect",
    "0x00507ff0": "OID__CanFireAtTarget_BallisticArcA",
    "0x0050856e": "OID__CanFireAtTarget_BallisticArcA",
    "0x005085d9": "OID__CanFireAtTarget_BallisticArcA",
    "0x00508860": "OID__CanFireAtTarget_BallisticArcA",
    "0x005090ea": "OID__CanFireAtTarget_BallisticArcB",
    "0x004f9d03": "CUnit__ApplyDamage",
}

CONTEXT_NAMES = {
    "vector_constructor_iterator_nothrow",
    "CHeightField__TraceLineAgainstHeightfield",
    "CMapWho__GetFirstEntryWithinLine",
    "CMapWhoEntry__GetOwner",
    "CThing__GetPersistentCollisionSeekingThing",
    "CMapWho__GetNextEntryWithinLine",
    "CWorld__InvokeVtable14WithTempBuffers",
}

OVERCLAIM_TOKENS = (
    "runtime collision/targeting behavior proven",
    "exact cline layout proven",
    "exact cworldlinecolreport layout proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict


def instruction_text(rows: list[dict[str, str]]) -> str:
    return "\n".join(f"{row.get('function_name', '')} {row.get('mnemonic', '')} {row.get('operands', '')}" for row in rows)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 1,
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 121,
        "pre-target-deep-instructions.tsv": 385,
        "pre-target-range-disassembly.tsv": 322,
        "pre-xref-site-instructions.tsv": 1260,
        "pre-decompile/index.tsv": 1,
        "pre-caller-metadata.tsv": 9,
        "pre-caller-instructions.tsv": 1089,
        "pre-caller-decompile/index.tsv": 9,
        "pre-context-metadata.tsv": 7,
        "pre-context-tags.tsv": 7,
        "pre-context-decompile/index.tsv": 7,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 121,
        "post-target-deep-instructions.tsv": 385,
        "post-target-range-disassembly.tsv": 322,
        "post-xref-site-instructions.tsv": 1260,
        "post-decompile/index.tsv": 1,
        "post-caller-metadata.tsv": 9,
        "post-caller-instructions.tsv": 1089,
        "post-caller-decompile/index.tsv": 9,
        "post-context-metadata.tsv": 7,
        "post-context-tags.tsv": 7,
        "post-context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(metadata["address"]) == ADDRESS, "metadata address mismatch", failures)
    require(metadata["name"] == NAME, "metadata name mismatch", failures)
    require(metadata["signature"] == SIGNATURE, f"metadata signature mismatch: {metadata['signature']}", failures)
    require(metadata["status"] == "OK", "metadata status mismatch", failures)
    for token in COMMENT_TOKENS:
        require(token in metadata.get("comment", ""), f"missing comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0]["tags"].split(";"))
    require(EXPECTED_TAGS.issubset(tags), f"missing tags: {EXPECTED_TAGS - tags}", failures)

    xrefs = {normalize_address(row["from_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    for from_addr, function_name in EXPECTED_XREFS.items():
        row = xrefs.get(from_addr)
        require(row is not None, f"missing xref from {from_addr}", failures)
        if row is not None:
            require(normalize_address(row["target_addr"]) == ADDRESS, f"xref target mismatch at {from_addr}", failures)
            require(row["target_name"] == NAME, f"xref target name mismatch at {from_addr}", failures)
            require(row["from_function"] == function_name, f"xref function mismatch at {from_addr}", failures)
            require(row["ref_type"] == "UNCONDITIONAL_CALL", f"xref type mismatch at {from_addr}", failures)

    context_names = {row["name"] for row in read_tsv(BASE / "post-context-metadata.tsv")}
    require(CONTEXT_NAMES.issubset(context_names), f"missing context names: {CONTEXT_NAMES - context_names}", failures)

    body_text = instruction_text(read_tsv(BASE / "post-target-range-disassembly.tsv"))
    for token in (
        "PUSH -0x1",
        "SUB ESP, 0x194",
        "CALL 0x00490a40",
        "CALL 0x00492110",
        "CALL 0x00492c90",
        "CALL 0x004f3d10",
        "CALL 0x004925a0",
        "CALL 0x004780f0",
        "RET 0x54",
        "MOV dword ptr [ECX + 0x8], EAX",
    ):
        require(token in body_text, f"missing body instruction token: {token}", failures)

    caller_text = instruction_text(read_tsv(BASE / "post-xref-site-instructions.tsv"))
    for token in (
        "CDXEngine__Render MOV ECX, 0x855090",
        "CBattleEngine__HandleAutoAim MOV ECX, 0x855090",
        "CBattleEngine__CalcUnitOverCrossHair MOV ECX, 0x855090",
        "CUnit__ApplyDamage MOV ECX, 0x855090",
        "SUB ESP, 0x34",
        "CALL 0x0050b030",
    ):
        require(token in caller_text, f"missing caller instruction token: {token}", failures)

    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")[0]
    require(decompile_index["signature"] == SIGNATURE, "decompile signature mismatch", failures)
    require(decompile_index["status"] == "OK", "decompile status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    initial_apply = read_text(BASE / "apply.log")
    require("READBACK_BAD: 0x0050b030" in initial_apply, "initial auto-this readback guard missing", failures)
    require("void * this, void * world" in initial_apply, "initial auto-this mismatch token missing", failures)
    require("SUMMARY: updated=0 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=1" in initial_apply, "initial readback-bad summary mismatch", failures)

    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-dry2.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply2.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "Wrote 121 instruction rows",
        "post-target-deep-instructions.log": "Wrote 385 instruction rows",
        "post-target-range-disassembly.log": "wrote 322 instruction rows",
        "post-xref-site-instructions.log": "Wrote 1260 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-caller-metadata.log": "targets=9 found=9 missing=0",
        "post-caller-instructions.log": "Wrote 1089 instruction rows",
        "post-caller-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-context-metadata.log": "targets=7 found=7 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-context-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    clean_logs = ("apply-dry.log", "apply-dry2.log", "apply2.log", "apply-final-dry.log")
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        bad_tokens = ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1")
        if relative in clean_logs:
            bad_tokens += ("READBACK_BAD",)
        for bad in bad_tokens:
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    require("READBACK_OK: 0x0050b030" in read_text(BASE / "apply2.log"), "corrected apply readback OK missing", failures)
    quality_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave843.log")
    queue_log = read_text(ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave843_queue_probe.log")
    require("total_functions=6098 commented_functions=5667" in quality_log, "quality refresh count mismatch", failures)
    require("Commentless functions: 431" in queue_log, "queue probe count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 431, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict = signature_counts(rows)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5667, "quality TSV commented count mismatch", failures)
    require(strict == 5667, "quality TSV strict count mismatch", failures)
    require(raw is not None and normalize_address(raw.get("address", "")) == "0x0050b9c0", "raw head address mismatch", failures)
    require(raw is not None and raw.get("name") == "CWorld__LoadWorld", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171871111 or backup.get("totalBytes") == 171871111.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        WORLD_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\ghidra_cworld_find_first_thing_to_hit_line_wave843_probe.py --check"
    require(package.get("scripts", {}).get("test:ghidra-cworld-find-first-thing-to-hit-line-wave843") == expected_script, "missing package script", failures)
    require(any(row.get("task") == "Wave843 CWorld FindFirstThingToHitLine" for row in read_jsonl(LEDGER)), "missing Wave843 ledger row", failures)
    require(any(row.get("task") == "Wave843 CWorld FindFirstThingToHitLine" and row.get("attempt_id") == 20498 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave843 attempt row", failures)


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
        print("Wave843 CWorld FindFirstThingToHitLine probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave843 CWorld FindFirstThingToHitLine probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
