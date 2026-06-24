#!/usr/bin/env python3
"""Validate Wave838 CUnit attached-node forwarder read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave838-unitai-attached-node"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_attached_node_forwarders_wave838_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNITAI_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-021158_post_wave838_unit_attached_node_forwarders_verified"

TARGETS = {
    "0x004fce40": {
        "name": "CUnit__ForwardAttachedNodeVFunc14IfPresent",
        "slot": "0x14",
        "ret": "0x004fce71",
        "old": "CUnitAI__CallAttachedNodeVFunc14IfPresent",
        "tags": {"owner-corrected", "vfunc-14"},
        "comment": (
            "Wave838 static read-back/name/signature correction",
            "this+0x208",
            "vfunc +0x14",
            "RET 0x10 at 0x004fce71",
            "CUnitAI__CallAttachedNodeVFunc14IfPresent",
            "0x0044610a CUnitAI__UpdateDoorWingEngagement_MidRange",
            "argument layout, return semantics, runtime behavior",
        ),
        "xrefs": {
            "0x00416712",
            "0x0048a0b8",
            "0x004a04db",
            "0x004ef3d9",
            "0x004fed4b",
            "0x0044610a",
        },
    },
    "0x004fce80": {
        "name": "CUnit__ForwardAttachedNodeVFunc18IfPresent",
        "slot": "0x18",
        "ret": "0x004fceb1",
        "old": "CUnit__ForwardControllerQuery18",
        "tags": {"name-refined", "vfunc-18"},
        "comment": (
            "Wave838 static read-back/name/signature correction",
            "this+0x208",
            "vfunc +0x18",
            "RET 0x10 at 0x004fceb1",
            "CUnit__ForwardControllerQuery18",
            "0x0047a38a",
            "0x0048a113",
            "0x004ef404",
            "0x004fecda",
            "0x004feda1",
            "argument layout, return semantics, runtime behavior",
        ),
        "xrefs": {
            "0x0047a38a",
            "0x0047af7e",
            "0x0048a113",
            "0x004ef404",
            "0x004fecda",
            "0x004feda1",
        },
    },
    "0x004fcec0": {
        "name": "CUnit__ForwardAttachedNodeVFunc1CIfPresent",
        "slot": "0x1c",
        "ret": "0x004fcef1",
        "old": "CUnitAI__GetAttachedNodeReadyState",
        "tags": {"owner-corrected", "vfunc-1c"},
        "comment": (
            "Wave838 static read-back/name/signature correction",
            "this+0x208",
            "vfunc +0x1c",
            "RET 0x10 at 0x004fcef1",
            "CUnitAI__GetAttachedNodeReadyState",
            "CSquadNormal__BuildAttackFormation",
            "0x004e8ba9/0x004e8c06",
            "0x00445db5/0x0044626e/0x00446472",
            "argument layout, return semantics, runtime behavior",
        ),
        "xrefs": {
            "0x0047b896",
            "0x004e8ba9",
            "0x004e8c06",
            "0x004fed76",
            "0x00445db5",
            "0x0044626e",
            "0x00446472",
        },
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "unit-attached-node-forwarders-wave838",
    "wave838-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "name-corrected",
    "cunit",
    "attached-node",
    "controller-forwarder",
    "ret-10",
}

CORE_ANCHORS = (
    "Wave838 Unit Attached Node Forwarders",
    "unit-attached-node-forwarders-wave838",
    "0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent",
    "0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent",
    "0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent",
    "CUnitAI__CallAttachedNodeVFunc14IfPresent",
    "CUnit__ForwardControllerQuery18",
    "CUnitAI__GetAttachedNodeReadyState",
    "0x004fde70 CWarspite__TransitionToUndeploying",
    "5662/6098 = 92.85%",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "argument layout proven",
    "return semantics proven",
    "low-signal",
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


def signature_for(name: str) -> str:
    return f"int __thiscall {name}(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)"


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
        "pre-metadata.tsv": 3,
        "pre-tags.tsv": 3,
        "pre-xrefs.tsv": 19,
        "pre-instructions.tsv": 171,
        "pre-target-deep-instructions.tsv": 483,
        "pre-xref-site-instructions.tsv": 855,
        "pre-decompile/index.tsv": 3,
        "pre-context-metadata.tsv": 8,
        "pre-context-decompile/index.tsv": 8,
        "post-metadata.tsv": 3,
        "post-tags.tsv": 3,
        "post-xrefs.tsv": 19,
        "post-instructions.tsv": 171,
        "post-target-deep-instructions.tsv": 483,
        "post-xref-site-instructions.tsv": 855,
        "post-decompile/index.tsv": 3,
        "post-context-metadata.tsv": 8,
        "post-context-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    instructions = read_tsv(BASE / "post-instructions.tsv")
    instruction_text_by_target: dict[str, str] = {}
    for row in instructions:
        target = normalize_address(row.get("target_addr", ""))
        if target in TARGETS:
            instruction_text_by_target.setdefault(target, "")
            instruction_text_by_target[target] += "\n".join(
                (row.get("instruction_addr", ""), row.get("mnemonic", ""), row.get("operands", ""))
            )

    for address, spec in TARGETS.items():
        name = spec["name"]
        signature = signature_for(name)
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in spec["comment"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | spec["tags"]
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(xrefs.get(address) == spec["xrefs"], f"xref set mismatch at {address}: {xrefs.get(address)}", failures)

        inst = instruction_text_by_target.get(address, "")
        require("dword ptr [ECX + 0x208]" in inst, f"missing attached-node load at {address}", failures)
        require(f"dword ptr [EAX + {spec['slot']}]" in inst, f"missing slot dispatch at {address}", failures)
        require("RET\n0x10" in inst or "RET\r\n0x10" in inst, f"missing RET 0x10 at {address}", failures)
        require(spec["ret"] in inst, f"missing return address token at {address}", failures)

        decompile_text = read_text(BASE / "post-decompile" / f"{address[2:]}_{name}.c")
        for token in (signature, "*(int **)((int)this + 0x208)", f"+ {spec['slot']}", "return in_EAX"):
            require(token in decompile_text, f"missing decompile token at {address}: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=3 signature_updated=3 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=3 skipped=0 renamed=3 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=3 found=3 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=3 missing=0",
        "post-xrefs.log": "Wrote 19 rows",
        "post-instructions.log": "Wrote 171 instruction rows",
        "post-target-deep-instructions.log": "Wrote 483 instruction rows",
        "post-xref-site-instructions.log": "Wrote 855 instruction rows",
        "post-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "post-context-metadata.log": "targets=8 found=8 missing=0",
        "post-context-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5662",
        "queue-probe.log": "Commentless functions: 436",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave838.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave838_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    for spec in TARGETS.values():
        require(f"READBACK_OK: {next(addr for addr, data in TARGETS.items() if data is spec)} {spec['name']}" in apply_text, f"missing READBACK_OK for {spec['name']}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 436, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "commentless high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5662, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5662, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004fde70", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CWarspite__TransitionToUndeploying", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171838343 or backup.get("totalBytes") == 171838343.0, "backup byte count mismatch", failures)
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
        UNIT_DOC,
        UNITAI_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-unit-attached-node-forwarders-wave838")
        == r"py -3 tools\ghidra_unit_attached_node_forwarders_wave838_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave838 Unit Attached Node Forwarders" for row in ledger_rows), "missing Wave838 ledger row", failures)
    require(
        any(row.get("task") == "Wave838 Unit Attached Node Forwarders" and row.get("attempt_id") == 20493 for row in attempts),
        "missing Wave838 attempt row",
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
        print("Wave838 unit-attached-node forwarders probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave838 unit-attached-node forwarders probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
