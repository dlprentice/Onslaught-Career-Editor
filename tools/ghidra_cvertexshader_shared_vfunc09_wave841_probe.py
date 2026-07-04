#!/usr/bin/env python3
"""Validate Wave841 shared default/false virtual-slot read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave841-cvertexshader-vfunc09"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cvertexshader_shared_vfunc09_wave841_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
VERTEX_SHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
CONTROLLER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Controller.cpp" / "_index.md"
DESTRUCTABLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DestructableSegmentsController.cpp" / "_index.md"
DXTREES_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTrees.cpp.md"
VBUFTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
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

ADDRESS = "0x005019c0"
NAME = "VFuncSlot_09_005019c0"
SIGNATURE = "int __cdecl VFuncSlot_09_005019c0(void)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-032940_post_wave841_cvertexshader_shared_vfunc09_verified"
NEXT_HEAD = "0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4"

EXPECTED_TAGS = {
    "static-reaudit",
    "cvertexshader-shared-vfunc09-wave841",
    "wave841-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "shared-vfunc",
    "default-false",
    "vtable-slot",
    "cvertexshader",
    "frontend-development",
}

COMMENT_TOKENS = (
    "Wave841 static read-back/signature/comment hardening",
    "shared default/false virtual stub",
    "XOR EAX,EAX; RET",
    "four direct frontend-development callsites",
    "twenty-six DATA pointer slots",
    "CControllerDefinition",
    "CVertexShader",
    "CDXTrees",
    "0x00501a10",
    "runtime behavior",
)

CALL_TARGETS = {
    "0x00458662": ("CALL", "0x005019c0", "JZ"),
    "0x00458a46": ("CALL", "0x005019c0", "JZ"),
    "0x00458d32": ("CALL", "0x005019c0", "JNZ"),
    "0x00458d4f": ("CALL", "0x005019c0", "JZ"),
}

CORE_DOC_TOKENS = (
    "Wave841 Shared Default/False VFunc09",
    "cvertexshader-shared-vfunc09-wave841",
    "0x005019c0 VFuncSlot_09_005019c0",
    SIGNATURE,
    "XOR EAX,EAX; RET",
    "26 DATA pointer slots",
    "49 RTTI-backed owner/slot rows",
    "CControllerDefinition",
    "CVertexShader",
    "CDXTrees",
    "5665/6098 = 92.90%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "exact source virtual method names proven",
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
        "pre-metadata.tsv": 1,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 30,
        "post-instructions.tsv": 229,
        "post-target-deep-instructions.tsv": 481,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 10,
        "post-context-tags.tsv": 10,
        "post-context-decompile/index.tsv": 10,
        "post-xref-site-instructions.tsv": 580,
        "post-candidate-vtable-rtti.tsv": 462,
        "post-valid-vtable-slots.tsv": 864,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    row = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(row["address"]) == ADDRESS, "post metadata address mismatch", failures)
    require(row["name"] == NAME, "post metadata name mismatch", failures)
    require(row["signature"] == SIGNATURE, f"post metadata signature mismatch: {row['signature']}", failures)
    for token in COMMENT_TOKENS:
        require(token in row.get("comment", ""), f"missing comment token: {token}", failures)

    tags = set(read_tsv(BASE / "post-tags.tsv")[0].get("tags", "").split(";"))
    require(EXPECTED_TAGS.issubset(tags), f"missing tags: {EXPECTED_TAGS - tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    data_refs = [row for row in xrefs if row.get("ref_type") == "DATA"]
    calls = [row for row in xrefs if row.get("ref_type") == "UNCONDITIONAL_CALL"]
    require(len(data_refs) == 26, "DATA xref count mismatch", failures)
    require(len(calls) == 4, "call xref count mismatch", failures)
    for call_addr in CALL_TARGETS:
        require(any(normalize_address(row["from_addr"]) == call_addr for row in calls), f"missing call xref {call_addr}", failures)

    instructions = read_tsv(BASE / "post-instructions.tsv")
    require(any(row["instruction_addr"] == "0x005019c0" and row["mnemonic"] == "XOR" and row["operands"] == "EAX, EAX" for row in instructions), "missing XOR EAX,EAX", failures)
    require(any(row["instruction_addr"] == "0x005019c2" and row["mnemonic"] == "RET" for row in instructions), "missing RET", failures)

    callsites = read_tsv(BASE / "post-xref-site-instructions.tsv")
    for target, (mnemonic, operand, branch) in CALL_TARGETS.items():
        scoped = [row for row in callsites if row["target_addr"] == target]
        require(any(row["role"] == "TARGET" and row["mnemonic"] == mnemonic and row["operands"] == operand for row in scoped), f"missing target callsite {target}", failures)
        require(any(row["role"] == "AFTER" and row["mnemonic"] == "TEST" and row["operands"] == "EAX, EAX" for row in scoped), f"missing EAX test after {target}", failures)
        require(any(row["role"] == "AFTER" and row["mnemonic"] == branch for row in scoped), f"missing branch after {target}", failures)

    rtti = read_tsv(BASE / "post-candidate-vtable-rtti.tsv")
    valid_rtti = [row for row in rtti if row.get("signature") == "0x00000000" and row.get("demangled_type_name")]
    require(len(valid_rtti) == 36, "RTTI-valid vtable count mismatch", failures)
    for owner in ("CControllerDefinition", "CVertexShader", "CDXTrees", "CDXFrontEndVideo"):
        require(any(row.get("demangled_type_name") == owner for row in valid_rtti), f"missing RTTI owner {owner}", failures)

    slots = read_tsv(BASE / "post-valid-vtable-slots.tsv")
    owner_slots = [row for row in slots if row.get("function_name") == NAME]
    require(len(owner_slots) == 49, "owner/slot row count mismatch", failures)
    for token in (
        ("005db404", "7"),
        ("005dfbc4", "1"),
        ("005dfbc4", "4"),
        ("005e59d8", "1"),
    ):
        require(any(row["vtable"] == token[0] and row["slot_index"] == token[1] for row in owner_slots), f"missing vtable slot {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 30 rows",
        "post-instructions.log": "Wrote 229 instruction rows",
        "post-target-deep-instructions.log": "Wrote 481 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-xref-site-instructions.log": "targets=4 missing=0",
        "post-valid-vtable-slots.log": "ExportVtableSlots complete: targets=36 rows=864",
        "quality-refresh.log": "total_functions=6098 commented_functions=5665",
        "queue-probe.log": "Commentless functions: 433",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave841.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave841_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "READBACK_BAD", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 433, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_head = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5665, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5665, "strict clean-signature count mismatch", failures)
    require(raw_head is not None and normalize_address(raw_head["address"]) == "0x0050ab60", "raw commentless head mismatch", failures)
    require(raw_head is not None and raw_head["name"] == "CVBufTexture__RenderAndRestoreStateFlag4", "raw commentless name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 171838343, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        VERTEX_SHADER_DOC,
        CONTROLLER_DOC,
        DESTRUCTABLE_DOC,
        DXTREES_DOC,
        VBUFTEXTURE_DOC,
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
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-cvertexshader-shared-vfunc09-wave841")
        == r"py -3 tools\ghidra_cvertexshader_shared_vfunc09_wave841_probe.py --check",
        "missing package script",
        failures,
    )
    require(any(row.get("task") == "Wave841 Shared Default/False VFunc09" for row in read_jsonl(LEDGER)), "missing Wave841 ledger row", failures)
    require(any(row.get("task") == "Wave841 Shared Default/False VFunc09" and row.get("attempt_id") == 20496 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave841 attempt row", failures)


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
        print("Wave841 shared default/false vfunc09 probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave841 shared default/false vfunc09 probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
