#!/usr/bin/env python3
"""Validate Wave628 CRT heap/FPU Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave628-crt-heap-fp-head"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_heap_fp_wave628_2026-05-20.md"
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
    "0x0056202e": (
        "CRT__ReallocBase",
        "void * __cdecl CRT__ReallocBase(void * ptr, uint byteCount)",
        ("realloc-family base helper", "small-block heap modes", "Static CRT heap evidence only"),
        ("crt-runtime", "heap", "small-block-heap"),
    ),
    "0x0056235d": (
        "CRT__MsizeByPointer",
        "uint __cdecl CRT__MsizeByPointer(void * ptr)",
        ("msize-family helper", "HeapSize", "Static CRT heap evidence only"),
        ("crt-runtime", "heap", "small-block-heap"),
    ),
    "0x0056244b": (
        "CRT__HandleDomainErrorAndReturnInput",
        "double __cdecl CRT__HandleDomainErrorAndReturnInput(int fpStatus, double inputValue, int controlWord)",
        ("domain-error helper", "errno to EDOM", "Static FPU/errno evidence only"),
        ("crt-runtime", "fpu-exception", "errno"),
    ),
    "0x005627ea": (
        "CRT__AdjustFloatingPointForFormatFlags",
        "bool __cdecl CRT__AdjustFloatingPointForFormatFlags(uint activeFlags, void * inOutDouble, uint controlFlags)",
        ("floating-point adjustment helper", "CRT__Frexp", "Static FPU-format evidence only"),
        ("crt-runtime", "fpu-exception", "format-output"),
    ),
    "0x00562a01": (
        "CRT__HandleFpStatusAndReturnDouble",
        "double __cdecl CRT__HandleFpStatusAndReturnDouble(int sourceKind, int fpStatus, double primaryValue, double replacementValue, double fallbackValue, int controlWord)",
        ("stale CDXTexture-labeled", "three double slots", "Static FPU/errno evidence only"),
        ("crt-runtime", "fpu-exception", "errno", "name-corrected"),
    ),
    "0x00562a89": (
        "CRT__SetErrnoForFpSourceKind",
        "void __cdecl CRT__SetErrnoForFpSourceKind(int sourceKind)",
        ("stale CDXTexture-labeled errno helper", "ERANGE (0x22)", "Static FPU/errno evidence only"),
        ("crt-runtime", "fpu-exception", "errno", "name-corrected"),
    ),
    "0x00562ab1": (
        "CRT__MapFpStatusToErrorCode",
        "int __cdecl CRT__MapFpStatusToErrorCode(int fpStatus)",
        ("table-walk mapper", "DAT_00653768", "Static FPU table evidence only"),
        ("crt-runtime", "fpu-exception", "lookup-table"),
    ),
    "0x00562ad6": (
        "CRT__MapFormatFlagsToSourceKind",
        "int __cdecl CRT__MapFormatFlagsToSourceKind(uint fpFlags)",
        ("maps floating-point format/status flag bits", "bit 0x20 to kind 5", "Static flag-mapping evidence only"),
        ("crt-runtime", "fpu-exception", "format-output"),
    ),
    "0x00562b15": (
        "CRT__BuildNormalizedDoubleFromParts",
        "double __cdecl CRT__BuildNormalizedDoubleFromParts(double valueBits, int exponentAdjust)",
        ("helper used by CRT__Frexp", "preserves sign/mantissa", "Static split-double evidence only"),
        ("crt-runtime", "fpu-classification", "frexp"),
    ),
    "0x00562b3e": (
        "CRT__ClassifyDoubleWordsCore",
        "int __cdecl CRT__ClassifyDoubleWordsCore(uint lowWord, uint highWord)",
        ("stale CFastVB-labeled", "CRT__ClassifyDoubleWords wrapper", "Static FPU-classification evidence only"),
        ("crt-runtime", "fpu-classification", "name-corrected"),
    ),
    "0x00562b98": (
        "CRT__Frexp",
        "double __cdecl CRT__Frexp(double value, int * outExponent)",
        ("frexp-family helper", "normalizes denormal mantissas", "Static FPU/frexp evidence only"),
        ("crt-runtime", "fpu-classification", "frexp"),
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


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
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
        "BADNAME:",
        "Read-back mismatch",
        "BAD:",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-wave628-dry.log",
        {
            "updated": 0,
            "skipped": 11,
            "renamed": 0,
            "would_rename": 3,
            "signature_updated": 0,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )
    require_log_summary(
        BASE / "apply-wave628-apply.log",
        {
            "updated": 11,
            "skipped": 0,
            "renamed": 3,
            "would_rename": 0,
            "signature_updated": 11,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )
    require_log_summary(
        BASE / "apply-wave628-final-dry.log",
        {
            "updated": 0,
            "skipped": 11,
            "renamed": 0,
            "would_rename": 0,
            "signature_updated": 0,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=11 found=11 missing=0",),
        "post-context-tags.log": ("rows=11 missing=0",),
        "post-context-xrefs.log": ("Wrote 23 rows",),
        "post-context-instructions.log": ("Wrote 2871 instruction rows", "targets=11 missing=0"),
        "post-context-decompile.log": ("targets=11 dumped=11 missing=0 failed=0",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2776", "Param signatures: 973"),
    }
    for log_name, tokens in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, tokens, failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_tags_and_decompile(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 11:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 11")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, _) in TARGETS.items():
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
    if len(tag_rows) != 11:
        failures.append(f"post-context-tags row count mismatch: {len(tag_rows)} != 11")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        expected_tags = {
            "static-reaudit",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "crt-heap-fp-wave628",
            *tag_tokens,
        }
        for token in expected_tags:
            if token not in tags:
                failures.append(f"{address} missing tag {token}")

    decompile_rows = read_tsv_rows(BASE / "post-decompile" / "index.tsv")
    if len(decompile_rows) != 11:
        failures.append(f"post-decompile index row count mismatch: {len(decompile_rows)} != 11")
    for row in decompile_rows:
        if row["status"] != "OK":
            failures.append(f"{row['address']} decompile status mismatch: {row['status']}")


def check_edges(failures: list[str]) -> None:
    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "0056202e\tCRT__ReallocBase\t0055df61\t0055df28\tCRT__OnexitTablePush",
        "0056235d\tCRT__MsizeByPointer\t0055df34\t0055df28\tCRT__OnexitTablePush",
        "0056244b\tCRT__HandleDomainErrorAndReturnInput\t0055e038\t0055dfe7\tCRT__RoundDoubleWithFpuChecks",
        "005627ea\tCRT__AdjustFloatingPointForFormatFlags\t005624af\t0056249f\tCRT__HandleFloatingPointExceptionByFlags",
        "00562a01\tCRT__HandleFpStatusAndReturnDouble\t00562476\t0056244b\tCRT__HandleDomainErrorAndReturnInput",
        "00562a89\tCRT__SetErrnoForFpSourceKind\t00562a60\t00562a01\tCRT__HandleFpStatusAndReturnDouble",
        "00562ab1\tCRT__MapFpStatusToErrorCode\t00562a0a\t00562a01\tCRT__HandleFpStatusAndReturnDouble",
        "00562ad6\tCRT__MapFormatFlagsToSourceKind\t005624e0\t0056249f\tCRT__HandleFloatingPointExceptionByFlags",
        "00562b15\tCRT__BuildNormalizedDoubleFromParts\t00562c1a\t00562b98\tCRT__Frexp",
        "00562b3e\tCRT__ClassifyDoubleWordsCore\t0056d1a6\t0056d18a\tCRT__ClassifyDoubleWords",
        "00562b98\tCRT__Frexp\t0056294a\t005627ea\tCRT__AdjustFloatingPointForFormatFlags",
    ):
        if token not in xrefs:
            failures.append(f"post-context-xrefs missing token: {token}")


def check_queue_backup_and_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2776,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 973,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x00562cef" or head.get("name") != "CRT__InputFormatCore":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BASE / "backup-summary.json")
    if backup.get("backupPath") != "[maintainer-local-ghidra-backup-root]\\BEA_20260520-074256_post_wave628_crt_heap_fp_verified":
        failures.append(f"backupPath mismatch: {backup.get('backupPath')}")
    if backup.get("fileCount") != 19 or int(backup.get("totalBytes", 0)) != 162139015 or backup.get("diffCount") != 0:
        failures.append(f"backup summary mismatch: {backup}")

    docs = {
        "package.json": read_text(PACKAGE_JSON),
        "public note": read_text(PUBLIC_NOTE),
        "functions index": read_text(FUNCTION_INDEX),
        "crt doc": read_text(CRT_DOC),
        "ghidra reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
        "tracking": read_text(TRACKING),
    }
    expected_doc_tokens = {
        "package.json": ("test:ghidra-crt-heap-fp-wave628",),
        "public note": ("Ghidra CRT Heap/FPU Wave628", "CRT__HandleFpStatusAndReturnDouble", "2776", "973"),
        "functions index": ("Wave628 CRT heap/FPU hardening", "0x00562cef CRT__InputFormatCore"),
        "crt doc": ("Wave628 Static Read-Back Note", "CRT__Frexp", "CRT__InputFormatCore"),
        "ghidra reference": ("Current Signature Caveat: CRT Heap/FPU Wave628", "CRT__ClassifyDoubleWordsCore"),
        "campaign": ("ghidra_crt_heap_fp_wave628_2026-05-20.md", "0x00562cef CRT__InputFormatCore"),
        "backlog": ("Ghidra CRT heap/FPU Wave628 signature/comment hardening", "DiffCount=0"),
        "ledger": ("Ghidra CRT heap/FPU Wave628 signature/comment hardening", "strict clean-signature proxy 3265/6093 = 53.59%"),
        "attempt log": ("attempt_id\":20283", "headless_java_apply_signature_comment_tags_with_three_renames_no_boundary_change"),
        "tracking": ("Wave628 hardened eleven adjacent CRT heap/FPU helper rows", "next_attempt_id\": 20284"),
    }
    for label, tokens in expected_doc_tokens.items():
        require_tokens(label, docs[label], tokens, failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run validation")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_metadata_tags_and_decompile(failures)
    check_edges(failures)
    check_queue_backup_and_docs(failures)

    if failures:
        print("Wave628 CRT heap/FPU probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave628 CRT heap/FPU probe: PASS")
    print("Verified 11 saved metadata rows, 11 tag rows, 23 xref rows, 2871 instruction rows, 11 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
