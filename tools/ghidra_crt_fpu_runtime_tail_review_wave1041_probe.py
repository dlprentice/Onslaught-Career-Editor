#!/usr/bin/env python3
"""Validate Wave1041 CRT/FPU runtime-tail read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1041-crt-fpu-runtime-tail-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_crt_fpu_runtime_tail_review_wave1041_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1041_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified"

TARGETS = {
    "0x0055da76": {
        "name": "CRT__InitRuntimeFromStoredFrameGlobals",
        "signature": "void CRT__InitRuntimeFromStoredFrameGlobals(void)",
        "comment": ("CRT__InitFloatConversionDispatchTable", "DAT_009d08b8", "CRT__InitFpuControlWord_0x10000_0x30000"),
        "decompile": ("CRT__InitFloatConversionDispatchTable", "DAT_009d08b8", "CRT__InitFpuControlWord_0x10000_0x30000"),
        "instructions": ("CALL\t0x0055da8d", "MOV\t[0x009d08b8], EAX", "FNCLEX"),
    },
    "0x0055e3ea": {
        "name": "CRT__FpuIntrinsicDispatch2Thunk",
        "signature": "void __cdecl CRT__FpuIntrinsicDispatch2Thunk(void)",
        "comment": ("__cintrindisp2", "broad math/renderer/gameplay/UI callsites", "sprite-local"),
        "decompile": ("__cintrindisp2",),
        "instructions": ("MOV\tEDX, 0x653330", "JMP\t0x00563a10"),
    },
    "0x00562a89": {
        "name": "CRT__SetErrnoForFpSourceKind",
        "signature": "void __cdecl CRT__SetErrnoForFpSourceKind(int sourceKind)",
        "comment": ("EDOM", "ERANGE", "CRT thread-local errno pointer"),
        "decompile": ("0x21", "0x22", "CRT__GetErrnoThreadPtr_00567aa8"),
        "instructions": ("MOV\tdword ptr [EAX], 0x22", "MOV\tdword ptr [EAX], 0x21"),
    },
    "0x00569cb8": {
        "name": "CRT__FloatDispatchAmsgExitCode2Thunk",
        "signature": "void CRT__FloatDispatchAmsgExitCode2Thunk(void)",
        "comment": ("__amsg_exit", "0x00653658", "ControlsUI__FormatWideStringCore"),
        "decompile": ("__amsg_exit(2)",),
        "instructions": ("PUSH\t0x2", "CALL\t0x00560289", "POP\tECX"),
    },
}

DOC_TOKENS = (
    "Wave1041",
    "crt-fpu-runtime-tail-review-wave1041",
    "0x0055da76 CRT__InitRuntimeFromStoredFrameGlobals",
    "0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk",
    "0x00562a89 CRT__SetErrnoForFpSourceKind",
    "0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk",
    "__cintrindisp2",
    "__amsg_exit",
    "DAT_009d08b8",
    "0x00653658",
    "727/1408 = 51.63%",
    "960/1493 = 64.30%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime errno behavior proven",
    "runtime error/report/exit behavior proven",
    "exact msvc crt helper/source identity proven",
    "exact float-dispatch table semantics proven",
    "fpu control/status side effects proven",
    "beA patching behavior proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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


def decompile_path(address: str, name: str) -> Path:
    return BASE / "decompile" / f"{address[2:]}_{name}.c"


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 4,
        "tags.tsv": 4,
        "xrefs.tsv": 63,
        "instructions.tsv": 24,
        "decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    instruction_text = "\n".join(
        f"{normalize_address(row['target_addr'])}\t{row['mnemonic']}\t{row['operands']}"
        for row in read_tsv(BASE / "instructions.tsv")
    )
    xref_text = read_text(BASE / "xrefs.tsv")

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["comment"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            require("static-reaudit" in tag_text, f"missing static-reaudit tag at {address}", failures)
            require(("crt" in tag_text.lower()) or ("compiler-runtime" in tag_text), f"missing CRT/compiler tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        body = read_text(decompile_path(address, expected["name"]))
        for token in expected["decompile"]:
            require(token in body, f"missing decompile token at {address}: {token}", failures)
        for token in expected["instructions"]:
            require(f"{address}\t{token}" in instruction_text, f"missing instruction token at {address}: {token}", failures)

    for token in (
        "CRT__RunStaticInitRangesWithOptionalCallback",
        "CConsole__RenderLoadingScreen",
        "CRT__HandleFloatingPointExceptionByFlags",
        "CRT__FormatOutputToStream",
        "00653658",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=4 found=4 missing=0",
        "tags.log": "rows=4 missing=0",
        "xrefs.log": "Wrote 63 rows",
        "instructions.log": "Wrote 24 function-body instruction rows",
        "decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Traceback", "BADADDR", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (174263175, 174263175.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_and_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        CRT_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        lowered = text.lower()
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-crt-fpu-runtime-tail-review-wave1041")
        == r"py -3 tools\ghidra_crt_fpu_runtime_tail_review_wave1041_probe.py --check",
        "missing package focused probe script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1041-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1041 --check",
        "missing package aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1041 CRT FPU runtime tail review" for row in ledger_rows), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1041 CRT FPU runtime tail review" and row.get("attempt_id") == 20623 for row in attempt_rows),
        "missing attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_and_docs(failures)

    if failures:
        print("Wave1041 CRT/FPU runtime-tail review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1041 CRT/FPU runtime-tail review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
