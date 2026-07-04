#!/usr/bin/env python3
"""Validate Wave840 shader capability init read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave840-shader-capability-init"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_shader_capability_init_wave840_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
PLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Platform.cpp" / "_index.md"
VERTEX_SHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
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

ADDRESS = "0x005016b0"
NAME = "InitShaderCapabilityFlagsAndCVar"
SIGNATURE = "void __cdecl InitShaderCapabilityFlagsAndCVar(void)"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-030308_post_wave840_shader_capability_init_verified"
NEXT_HEAD = "0x005019c0 VFuncSlot_09_005019c0"

EXPECTED_TAGS = {
    "static-reaudit",
    "shader-capability-init-wave840",
    "wave840-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "comment-hardened",
    "pc-platform",
    "vertex-shader",
    "direct3d",
    "cvar",
}

COMMENT_TOKENS = (
    "Wave840 static read-back/signature/comment hardening",
    "PCPlatform__Init",
    "0x005155b1",
    "Initting shaders",
    "DAT_00888c8c",
    "Direct3D device vtable +0x1c",
    "DAT_00854e6c",
    "0xfffe0101",
    "DAT_0063c108",
    "cg_forcevertexshaders",
    "DAT_00854e6d",
    "runtime shader enablement",
)

INSTRUCTION_EXPECTATIONS = (
    ("0x005016cc", "CALL", "dword ptr [ECX + 0x1c]"),
    ("0x005016cf", "CMP", "dword ptr [ESP + 0xc4], 0xfffe0101"),
    ("0x005016dd", "MOV", "[0x00854e6c], AL"),
    ("0x005016f1", "PUSH", "0x854e10"),
    ("0x0050170b", "PUSH", "0x63cde8"),
    ("0x00501715", "CALL", "0x0042b040"),
    ("0x00501720", "RET", ""),
)

CALLER_EXPECTATIONS = (
    ("0x00515598", "MOV", "byte ptr [0x0063c108], 0x1"),
    ("0x0051559f", "PUSH", "0x63e008"),
    ("0x005155b1", "CALL", "0x005016b0"),
)

CORE_DOC_TOKENS = (
    "Wave840 Shader Capability Init",
    "shader-capability-init-wave840",
    "0x005016b0 InitShaderCapabilityFlagsAndCVar",
    SIGNATURE,
    "0x005155b1 PCPlatform__Init",
    "Initting shaders",
    "cg_forcevertexshaders",
    "DAT_00854e6c",
    "0xfffe0101",
    "5664/6098 = 92.89%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime shader enablement proven",
    "runtime hardware behavior proven",
    "runtime driver behavior proven",
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


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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
        "pre-tags.tsv": 1,
        "pre-xrefs.tsv": 1,
        "pre-instructions.tsv": 205,
        "pre-target-deep-instructions.tsv": 501,
        "pre-xref-site-instructions.tsv": 97,
        "pre-decompile/index.tsv": 1,
        "pre-context-metadata.tsv": 6,
        "pre-context-tags.tsv": 6,
        "pre-context-decompile/index.tsv": 6,
        "post-metadata.tsv": 1,
        "post-tags.tsv": 1,
        "post-xrefs.tsv": 1,
        "post-instructions.tsv": 205,
        "post-target-deep-instructions.tsv": 501,
        "post-xref-site-instructions.tsv": 97,
        "post-decompile/index.tsv": 1,
        "post-context-metadata.tsv": 6,
        "post-context-tags.tsv": 6,
        "post-context-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")[0]
    require(normalize_address(metadata.get("address", "")) == ADDRESS, "metadata address mismatch", failures)
    require(metadata.get("name") == NAME, "metadata name mismatch", failures)
    require(metadata.get("signature") == SIGNATURE, "metadata signature mismatch", failures)
    require(metadata.get("status") == "OK", "metadata status mismatch", failures)
    comment = metadata.get("comment", "")
    for token in COMMENT_TOKENS:
        require(token in comment, f"missing comment token: {token}", failures)

    tags = read_tsv(BASE / "post-tags.tsv")[0]
    require(normalize_address(tags.get("address", "")) == ADDRESS, "tag address mismatch", failures)
    actual_tags = set(tags.get("tags", "").split(";"))
    require(EXPECTED_TAGS.issubset(actual_tags), f"missing tags: {EXPECTED_TAGS - actual_tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    require(normalize_address(xrefs[0].get("from_addr", "")) == "0x005155b1", "xref source mismatch", failures)
    require(xrefs[0].get("from_function") == "PCPlatform__Init", "xref caller mismatch", failures)
    require(xrefs[0].get("ref_type") == "UNCONDITIONAL_CALL", "xref type mismatch", failures)

    instructions = {
        normalize_address(row.get("instruction_addr", "")): row
        for row in read_tsv(BASE / "post-target-deep-instructions.tsv")
    }
    for address, mnemonic, operands in INSTRUCTION_EXPECTATIONS:
        row = instructions.get(address)
        require(row is not None, f"missing instruction row: {address}", failures)
        if row is not None:
            require(row.get("mnemonic") == mnemonic, f"instruction mnemonic mismatch at {address}", failures)
            require(row.get("operands") == operands, f"instruction operands mismatch at {address}", failures)

    caller = {
        normalize_address(row.get("instruction_addr", "")): row
        for row in read_tsv(BASE / "post-xref-site-instructions.tsv")
    }
    for address, mnemonic, operands in CALLER_EXPECTATIONS:
        row = caller.get(address)
        require(row is not None, f"missing caller instruction row: {address}", failures)
        if row is not None:
            require(row.get("mnemonic") == mnemonic, f"caller mnemonic mismatch at {address}", failures)
            require(row.get("operands") == operands, f"caller operands mismatch at {address}", failures)

    decompile_rows = read_tsv(BASE / "post-decompile" / "index.tsv")
    require(decompile_rows[0].get("signature") == SIGNATURE, "decompile signature mismatch", failures)
    require(decompile_rows[0].get("status") == "OK", "decompile status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=1 found=1 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=1 missing=0",
        "post-xrefs.log": "Wrote 1 rows",
        "post-instructions.log": "Wrote 205 instruction rows",
        "post-target-deep-instructions.log": "Wrote 501 instruction rows",
        "post-xref-site-instructions.log": "Wrote 97 instruction rows",
        "post-decompile.log": "targets=1 dumped=1 missing=0 failed=0",
        "post-context-metadata.log": "targets=6 found=6 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5664",
        "queue-probe.log": "Commentless functions: 434",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave840.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave840_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 434, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5664, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5664, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x005019c0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "VFuncSlot_09_005019c0", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 171838343, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        PCPLATFORM_DOC,
        PLATFORM_DOC,
        VERTEX_SHADER_DOC,
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
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-shader-capability-init-wave840")
        == r"py -3 tools\ghidra_shader_capability_init_wave840_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave840 Shader Capability Init" for row in ledger_rows), "missing Wave840 ledger row", failures)
    require(
        any(row.get("task") == "Wave840 Shader Capability Init" and row.get("attempt_id") == 20495 for row in attempt_rows),
        "missing Wave840 attempt row",
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
        print("Wave840 shader capability init probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave840 shader capability init probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
