#!/usr/bin/env python3
"""Validate Wave739 D3D runtime-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave739-d3d-runtime-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_d3d_runtime_tail_wave739_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DISPLAY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "display-settings.md"
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

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260522-135016_post_wave739_d3d_runtime_tail_verified"

TARGETS = {
    "0x005be622": {
        "name": "Direct3DCreate9",
        "signature": "void * __stdcall Direct3DCreate9(uint sdk_version)",
        "comment_tokens": ("Wave739 static read-back", "six-byte JMP", "0x005d8348", "0x005290bc", "SDK version 0x1f"),
        "tags": {"static-reaudit", "d3d-runtime-tail-wave739", "wave739-readback-verified", "signature-hardened", "import-thunk", "d3d9"},
        "decompile_status": "OK",
    },
    "0x005be628": {
        "name": "HResultToString",
        "signature": "char * __stdcall HResultToString(int hresult)",
        "comment_tokens": ("Wave739 static read-back", "22 call sites", "single RET 0x4", "0x005c9c66", "E_ABORT", "decompile times out"),
        "tags": {"static-reaudit", "d3d-runtime-tail-wave739", "wave739-readback-verified", "signature-hardened", "hresult-string-map", "decompile-timeout"},
        "decompile_status": "FAILED",
    },
}

DOC_TOKENS = (
    "Wave739 D3D runtime tail",
    "d3d-runtime-tail-wave739",
    "0x005be622 Direct3DCreate9",
    "0x005be628 HResultToString",
    "0x005d04e0 DirectInput8Create",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime graphics behavior proven",
    "runtime error reporting behavior proven",
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
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 22,
        "pre-instructions.tsv": 210,
        "pre-decompile/index.tsv": 2,
        "xref-site-instructions.tsv": 902,
        "hresult-full-instructions.tsv": 17343,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 22,
        "post-instructions.tsv": 210,
        "post-decompile/index.tsv": 2,
        "post-xref-site-instructions.tsv": 902,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
        require(row.get("signature") == expected["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(expected["tags"].issubset(actual_tags), f"tags missing at {address}: {expected['tags'] - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == expected["decompile_status"], f"decompile status mismatch at {address}", failures)

    hresult_rows = read_tsv(BASE / "hresult-full-instructions.tsv")
    require(any(row["instruction_addr"] == "0x005c9c66" and row["mnemonic"] == "RET" and row["operands"] == "0x4" for row in hresult_rows), "missing HResultToString RET 0x4 evidence", failures)
    require(read_tsv(BASE / "hresult-string-60bc44.tsv")[0].get("cstring") == "E_ABORT", "sample HRESULT string mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "pre-metadata.log": "targets=2 found=2 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "pre-xrefs.log": "Wrote 22 rows",
        "pre-instructions.log": "Wrote 210 instruction rows",
        "pre-decompile.log": "targets=2 dumped=1 missing=0 failed=1",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 22 rows",
        "post-instructions.log": "Wrote 210 instruction rows",
        "post-decompile.log": "targets=2 dumped=1 missing=0 failed=1",
        "post-xref-site-instructions.log": "Wrote 902 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=4351",
        "queue-probe.log": "Commentless functions: 1747",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1747, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1215, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 36, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d04e0", "high-signal head mismatch", failures)
    require(high_signal["name"] == "DirectInput8Create", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4351, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4293, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 166988679, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        DISPLAY_DOC,
        VERTEX_SHADER_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for doc in docs:
        text = read_text(doc)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {doc.relative_to(ROOT)}: {token}", failures)
        for token in OVERCLAIM_TOKENS:
            require(token.lower() not in text.lower(), f"overclaim token in {doc.relative_to(ROOT)}: {token}", failures)

    package_text = read_text(PACKAGE_JSON)
    require("test:ghidra-d3d-runtime-tail-wave739" in package_text, "missing npm probe script", failures)

    ledger_entries = read_jsonl(LEDGER)
    attempt_entries = read_jsonl(ATTEMPT_LOG)
    require(any(e.get("task") == "Wave739 D3D runtime tail" for e in ledger_entries), "ledger missing Wave739", failures)
    require(any(e.get("task") == "Wave739 D3D runtime tail" for e in attempt_entries), "attempt log missing Wave739", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero on validation failure.")
    args = parser.parse_args()

    failures: list[str] = []
    for check in (check_artifacts, check_logs, check_queue_and_backup, check_docs):
        try:
            check(failures)
        except Exception as exc:  # noqa: BLE001 - probe should report all available context.
            failures.append(f"{check.__name__}: {exc}")

    if failures:
        print("Wave739 D3D runtime tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave739 D3D runtime tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
