#!/usr/bin/env python3
"""Validate Wave883 CRT locale/string/runtime tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave883-crt-locale-string-runtime-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_locale_string_runtime_tail_wave883_2026-05-26.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave883 CRT locale/string/runtime tail"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260526-005047_post_wave883_crt_locale_string_runtime_tail_verified"
NEXT_HEAD = "0x00569cb8 ControlsUI__AbortInvalidParameter"
STRICT_PROXY = "5966/6113 = 97.60%"

TARGETS = {
    "0x00563ad3": ("CRT__FpuTransDispatch2_ClearStatusAndHandle", "void CRT__FpuTransDispatch2_ClearStatusAndHandle(void)", ("__ctrandisp2", "CRT__HandleFloatingPointException", "0x7ff0")),
    "0x00565ee0": ("CRT__LCMapStringA_Compat", "int CRT__LCMapStringA_Compat(void)", ("LCMapStringW", "WideCharToMultiByte", "CDXTexture__AsciiToLowerInPlace")),
    "0x00567aa8": ("CRT__GetErrnoThreadPtr_00567aa8", "int CRT__GetErrnoThreadPtr_00567aa8(void)", ("+ 0x8", "43 xrefs", "CRT__StrToLongWithBaseAndLocaleCType")),
    "0x00567ab1": ("CRT__GetDosErrnoThreadPtr_00567ab1", "int CRT__GetDosErrnoThreadPtr_00567ab1(void)", ("+ 0xc", "21 xrefs", "CRT__SetErrnoAndDosErrnoFromWinError")),
    "0x00567ed0": ("CRT__SystemTimeToUnixTimestampLocal", "int CRT__SystemTimeToUnixTimestampLocal(void)", ("CRT__EnsureTzsetInitialized", "0x7c558180", "CRT__IsInDst_WrapperLocked")),
    "0x005681bc": ("CRT__ResetMultibyteTables_005681bc", "void CRT__ResetMultibyteTables_005681bc(void)", ("0x40 dwords", "DAT_009d33a4", "DAT_009d35c4")),
    "0x005681e5": ("CRT__BuildMultibyteCTypeCaseTables_005681e5", "void CRT__BuildMultibyteCTypeCaseTables_005681e5(void)", ("GetCPInfo", "CRT__GetStringTypeACompat", "CRT__LCMapStringA_Compat")),
    "0x0056836a": ("CRT__EnsureRuntimeInitSentinelSet", "void CRT__EnsureRuntimeInitSentinelSet(void)", ("DAT_009d4608", "CRT__SetMultibyteCodePage(-3)", "CRT__BuildArgvTable")),
    "0x00568390": ("stricmp", "int __cdecl stricmp(char * a, char * b)", ("217 xrefs", "CLIParams__ParseCommandLine", "CRT__ToLowerWithLocale")),
    "0x0056a1cd": ("CRT__ParseFloatTextToLongDouble", "int CRT__ParseFloatTextToLongDouble(void)", ("DAT_00653aa0", "0x56a66e", "CRT__GetCharTypeMask_Compat")),
    "0x0056a69e": ("CRT__GetStringTypeACompat", "int CRT__GetStringTypeACompat(void)", ("GetStringTypeW", "MultiByteToWideChar", "DAT_009d0ad0")),
    "0x0056aff4": ("CRT__AllocOsHandleSlot", "int CRT__AllocOsHandleSlot(void)", ("0x12", "0x480-byte", "CRT__LockFileHandleByIndex")),
    "0x0056be17": ("CRT__InitCTypeTablesFromCodePage", "int CRT__InitCTypeTablesFromCodePage(void)", ("0x202/0x202/0x101/0x202", "0x8000", "CRT__GetStringTypeWideOrAnsiCompat_0056defa")),
    "0x0056c05c": ("CRT__ReturnZero", "int CRT__ReturnZero(void)", ("return-zero", "CRT__HandleFloatingPointException")),
    "0x0056c2af": ("CRT__FindLocaleForLanguageAndCountry_0056c2af", "void CRT__FindLocaleForLanguageAndCountry_0056c2af(void)", ("CRT__EnumLocalesCallback_MatchLanguageCountry", "DAT_009d0b30")),
    "0x0056c53a": ("CRT__FindLocaleForLanguageOnly_0056c53a", "void CRT__FindLocaleForLanguageOnly_0056c53a(void)", ("CRT__EnumLocalesCallback_MatchLanguageOnly", "DAT_009d0b30")),
    "0x0056c64d": ("CRT__FindLocaleForCountryOnly_0056c64d", "void CRT__FindLocaleForCountryOnly_0056c64d(void)", ("CRT__ValidateCodePageAgainstLocale", "DAT_009d0b1c")),
    "0x0056c70a": ("CRT__InitLocaleDefaults", "void CRT__InitLocaleDefaults(void)", ("GetUserDefaultLCID", "0x104")),
    "0x0056c80b": ("CRT__IsWindowsNtPlatform", "int CRT__IsWindowsNtPlatform(void)", ("GetVersionExA", "dwPlatformId equals 2")),
    "0x0056c998": ("CRT__StrToLongWithBaseAndLocaleCType", "int CRT__StrToLongWithBaseAndLocaleCType(void)", ("0xffffffff/base", "errno 0x22", "CRT__ToUpperWithLocaleLock")),
    "0x0056cbb4": ("CRT__EnsureTzsetInitialized", "void CRT__EnsureTzsetInitialized(void)", ("locks index 0xb", "CRT__Tzset", "DAT_009d0bf8")),
    "0x0056cbe2": ("CRT__Tzset", "void CRT__Tzset(void)", ("GetTimeZoneInformation", "TZ", "DAT_00656988")),
    "0x0056defa": ("CRT__GetStringTypeWideOrAnsiCompat_0056defa", "int CRT__GetStringTypeWideOrAnsiCompat_0056defa(void)", ("DAT_009d0c2c", "GetStringTypeA", "CRT__MemMoveOverlapSafe")),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-locale-string-runtime-tail-wave883",
    "wave883-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-verified",
    "important-crt-runtime-infrastructure",
    "high-importance-low-local-evidence-density",
    "compiler-runtime",
    "crt-runtime",
    "raw-commentless-tail",
}

XREF_COUNTS = {
    "0x00563ad3": 2,
    "0x00565ee0": 8,
    "0x00567aa8": 43,
    "0x00567ab1": 21,
    "0x00567ed0": 1,
    "0x005681bc": 1,
    "0x005681e5": 1,
    "0x0056836a": 4,
    "0x00568390": 217,
    "0x0056a1cd": 3,
    "0x0056a69e": 3,
    "0x0056aff4": 1,
    "0x0056be17": 1,
    "0x0056c05c": 2,
    "0x0056c2af": 1,
    "0x0056c53a": 1,
    "0x0056c64d": 1,
    "0x0056c70a": 1,
    "0x0056c80b": 1,
    "0x0056c998": 2,
    "0x0056cbb4": 1,
    "0x0056cbe2": 1,
    "0x0056defa": 2,
}

CORE_ANCHORS = (
    TASK,
    "crt-locale-string-runtime-tail-wave883",
    "0x00563ad3 CRT__FpuTransDispatch2_ClearStatusAndHandle",
    "0x00565ee0 CRT__LCMapStringA_Compat",
    "0x00567aa8 CRT__GetErrnoThreadPtr_00567aa8",
    "0x00568390 stricmp",
    "0x0056a1cd CRT__ParseFloatTextToLongDouble",
    "0x0056aff4 CRT__AllocOsHandleSlot",
    "0x0056cbe2 CRT__Tzset",
    "0x0056defa CRT__GetStringTypeWideOrAnsiCompat_0056defa",
    "LCMapStringW",
    "GetTimeZoneInformation",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime locale behavior proven",
    "runtime timezone behavior proven",
    "runtime nls behavior proven",
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
        "pre-metadata.tsv": 23,
        "pre-tags.tsv": 23,
        "pre-xrefs.tsv": 319,
        "pre-instructions.tsv": 1973,
        "pre-decompile/index.tsv": 23,
        "post-metadata.tsv": 23,
        "post-tags.tsv": 23,
        "post-xrefs.tsv": 319,
        "post-instructions.tsv": 1973,
        "post-decompile/index.tsv": 23,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    xref_counts: dict[str, int] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        address = normalize_address(row["target_addr"])
        xref_counts[address] = xref_counts.get(address, 0) + 1

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave883 static read-back" in comment, f"missing Wave883 comment at {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(xref_counts.get(address) == XREF_COUNTS[address], f"xref count mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=23 renamed=0 would_rename=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=23 skipped=0 renamed=0 would_rename=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=23 renamed=0 would_rename=0 missing=0 bad=0",
        "post-metadata.log": "targets=23 found=23 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=23 missing=0",
        "post-xrefs.log": "Wrote 319 rows",
        "post-instructions.log": "Wrote 1973 function-body instruction rows",
        "post-decompile.log": "targets=23 dumped=23 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6113 commented_functions=5966",
        "queue-probe.log": "Commentless functions: 147",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave883.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave883_queue_probe.log",
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
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 147, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6113, "quality TSV row count mismatch", failures)
    require(commented == 5966, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5966, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00569cb8", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "ControlsUI__AbortInvalidParameter", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172788615 or backup.get("totalBytes") == 172788615.0, "backup byte count mismatch", failures)
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
        CRT_DOC,
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
        scripts.get("test:ghidra-crt-locale-string-runtime-tail-wave883")
        == r"py -3 tools\ghidra_crt_locale_string_runtime_tail_wave883_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave883 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20538 for row in attempts), "missing Wave883 attempt row", failures)


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
        print("Wave883 CRT locale/string/runtime tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave883 CRT locale/string/runtime tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
