#!/usr/bin/env python3
"""Validate Wave622 CRT/CLI string Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave622-cli-crt-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_cli_string_wave622_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x0055e14f": (
        "CRT__SscanfFromString",
        "int __cdecl CRT__SscanfFromString(char * input, char * format, ...)",
        ("CRT__InputFormatCore", "records strlen(input)", "CLIParams__ParseCommandLine"),
        ("crt-cli-string-wave622", "string-scan", "varargs", "name-corrected"),
    ),
    "0x0055e183": (
        "CRT__PrintfStdoutLocked",
        "int __cdecl CRT__PrintfStdoutLocked(char * format, ...)",
        ("0x6533e0", "CRT__FormatOutputToStream", "unlock"),
        ("crt-cli-string-wave622", "formatted-output", "stdout-stream", "varargs", "name-corrected"),
    ),
    "0x0055e1c4": (
        "CRT__ParseDoubleSkippingWhitespace",
        "double __cdecl CRT__ParseDoubleSkippingWhitespace(char * text)",
        ("CRT__ParseFloatTextToFloatAndStatus", "CConsole__SetVariableByName", "locale edge cases"),
        ("crt-cli-string-wave622", "float-parser", "ctype-table", "name-corrected"),
    ),
    "0x0055e21b": (
        "CRT__ParseDecimalIntA",
        "int __cdecl CRT__ParseDecimalIntA(char * text)",
        ("optional plus/minus", "CRT__Tzset", "overflow behavior"),
        ("crt-cli-string-wave622", "decimal-parser", "ctype-table"),
    ),
    "0x0055e2a6": (
        "CRT__ParseDecimalIntA_Thunk",
        "int __cdecl CRT__ParseDecimalIntA_Thunk(char * text)",
        ("tail wrapper", "mesh suffix parsing", "CDXTexture chunk processing"),
        ("crt-cli-string-wave622", "decimal-parser", "thunk", "name-corrected"),
    ),
    "0x0055e598": (
        "ControlsUI__FormatWideStringSafe",
        "int __cdecl ControlsUI__FormatWideStringSafe(short * outWide, short * format, ...)",
        ("ControlsUI__FormatWideStringCore", "double NUL", "ControlsUI__RenderBindingsList"),
        ("crt-cli-string-wave622", "wide-format", "controls-ui", "varargs"),
    ),
    "0x0055e624": (
        "CRT__WStrCat",
        "int __cdecl CRT__WStrCat(short * destWide, short * srcWide)",
        ("terminating 16-bit zero", "copies srcWide 16-bit units", "old ControlsUI owner label"),
        ("crt-cli-string-wave622", "wide-string", "name-corrected"),
    ),
    "0x0055e64e": (
        "CRT__WStrCpy",
        "int __cdecl CRT__WStrCpy(short * destWide, short * srcWide)",
        ("terminating zero", "game-interface rendering", "IScript sound"),
        ("crt-cli-string-wave622", "wide-string"),
    ),
    "0x0055e673": (
        "CRT__ToUpperWithLocaleLock",
        "int __cdecl CRT__ToUpperWithLocaleLock(int charValue)",
        ("locale lock counter", "CRT__ToUpperWithLocale", "lock index 0x13"),
        ("crt-cli-string-wave622", "locale", "ctype-table"),
    ),
    "0x0055e6e2": (
        "CRT__ToUpperWithLocale",
        "int __cdecl CRT__ToUpperWithLocale(int charValue)",
        ("ASCII fast path", "LCMapStringA-compatible", "Direct caller"),
        ("crt-cli-string-wave622", "locale", "ctype-table"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "crt identity proven",
    "crt version proven",
    "fully recovered",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        token = token.replace("\\\\", "\\")
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_clean_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    expectations = {
        "apply-wave622-dry.log": {
            "updated": 0,
            "skipped": 10,
            "renamed": 0,
            "would_rename": 5,
            "varargs": 0,
            "missing": 0,
            "bad": 0,
        },
        "apply-wave622-apply.log": {
            "updated": 10,
            "skipped": 0,
            "renamed": 5,
            "would_rename": 0,
            "varargs": 3,
            "missing": 0,
            "bad": 0,
        },
        "apply-wave622-final-dry.log": {
            "updated": 0,
            "skipped": 10,
            "renamed": 0,
            "would_rename": 0,
            "varargs": 0,
            "missing": 0,
            "bad": 0,
        },
    }
    for name, expected in expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=10 found=10 missing=0",),
        "post-context-tags.log": ("rows=10 missing=0",),
        "post-context-xrefs.log": ("Wrote 198 rows",),
        "post-context-instructions.log": ("Wrote 610 instruction rows", "targets=10 missing=0"),
        "post-context-decompile.log": ("targets=10 dumped=10 missing=0 failed=0",),
        "post-function-quality.log": ("total_functions=6093 commented_functions=3244",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2849", "Param signatures: 1036"),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_and_edges(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 10:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 10")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, tag_tokens) in TARGETS.items():
        row = by_address.get(address)
        if not row:
            failures.append(f"post-context-metadata missing {address}")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} status mismatch: {row['status']}")
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-hardened", *tag_tokens):
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "0055e14f\tCRT__SscanfFromString\t00423d2d\t00423bc0\tCLIParams__ParseCommandLine",
        "0055e14f\tCRT__SscanfFromString\t004f57dc\t004f57b0\tCTokenArchive__ReadNextToken",
        "0055e183\tCRT__PrintfStdoutLocked\t00423caf\t00423bc0\tCLIParams__ParseCommandLine",
        "0055e183\tCRT__PrintfStdoutLocked\t0056f876\t0056f620\tCFastVB__BuildTriangleAdjacency",
        "0055e1c4\tCRT__ParseDoubleSkippingWhitespace\t0042a9cd\t0042a7b0\tCConsole__SetVariableByName",
        "0055e21b\tCRT__ParseDecimalIntA\t0055e2aa\t0055e2a6\tCRT__ParseDecimalIntA_Thunk",
        "0055e2a6\tCRT__ParseDecimalIntA_Thunk\t004e25c5\t004e2530\tCEffect__LoadSFXFile",
        "0055e598\tControlsUI__FormatWideStringSafe\t00455821\t00455010\tControlsUI__RenderBindingsList",
        "0055e624\tCRT__WStrCat\t00464c03\t00464bc0\tCFEPSaveGame__AskIfYouWantToDelete",
        "0055e64e\tCRT__WStrCpy\t00465a7b\t00465a20\tTextLayout__WrapWideTextToFixedLines",
        "0055e673\tCRT__ToUpperWithLocaleLock\t0056cac3\t0056c998\tCRT__StrToLongWithBaseAndLocaleCType",
        "0055e6e2\tCRT__ToUpperWithLocale\t0055e6bf\t0055e673\tCRT__ToUpperWithLocaleLock",
    ):
        require_tokens("post-context-xrefs.tsv", xrefs, (token,), failures)

    instructions = read_text(BASE / "post-context-instructions.tsv")
    for token in (
        "0x0055e14f\t0x0055e14f\tAFTER\t15\t0x0055e179\t0x0055e14f\tCRT__SscanfFromString\tCALL\t0x00562cef",
        "0x0055e183\t0x0055e183\tAFTER\t14\t0x0055e1a5\t0x0055e183\tCRT__PrintfStdoutLocked\tCALL\t0x00561834",
        "0x0055e1c4\t0x0055e1c4\tAFTER\t31\t0x0055e20d\t0x0055e1c4\tCRT__ParseDoubleSkippingWhitespace\tCALL\t0x005638d2",
        "0x0055e2a6\t0x0055e2a6\tAFTER\t1\t0x0055e2aa\t0x0055e2a6\tCRT__ParseDecimalIntA_Thunk\tCALL\t0x0055e21b",
        "0x0055e598\t0x0055e598\tAFTER\t14\t0x0055e5c1\t0x0055e598\tControlsUI__FormatWideStringSafe\tCALL\t0x00565083",
        "0x0055e624\t0x0055e624\tAFTER\t10\t0x0055e63d\t0x0055e624\tCRT__WStrCat\tMOV\tSI, word ptr [EDX]",
        "0x0055e673\t0x0055e673\tAFTER\t28\t0x0055e6bf\t0x0055e673\tCRT__ToUpperWithLocaleLock\tCALL\t0x0055e6e2",
    ):
        require_tokens("post-context-instructions.tsv", instructions, (token,), failures)


def check_decompiles(failures: list[str]) -> None:
    decomp_dir = BASE / "post-context-decompile"
    expected_files = {
        "0055e14f_CRT__SscanfFromString.c": ("CRT__InputFormatCore", "_strlen(input)", "return iVar1"),
        "0055e183_CRT__PrintfStdoutLocked.c": (
            "CRT__FormatOutputToStream",
            "CRT__UnlockRouteByIndex",
            "return iVar2",
        ),
        "0055e1c4_CRT__ParseDoubleSkippingWhitespace.c": (
            "CRT__ParseFloatTextToFloatAndStatus",
            "return *(double *)",
        ),
        "0055e21b_CRT__ParseDecimalIntA.c": (
            "iVar3 = (uVar4 - 0x30) + iVar3 * 10",
            "return iVar3",
        ),
        "0055e2a6_CRT__ParseDecimalIntA_Thunk.c": ("CRT__ParseDecimalIntA(text)", "return iVar1"),
        "0055e598_ControlsUI__FormatWideStringSafe.c": (
            "ControlsUI__FormatWideStringCore",
            "short *outWide",
        ),
        "0055e624_CRT__WStrCat.c": ("return (int)psVar2", "*destWide = sVar1"),
        "0055e64e_CRT__WStrCpy.c": ("return (int)psVar1", "*destWide = sVar2"),
        "0055e673_CRT__ToUpperWithLocaleLock.c": (
            "CRT__ToUpperWithLocale(charValue)",
            "CRT__UnlockByIndex(0x13)",
        ),
        "0055e6e2_CRT__ToUpperWithLocale.c": ("CRT__LCMapStringA_Compat", "return charValue"),
    }
    for name, tokens in expected_files.items():
        text = read_text(decomp_dir / name)
        require_tokens(name, text, tokens, failures)
        for token in OVERCLAIM_TOKENS:
            if token in text.lower():
                failures.append(f"{name} overclaims: {token}")


def check_docs_and_state(failures: list[str]) -> None:
    doc_tokens = {
        PUBLIC_NOTE: (
            "Ghidra CRT/CLI String Wave622 Readiness Note",
            "CRT__SscanfFromString",
            "3244/6093 = 53.24%",
            "0x0055e7ae Sort__QuickSortGeneric",
            "full format/parser/locale semantics",
        ),
        FUNCTION_INDEX: ("Latest saved-correction note: Wave622", "CRT__PrintfStdoutLocked", "CRT__ToUpperWithLocale"),
        CRT_DOC: ("Wave622 Static Read-Back Note", "0x0055e14f", "3244` commented"),
        GHIDRA_REFERENCE: ("0x0055e14f | CRT__SscanfFromString", "0x0055e624 | CRT__WStrCat"),
        CAMPAIGN: ("after Wave622", "ghidra_crt_cli_string_wave622_2026-05-20.md", "1036` `param_N`"),
        BACKLOG: ("Ghidra CRT/CLI string Wave622 signature/comment hardening", "updated=10 skipped=0 renamed=5"),
        LEDGER: ("Ghidra CRT/CLI string Wave622 signature/comment hardening", "strict clean-signature proxy 3192/6093 = 52.39%"),
        ATTEMPT_LOG: ("attempt_id\":20277", "headless_java_apply_signature_comment_tags_with_five_renames_no_boundary_change"),
        TRACKING: ("Wave622 hardened ten CRT/CLI string", "next_attempt_id\": 20278"),
        PACKAGE_JSON: ("test:ghidra-crt-cli-string-wave622", "tools\\\\ghidra_crt_cli_string_wave622_probe.py --check"),
    }
    for path, tokens in doc_tokens.items():
        text = read_text(path)
        require_tokens(path.name, text, tokens, failures)

    for path in (PUBLIC_NOTE, CRT_DOC, CAMPAIGN):
        lowered = read_text(path).lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.name} overclaims: {token}")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2849,
        "undefinedSignatureCount": 1218,
        "paramSignatureCount": 1036,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0055e7ae" or head.get("name") != "Sort__QuickSortGeneric":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("DiffCount") != 0:
        failures.append(f"backup DiffCount mismatch: {backup.get('DiffCount')}")
    if backup.get("SourceFileCount") != 19 or backup.get("BackupFileCount") != 19:
        failures.append("backup file count mismatch")
    if int(backup.get("SourceBytes", 0)) != 161909639 or int(backup.get("BackupBytes", 0)) != 161909639:
        failures.append("backup byte count mismatch")
    require_tokens("backup path", backup.get("BackupPath", ""), ("BEA_20260520-045112_post_wave622_cli_crt_string_verified",), failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    checks = (
        check_logs,
        check_metadata_tags_and_edges,
        check_decompiles,
        check_docs_and_state,
        check_queue_and_backup,
    )
    for check in checks:
        try:
            check(failures)
        except Exception as exc:  # pragma: no cover - diagnostic path
            failures.append(f"{check.__name__} raised {type(exc).__name__}: {exc}")

    if failures:
        print("Wave622 CRT/CLI string probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave622 CRT/CLI string probe: PASS")
    print("Verified 10 saved metadata rows, tags, xrefs, instructions, decompiles, queue telemetry, docs, logs, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
