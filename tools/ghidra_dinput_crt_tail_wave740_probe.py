#!/usr/bin/env python3
"""Validate Wave740 DirectInput/CRT tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave740-dinput-crt-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dinput_crt_tail_wave740_2026-05-22.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
IMPORT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "import-thunks.md"
FEP_SAVE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FEPSaveGame.cpp" / "_index.md"
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

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260522-141639_post_wave740_dinput_crt_tail_verified"

TARGETS = {
    "0x005d04e0": {
        "name": "DirectInput8Create",
        "signature": "int __stdcall DirectInput8Create(void * hinstance, uint directinput_version, void * riid_directinput8, void * * directinput_out, void * outer_unknown)",
        "tokens": ("DINPUT8.DLL", "0x005d8020", "0x00513178", "version 0x800"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "directinput", "import-thunk"},
    },
    "0x005d04ec": {
        "name": "CFEPSaveGame__WideStrCaseInsensitiveCompare",
        "signature": "int __cdecl CFEPSaveGame__WideStrCaseInsensitiveCompare(ushort * left_wide, ushort * right_wide)",
        "tokens": ("wide-string", "EnumerateSaveFiles_Main", "CFEPSaveGame__CreateSave", "WideCharToLowerCompat"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "frontend-save", "wide-string"},
    },
    "0x005d070f": {
        "name": "CRT__VsnprintfAndTerminate_005d070f",
        "signature": "int __cdecl CRT__VsnprintfAndTerminate_005d070f(char * out_buffer, int out_buffer_size, char * format, void * va_list_args)",
        "tokens": ("vsnprintf-style", "Texture and CFastVB diagnostic", "CRT__FormatOutputToStream"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "crt-format", "vsnprintf"},
    },
    "0x005d075f": {
        "name": "CRT__FormatToBufferAndTerminate",
        "signature": "int __cdecl CRT__FormatToBufferAndTerminate(char * out_buffer, int out_buffer_size, char * format)",
        "tokens": ("sprintf-style", "stack0x00000010", "Texture diagnostic"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "crt-format", "hidden-varargs-tail"},
    },
    "0x005d07f4": {
        "name": "CRT__FSeek_Locked",
        "signature": "int __cdecl CRT__FSeek_Locked(void * stream, int offset, int origin)",
        "tokens": ("locked CRT fseek", "FSeek_UnlockedCore", "unlocks by stream address"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "crt-stdio", "locked-wrapper"},
    },
    "0x005d0820": {
        "name": "CRT__FSeek_UnlockedCore",
        "signature": "int __cdecl CRT__FSeek_UnlockedCore(void * stream, int offset, int origin)",
        "tokens": ("errno 0x16", "CRT__LseekFd", "0 or -1"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "crt-stdio", "unlocked-core"},
    },
    "0x005d09e4": {
        "name": "CRT__IncrementDotSuffixCounter",
        "signature": "int __cdecl CRT__IncrementDotSuffixCounter(char * path_buffer)",
        "tokens": ("temp-file suffix", "base 0x20", "0x7fff"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "crt-tempfile", "suffix-counter"},
    },
    "0x005d0a2a": {
        "name": "CFEPSaveGame__WideCharToLowerCompat",
        "signature": "uint __cdecl CFEPSaveGame__WideCharToLowerCompat(uint wide_char)",
        "tokens": ("0xffff", "ASCII A-Z", "CRT__GetCharTypeMaskCompat"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "frontend-save", "wide-char"},
    },
    "0x005d0e88": {
        "name": "CRT__WcsNLen",
        "signature": "int __cdecl CRT__WcsNLen(ushort * wide_string, int max_chars)",
        "tokens": ("bounded wide-string", "CRT__LCMapStringW_AnsiCompat", "max_chars"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "crt-wide-string", "wcsnlen"},
    },
    "0x005d0eb8": {
        "name": "CRT__GetCharTypeMaskCompat",
        "signature": "uint __cdecl CRT__GetCharTypeMaskCompat(uint wide_char, uint mask)",
        "tokens": ("mask 1", "PTR_DAT_00653894", "CRT__GetStringTypeWideOrAnsiCompat_0056defa"),
        "tags": {"dinput-crt-tail-wave740", "wave740-readback-verified", "crt-wide-string", "char-type-mask"},
    },
}

DOC_TOKENS = (
    "Wave740 DInput/CRT tail",
    "dinput-crt-tail-wave740",
    "0x005d04e0 DirectInput8Create",
    "0x005d04ec CFEPSaveGame__WideStrCaseInsensitiveCompare",
    "0x005d070f CRT__VsnprintfAndTerminate_005d070f",
    "0x005d0eb8 CRT__GetCharTypeMaskCompat",
    "0x005d0f10 Unwind@005d0f10",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime input behavior proven",
    "runtime filesystem behavior proven",
    "runtime locale behavior proven",
    "runtime diagnostic text behavior proven",
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
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 30,
        "pre-instructions.tsv": 1250,
        "pre-decompile/index.tsv": 10,
        "xref-site-instructions.tsv": 630,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 30,
        "post-instructions.tsv": 1250,
        "post-decompile/index.tsv": 10,
        "post-xref-site-instructions.tsv": 630,
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
        for token in expected["tokens"]:
            require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

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
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_text = read_text(BASE / "post-xrefs.tsv")
    for token in (
        "005d04e0\tDirectInput8Create\t00513178\t00513120\tPlatformInput__InitDirectInput",
        "005d04ec\tCFEPSaveGame__WideStrCaseInsensitiveCompare\t00464ee6\t00464c50\tCFEPSaveGame__CreateSave",
        "005d070f\tCRT__VsnprintfAndTerminate_005d070f\t00599a91\t00599a74\tCFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag",
        "005d0a2a\tCFEPSaveGame__WideCharToLowerCompat\t005d0580\t005d04ec\tCFEPSaveGame__WideStrCaseInsensitiveCompare",
        "005d0eb8\tCRT__GetCharTypeMaskCompat\t005d0a5f\t005d0a2a\tCFEPSaveGame__WideCharToLowerCompat",
    ):
        require(token in xref_text, f"missing xref token: {token}", failures)

    xref_site_text = read_text(BASE / "post-xref-site-instructions.tsv")
    for token in (
        "0x00513161\t0x00513120\tPlatformInput__InitDirectInput\tPUSH\t0x800",
        "0x00513178\t0x00513120\tPlatformInput__InitDirectInput\tCALL\t0x005d04e0",
        "0x0058c92e\t0x0058c893\tCTexture__AppendDiagnosticMessage\tCALL\t0x005d070f",
        "0x005d0809\t0x005d07f4\tCRT__FSeek_Locked\tCALL\t0x005d0820",
        "0x005d0a5f\t0x005d0a2a\tCFEPSaveGame__WideCharToLowerCompat\tCALL\t0x005d0eb8",
    ):
        require(token in xref_site_text, f"missing xref-site instruction token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 30 rows",
        "post-instructions.log": "Wrote 1250 instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-xref-site-instructions.log": "Wrote 630 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=4361",
        "queue-probe.log": "Commentless functions: 1737",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 1737, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 1214, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 27, "param_N count mismatch", failures)
    high_signal = queue["priorityQueues"]["commentlessHighSignal"][0]
    require(high_signal["address"] == "0x005d0f10", "high-signal head mismatch", failures)
    require(high_signal["name"] == "Unwind@005d0f10", "high-signal name mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 4361, "quality TSV commented count mismatch", failures)
    require(strict_clean == 4303, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 166988679, "backup byte count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        IMPORT_DOC,
        FEP_SAVE_DOC,
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
    require("test:ghidra-dinput-crt-tail-wave740" in package_text, "missing npm probe script", failures)

    ledger_entries = read_jsonl(LEDGER)
    attempt_entries = read_jsonl(ATTEMPT_LOG)
    require(any(e.get("task") == "Wave740 DInput/CRT tail" for e in ledger_entries), "ledger missing Wave740", failures)
    require(any(e.get("task") == "Wave740 DInput/CRT tail" for e in attempt_entries), "attempt log missing Wave740", failures)


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
        print("Wave740 DInput/CRT tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0

    print("Wave740 DInput/CRT tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
