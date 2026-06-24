#!/usr/bin/env python3
"""Validate Wave900 final static-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave900-final-static-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_final_static_tail_wave900_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
FEPSAVE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPSaveGame.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-090248_post_wave900_final_static_tail_verified"
COMMON_TAGS = {
    "static-reaudit",
    "final-static-tail-wave900",
    "wave900-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "final-commentless-tail",
    "static-function-quality-closure",
}
TARGETS = {
    "0x005d04e6": {
        "name": "RtlUnwind",
        "signature": "void __stdcall RtlUnwind(PVOID TargetFrame, PVOID TargetIp, PEXCEPTION_RECORD ExceptionRecord, PVOID ReturnValue)",
        "tokens": ("Wave900 final static-tail", "0x005d81e4", "__global_unwind2", "one-instruction JMP"),
        "xrefs": {"0x0055d99b", "0x0055d705"},
        "extra_tags": {"windows-import-thunk", "rtl-unwind", "crt-seh-bridge", "one-instruction-thunk"},
    },
    "0x005d06f0": {
        "name": "CRT__InitSehFrameNoop",
        "signature": "void CRT__InitSehFrameNoop(void)",
        "tokens": ("Wave900 final static-tail", "0x005891cb", "FS:[0]", "ESP+0xc"),
        "xrefs": {"0x005891cb"},
        "extra_tags": {"crt-seh-frame", "locked-stack-abi", "cdxtexture-simd-init", "compiler-runtime"},
    },
    "0x005d08ad": {
        "name": "CRT__TmpFile_OpenUniqueBinaryStream",
        "signature": "int CRT__TmpFile_OpenUniqueBinaryStream(void)",
        "tokens": ("Wave900 final static-tail", "0x005b1d51", "DAT_009d3038", "0x8542", "0x180"),
        "xrefs": {"0x005b1d51"},
        "extra_tags": {"crt-tempfile", "cdxtexture-host-io", "locked-stack-abi", "filesystem-runtime-boundary"},
    },
    "0x005d0a9f": {
        "name": "CRT__LongJmpProbe_NoOp",
        "signature": "void CRT__LongJmpProbe_NoOp(void)",
        "tokens": ("Wave900 final static-tail", "_longjmp", "0x005d05f0", "RET 0x4"),
        "xrefs": {"0x005d05f0"},
        "extra_tags": {"crt-longjmp", "seh-shaped-probe", "locked-stack-abi", "compiler-runtime"},
    },
    "0x005d0c0c": {
        "name": "GetCurrentProcessId",
        "signature": "DWORD __stdcall GetCurrentProcessId(void)",
        "tokens": ("Wave900 final static-tail", "0x005d8144", "init_namebuf", "one-instruction JMP"),
        "xrefs": {"0x005d09c9"},
        "extra_tags": {"windows-import-thunk", "get-current-process-id", "temp-name-helper", "one-instruction-thunk"},
    },
    "0x005d0c7f": {
        "name": "CRT__LCMapStringW_AnsiCompat",
        "signature": "int CRT__LCMapStringW_AnsiCompat(void)",
        "tokens": ("Wave900 final static-tail", "0x005d0a89", "DAT_009d304c", "WideCharToMultiByte", "LCMapStringA"),
        "xrefs": {"0x005d0a89"},
        "extra_tags": {"crt-locale", "frontend-save-name", "wide-string-compat", "locked-stack-abi"},
    },
    "0x005d5120": {
        "name": "CTexture__FindTexture_Unwind",
        "signature": "void CTexture__FindTexture_Unwind(void)",
        "tokens": ("Wave900 final static-tail", "0x0061d9cc", "0x00632ef0", "OID__FreeObject_Callback"),
        "xrefs": {"0x0061d9cc"},
        "extra_tags": {"texture-find-unwind", "scope-table", "texture-cpp", "oid-free-callback"},
    },
}
CORE_ANCHORS = (
    "Wave900 final static tail",
    "final-static-tail-wave900",
    "0x005d04e6 RtlUnwind",
    "0x005d06f0 CRT__InitSehFrameNoop",
    "0x005d08ad CRT__TmpFile_OpenUniqueBinaryStream",
    "0x005d0a9f CRT__LongJmpProbe_NoOp",
    "0x005d0c0c GetCurrentProcessId",
    "0x005d0c7f CRT__LCMapStringW_AnsiCompat",
    "0x005d5120 CTexture__FindTexture_Unwind",
    "6113/6113 = 100.00%",
    BACKUP_PATH,
)
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime exception behavior proven",
    "runtime filesystem behavior proven",
    "runtime locale behavior proven",
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


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int, int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    undefined = sum(1 for row in rows if row.get("signature", "").startswith("undefined "))
    param = sum(1 for row in rows if re.search(r"\bparam_\d+\b", row.get("signature", "")))
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, undefined, param, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 8,
        "pre-instructions.tsv": 304,
        "pre-decompile/index.tsv": 7,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 8,
        "post-instructions.tsv": 304,
        "post-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | set(expected["extra_tags"])
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        actual_xrefs = xrefs.get(address, set())
        require(set(expected["xrefs"]).issubset(actual_xrefs), f"xrefs missing at {address}: {set(expected['xrefs']) - actual_xrefs}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 8 rows",
        "post-instructions.log": "Wrote 304 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=6113",
        "queue-probe.log": "Commentless functions: 0",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave900.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave900_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for key in ("commentlessHighSignal", "signature", "nameConfidence", "legacyWeakNames"):
        require(queue["priorityQueues"].get(key) == [], f"priority queue not empty: {key}", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, undefined, param, strict_clean = signature_counts(rows)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 6113, "quality TSV commented count mismatch", failures)
    require(undefined == 0, "quality TSV undefined count mismatch", failures)
    require(param == 0, "quality TSV param_N count mismatch", failures)
    require(strict_clean == 6113, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DXTEXTURE_DOC,
        FEPSAVE_DOC,
        TEXTURE_DOC,
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
    require(scripts.get("test:ghidra-final-static-tail-wave900") == r"py -3 tools\ghidra_final_static_tail_wave900_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave900 final static tail" for row in ledger_rows), "missing Wave900 ledger row", failures)
    require(any(row.get("task") == "Wave900 final static tail" and row.get("attempt_id") == 20555 for row in attempts), "missing Wave900 attempt row", failures)


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
        print("Wave900 final static-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave900 final static-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
