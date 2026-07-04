#!/usr/bin/env python3
"""Validate Wave645 CRT locale/string-tail Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave645-crt-locale-string-tail"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_locale_string_tail_wave645_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CRT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "crt-seh.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"

TARGETS = {
    "0x0056b368": (
        "CRT__WriteWideCharToStreamWithConversion",
        "uint __cdecl CRT__WriteWideCharToStreamWithConversion(uint wideChar, void * stream)",
        ("wide character", "locale/codepage", "Wave645"),
        ("crt-runtime", "wide-char-output", "stream", "locale-codepage"),
    ),
    "0x0056b4f2": (
        "CRT__LoadTimeLocaleInfoTable",
        "uint __cdecl CRT__LoadTimeLocaleInfoTable(void * timeLocaleInfo)",
        ("date/time locale", "GetLocaleInfo", "Wave645"),
        ("crt-runtime", "locale", "time-locale", "GetLocaleInfoA"),
    ),
    "0x0056bba5": (
        "CRT__NormalizeLocaleGroupingStringInPlace",
        "void __cdecl CRT__NormalizeLocaleGroupingStringInPlace(char * groupingText)",
        ("locale grouping string", "semicolon separators", "Wave645"),
        ("crt-runtime", "locale", "grouping-string", "stale-owner-corrected"),
    ),
    "0x0056bca7": (
        "CRT__LoadMonetaryLocaleInfoTable",
        "uint __cdecl CRT__LoadMonetaryLocaleInfoTable(void * monetaryLocaleInfo)",
        ("monetary locale", "grouping metadata", "Wave645"),
        ("crt-runtime", "locale", "monetary-locale", "stale-owner-corrected"),
    ),
    "0x0056bdc9": (
        "CRT__FreeLocaleBufferSet",
        "void __cdecl CRT__FreeLocaleBufferSet(void * localeBufferSet)",
        ("locale buffer set", "heap-backed string slots", "Wave645"),
        ("crt-runtime", "locale", "heap-free", "buffer-set"),
    ),
    "0x0056c060": (
        "CRT__StrCSpn",
        "int __cdecl CRT__StrCSpn(char * text, char * rejectSet)",
        ("strcspn-style", "256-bit reject-set bitmap", "Wave645"),
        ("crt-runtime", "string", "strcspn", "bitmap-search"),
    ),
    "0x0056c0a0": (
        "CRT__StrPBrk",
        "char * __cdecl CRT__StrPBrk(char * text, char * acceptSet)",
        ("strpbrk-style", "256-bit accept-set bitmap", "Wave645"),
        ("crt-runtime", "string", "strpbrk", "bitmap-search"),
    ),
    "0x0056c0da": (
        "CRT__ResolveLocaleNameAndMetadata_NlsCore",
        "int __cdecl CRT__ResolveLocaleNameAndMetadata_NlsCore(char * localeTriple, ushort * outLocaleIds, char * outResolvedTriple)",
        ("NLS-backed locale resolver core", "language/country aliases", "Wave645"),
        ("crt-runtime", "locale", "NLS", "GetLocaleInfoA"),
    ),
    "0x0056c257": (
        "CRT__LocaleAliasBinarySearchRemap",
        "void __cdecl CRT__LocaleAliasBinarySearchRemap(void * aliasTable, int highIndex, char * * nameSlot)",
        ("binary-searches", "locale alias table", "Wave645"),
        ("crt-runtime", "locale", "alias-table", "binary-search"),
    ),
    "0x0056c336": (
        "CRT__EnumLocalesCallback_MatchLanguageCountry",
        "int __stdcall CRT__EnumLocalesCallback_MatchLanguageCountry(char * localeIdText)",
        ("EnumLocales callback", "country and language names", "Wave645"),
        ("crt-runtime", "locale", "EnumLocalesA", "language-country"),
    ),
    "0x0056c590": (
        "CRT__EnumLocalesCallback_MatchLanguageOnly",
        "int __stdcall CRT__EnumLocalesCallback_MatchLanguageOnly(char * localeIdText)",
        ("EnumLocales callback", "language-only locale", "Wave645"),
        ("crt-runtime", "locale", "EnumLocalesA", "language-only"),
    ),
    "0x0056c684": (
        "CRT__ValidateCodePageAgainstLocale",
        "int __stdcall CRT__ValidateCodePageAgainstLocale(char * localeIdText)",
        ("EnumLocales-style callback", "validates the codepage", "Wave645"),
        ("crt-runtime", "locale", "codepage", "EnumLocalesA"),
    ),
    "0x0056c724": (
        "CRT__ResolveLocaleCodePageToken",
        "int __cdecl CRT__ResolveLocaleCodePageToken(char * codePageToken)",
        ("ACP/OCP/numeric locale codepage token", "decimal parser result", "Wave645"),
        ("crt-runtime", "locale", "codepage", "ACP-OCP"),
    ),
    "0x0056c78a": (
        "CRT__IsCodePageSupportedByLocaleMap",
        "int __cdecl CRT__IsCodePageSupportedByLocaleMap(int localeId)",
        ("locale-id exclusion table", "returns zero", "Wave645"),
        ("crt-runtime", "locale", "codepage", "locale-map"),
    ),
    "0x0056c7a9": (
        "CRT__ValidateLocaleLanguageMatch",
        "int __cdecl CRT__ValidateLocaleLanguageMatch(int localeId, int requireExactLanguage)",
        ("requested language", "prefix-only matches", "Wave645"),
        ("crt-runtime", "locale", "language-match", "LCID"),
    ),
    "0x0056c841": (
        "CRT__GetLocaleInfoACompatFallback",
        "int __stdcall CRT__GetLocaleInfoACompatFallback(uint localeId, int localeInfoType, char * outBuffer, int outChars)",
        ("compatibility GetLocaleInfoA wrapper", "internal sorted table", "Wave645"),
        ("crt-runtime", "locale", "GetLocaleInfoA", "compatibility-table"),
    ),
    "0x0056c927": (
        "CRT__ParseHexLocaleIdString",
        "int __cdecl CRT__ParseHexLocaleIdString(char * localeIdText)",
        ("hexadecimal locale-id string", "uppercase and lowercase A-F", "Wave645"),
        ("crt-runtime", "locale", "hex-parser", "LCID"),
    ),
    "0x0056c960": (
        "CRT__CountAlphaPrefix",
        "int __cdecl CRT__CountAlphaPrefix(char * text)",
        ("ASCII alphabetic prefix", "locale language string", "Wave645"),
        ("crt-runtime", "locale", "string", "alpha-prefix"),
    ),
    "0x0056c981": (
        "CRT__StrToLong",
        "int __cdecl CRT__StrToLong(char * text, char * * endPtr, int base)",
        ("strtol-style wrapper", "mode flag zero", "Wave645"),
        ("crt-runtime", "string-to-long", "strtol", "numeric-parser"),
    ),
    "0x0056cb9d": (
        "CRT__StrToLongWithBaseAndLocaleCType_Mode1Thunk",
        "int __cdecl CRT__StrToLongWithBaseAndLocaleCType_Mode1Thunk(char * text, char * * endPtr, int base)",
        ("mode flag one", "locale-aware string-to-long core", "Wave645"),
        ("crt-runtime", "string-to-long", "mode-flag", "numeric-parser"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "crt-locale-string-tail-wave645",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
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
        failures.append(f"{path.name} missing SUMMARY line")
        return {}
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-succeeded marker")
    if "LockException" in text:
        failures.append(f"{path.name} contains LockException")
    return values


def expect_summary(label: str, actual: dict[str, int], expected: dict[str, int], failures: list[str]) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{label} expected {key}={value}, saw {actual.get(key)}")


def check_metadata(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-metadata.tsv")}
    if set(rows) != set(TARGETS):
        failures.append(f"post-metadata target set mismatch: {sorted(rows)}")
    for address, (name, signature, comment_tokens, _tags) in TARGETS.items():
        row = rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], set(comment_tokens), failures)
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status is {row.get('status')}")


def check_tags(failures: list[str]) -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-tags.tsv")}
    for address, (_name, _signature, _comment_tokens, tags) in TARGETS.items():
        row = rows.get(address)
        if not row:
            failures.append(f"{address} missing tag row")
            continue
        actual = {tag for tag in row["tags"].split(";") if tag}
        missing = (COMMON_TAGS | set(tags)) - actual
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")


def check_counts(failures: list[str]) -> None:
    checks = [
        (BASE / "post-metadata.tsv", 20, "metadata rows"),
        (BASE / "post-tags.tsv", 20, "tag rows"),
        (BASE / "post-xrefs.tsv", 33, "xref rows"),
        (BASE / "post-instructions.tsv", 6420, "instruction rows"),
    ]
    for path, expected, label in checks:
        rows = read_tsv_rows(path)
        if len(rows) != expected:
            failures.append(f"{label}: expected {expected}, saw {len(rows)}")
    decomp = read_text(BASE / "export-post-decompile.log")
    require_tokens("export-post-decompile.log", decomp, ("targets=20 dumped=20 missing=0 failed=0", "REPORT: Save succeeded"), failures)
    for address, (name, _signature, _comment_tokens, _tags) in TARGETS.items():
        file_name = f"{address[2:]}_{name}.c"
        if not (BASE / "post-decompile" / file_name).is_file():
            failures.append(f"missing decompile file: {file_name}")


def check_logs(failures: list[str]) -> None:
    dry = parse_log_summary(BASE / "apply-dry.log", failures)
    apply = parse_log_summary(BASE / "apply.log", failures)
    final_dry = parse_log_summary(BASE / "apply-final-dry.log", failures)
    expect_summary(
        "dry",
        dry,
        {"updated": 0, "skipped": 20, "renamed": 0, "would_rename": 13, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "apply",
        apply,
        {"updated": 20, "skipped": 0, "renamed": 13, "would_rename": 0, "signature_updated": 20, "missing": 0, "bad": 0},
        failures,
    )
    expect_summary(
        "final dry",
        final_dry,
        {"updated": 0, "skipped": 20, "renamed": 0, "would_rename": 0, "signature_updated": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    expected_quality = {
        "commentlessFunctionCount": 2624,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 836,
    }
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} expected {value}, saw {quality.get(key)}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions expected 6093, saw {queue.get('totalFunctions')}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head["address"] != "0x0056ce69" or head["name"] != "CRT__IsInDst_WrapperLocked":
        failures.append(f"unexpected next queue head: {head}")

    rows = read_tsv_rows(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    if commented != 3469:
        failures.append(f"queue TSV commented rows expected 3469, saw {commented}")

    backup = read_json(BASE / "backup-summary.json")
    if backup.get("backupRoot") != "[maintainer-local-ghidra-backup-root]\\BEA_20260520-152241_post_wave645_crt_locale_string_tail_verified":
        failures.append(f"backupRoot mismatch: {backup.get('backupRoot')}")
    if backup.get("fileCount") != 19 or backup.get("totalBytes") != 162761607 or backup.get("diffCount") != 0:
        failures.append(f"backup summary mismatch: {backup}")


def check_docs_and_logs(failures: list[str]) -> None:
    public_note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        public_note,
        (
            "Ghidra CRT Locale/String Tail Wave645",
            "CRT__LoadTimeLocaleInfoTable",
            "CRT__StrToLongWithBaseAndLocaleCType_Mode1Thunk",
            "Queue after Wave645: `6093` total functions, `3469` commented, `2624` commentless",
            "Exact MSVC CRT version",
            "remain unproven",
        ),
        failures,
    )

    docs = {
        "functions/_index.md": read_text(FUNCTION_INDEX),
        "crt-seh.md": read_text(CRT_DOC),
        "GHIDRA-REFERENCE.md": read_text(GHIDRA_REFERENCE),
        "static-reaudit-campaign.md": read_text(CAMPAIGN),
        "MCP-MUTATION-BACKLOG.md": read_text(BACKLOG),
        "function_mutation_ledger.jsonl": read_text(LEDGER),
        "function_mutation_attempt_log.jsonl": read_text(ATTEMPT_LOG),
    }
    required = (
        "Wave645",
        "CRT__NormalizeLocaleGroupingStringInPlace",
        "CRT__LoadMonetaryLocaleInfoTable",
        "CRT__ResolveLocaleNameAndMetadata_NlsCore",
        "0x0056ce69 CRT__IsInDst_WrapperLocked",
    )
    for label, text in docs.items():
        require_tokens(label, text, required, failures)
    require_tokens(
        "package.json",
        read_text(PACKAGE_JSON),
        ("test:ghidra-crt-locale-string-tail-wave645", "ghidra_crt_locale_string_tail_wave645_probe.py"),
        failures,
    )

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20301:
        failures.append(f"tracking next_attempt_id expected 20301, saw {tracking.get('next_attempt_id')}")
    if "Wave645" not in " ".join(tracking.get("notes", [])):
        failures.append("tracking notes missing Wave645")

    for label, text in [("public note", public_note), *docs.items()]:
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} contains overclaim token: {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return nonzero on validation failure")
    args = parser.parse_args()

    failures: list[str] = []
    for check in (
        check_metadata,
        check_tags,
        check_counts,
        check_logs,
        check_queue_and_backup,
        check_docs_and_logs,
    ):
        try:
            check(failures)
        except Exception as exc:  # noqa: BLE001 - probe should aggregate failures.
            failures.append(f"{check.__name__}: {exc}")

    print("Wave645 CRT locale/string-tail probe")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print("Status: PASS")
    print(f"Targets: {len(TARGETS)}")
    print("Queue: 6093 total, 2624 commentless, 1217 exact-undefined, 836 param_N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
