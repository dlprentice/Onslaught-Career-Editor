#!/usr/bin/env python3
"""Validate Wave627 CRT/FPU/format Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave627-crt-fpu-format-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_fpu_format_wave627_2026-05-20.md"
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
    "0x00561618": (
        "CRT__ExtractFiniteExponentMaskOrPassThrough",
        "uint __cdecl CRT__ExtractFiniteExponentMaskOrPassThrough(uint unusedLowDword, uint highDword)",
        ("finite-exponent mask helper", "highDword & 0x7ff00000", "Inf/NaN exponent patterns"),
        ("crt-runtime", "fpu-classification", "name-corrected"),
        True,
    ),
    "0x0056162e": (
        "CRT__MathErrorHook_NoOp",
        "void CRT__MathErrorHook_NoOp(void)",
        ("compact math-error hook/return shim", "0x27f", "nonstandard stack cleanup"),
        ("crt-runtime", "custom-stack", "fpu-control"),
        False,
    ),
    "0x0056163b": (
        "__math_exit",
        "undefined __math_exit(void)",
        ("Visual Studio __math_exit library-match helper", "saved FPU control word", "nonstandard stack cleanup"),
        ("crt-runtime", "custom-stack", "fpu-control", "library-match"),
        False,
    ),
    "0x00561679": (
        "CRT__HandleFpuExceptionForMathOp",
        "void __fastcall CRT__HandleFpuExceptionForMathOp(int unusedEcx, int mathOpId)",
        ("FPU exception handler", "mathOpId is 0x1d", "Static FPU-exception evidence only"),
        ("crt-runtime", "fpu-control", "math-error"),
        True,
    ),
    "0x0056171c": (
        "CRT__FlsBuf",
        "uint __cdecl CRT__FlsBuf(uint character, void * stream)",
        ("flush-buffer helper", "CRT__WriteFdTextMode_Locking_00567505", "0xffffffff"),
        ("crt-runtime", "file-buffer", "stream-output"),
        True,
    ),
    "0x00561834": (
        "CRT__FormatOutputToStream",
        "int __cdecl CRT__FormatOutputToStream(void * outputTarget, char * format, void * argList)",
        ("printf-family core formatter", "adjacent arg-list readers", "output helpers"),
        ("crt-runtime", "format-output", "printf-core"),
        True,
    ),
    "0x00561f75": (
        "CRT__PutCharToStreamAndCount",
        "void __cdecl CRT__PutCharToStreamAndCount(uint character, void * stream, int * count)",
        ("single-byte output/count helper", "CRT__FlsBuf", "sets count to -1"),
        ("crt-runtime", "format-output", "stream-output"),
        True,
    ),
    "0x00561faa": (
        "CRT__PutCharRepeatedToStream",
        "void __cdecl CRT__PutCharRepeatedToStream(uint character, int repeatCount, void * stream, int * count)",
        ("repeated-byte output helper", "padding", "count becomes -1"),
        ("crt-runtime", "format-output", "stream-output"),
        True,
    ),
    "0x00561fdb": (
        "CRT__PutStringToStream",
        "void __cdecl CRT__PutStringToStream(char * text, int length, void * stream, int * count)",
        ("bounded string output helper", "CRT__PutCharToStreamAndCount", "count becomes -1"),
        ("crt-runtime", "format-output", "stream-output"),
        True,
    ),
    "0x00562013": (
        "CRT__ReadIntAndAdvanceArgList",
        "int __cdecl CRT__ReadIntAndAdvanceArgList(void * argListPtr)",
        ("printf-style arg-list reader", "advances the caller-owned argument cursor by four bytes", "ControlsUI__FormatWideStringCore"),
        ("crt-runtime", "format-output", "name-corrected", "vararg-reader"),
        True,
    ),
    "0x00562020": (
        "CRT__ReadFormatWordAndAdvance",
        "int __cdecl CRT__ReadFormatWordAndAdvance(void * argListPtr)",
        ("low word of the next 32-bit argument slot", "stale upper EAX bits", "vararg-reader"),
        ("crt-runtime", "format-output", "vararg-reader"),
        True,
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
        BASE / "apply-wave627-dry.log",
        {
            "updated": 0,
            "skipped": 11,
            "renamed": 0,
            "would_rename": 2,
            "signature_updated": 0,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )
    require_log_summary(
        BASE / "apply-wave627-apply.log",
        {
            "updated": 11,
            "skipped": 0,
            "renamed": 2,
            "would_rename": 0,
            "signature_updated": 9,
            "missing": 0,
            "bad": 0,
        },
        failures,
    )
    require_log_summary(
        BASE / "apply-wave627-final-dry.log",
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
        "post-context-xrefs.log": ("Wrote 63 rows",),
        "post-context-instructions.log": ("Wrote 979 instruction rows", "targets=11 missing=0"),
        "post-context-decompile.log": ("targets=11 dumped=11 missing=0 failed=0",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2787", "Param signatures: 984"),
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

    for address, (name, signature, comment_tokens, _, _) in TARGETS.items():
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
    for address, (_, _, _, tag_tokens, signature_hardened) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        expected_tags = {
            "static-reaudit",
            "retail-binary-evidence",
            "comment-hardened",
            "crt-fpu-format-wave627",
            *tag_tokens,
        }
        if signature_hardened:
            expected_tags.add("signature-hardened")
        else:
            if "signature-hardened" in tags:
                failures.append(f"{address} unexpectedly has signature-hardened tag")
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
        "00561618\tCRT__ExtractFiniteExponentMaskOrPassThrough\t0055dcb6\t0055dcb0\tOID__AcosWrapper",
        "0056162e\tCRT__MathErrorHook_NoOp\t0055fac4\t0055fa62\tCRT__PowCoreWithFpuGuards",
        "0056163b\t__math_exit\t0055f3e0\t0055f39d\tCRT__AcosCoreWithFpuGuards",
        "00561679\tCRT__HandleFpuExceptionForMathOp\t0055fad5\t0055fa62\tCRT__PowCoreWithFpuGuards",
        "0056171c\tCRT__FlsBuf\t00561f92\t00561f75\tCRT__PutCharToStreamAndCount",
        "00561834\tCRT__FormatOutputToStream\t0055e1a5\t0055e183\tCRT__PrintfStdoutLocked",
        "00561f75\tCRT__PutCharToStreamAndCount\t00561fc4\t00561faa\tCRT__PutCharRepeatedToStream",
        "00561faa\tCRT__PutCharRepeatedToStream\t00561e8e\t00561834\tCRT__FormatOutputToStream",
        "00561fdb\tCRT__PutStringToStream\t00561ea4\t00561834\tCRT__FormatOutputToStream",
        "00562013\tCRT__ReadIntAndAdvanceArgList\t00565168\t00565083\tControlsUI__FormatWideStringCore",
        "00562020\tCRT__ReadFormatWordAndAdvance\t00561afb\t00561834\tCRT__FormatOutputToStream",
    ):
        if token not in xrefs:
            failures.append(f"post-context-xrefs missing token: {token}")


def check_queue_backup_and_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2787,
        "undefinedSignatureCount": 1217,
        "paramSignatureCount": 984,
    }
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue["priorityQueues"]["commentlessHighSignal"][0]
    if head.get("address") != "0x0056202e" or head.get("name") != "CRT__ReallocBase":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupPath") != "[maintainer-local-ghidra-backup-root]\\BEA_20260520-070942_post_wave627_crt_fpu_format_verified":
        failures.append(f"backupPath mismatch: {backup.get('backupPath')}")
    if backup.get("fileCount") != 19 or int(backup.get("totalBytes", 0)) != 162106247 or backup.get("diffCount") != 0:
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
        "package.json": ("test:ghidra-crt-fpu-format-wave627",),
        "public note": ("Ghidra CRT/FPU/Format Wave627", "CRT__ReadIntAndAdvanceArgList", "2787", "984"),
        "functions index": ("Wave627 CRT/FPU/format hardening", "0x0056202e CRT__ReallocBase"),
        "crt doc": ("Wave627 Static Read-Back Note", "CRT__ReadIntAndAdvanceArgList", "custom-stack"),
        "ghidra reference": ("Current Signature Caveat: CRT/FPU/Format Wave627", "CRT__FormatOutputToStream"),
        "campaign": ("ghidra_crt_fpu_format_wave627_2026-05-20.md", "0x0056202e CRT__ReallocBase"),
        "backlog": ("Ghidra CRT/FPU/format Wave627 signature/comment hardening", "DiffCount=0"),
        "ledger": ("Ghidra CRT/FPU/format Wave627 signature/comment hardening", "strict clean-signature proxy 3254/6093 = 53.41%"),
        "attempt log": ("attempt_id\":20282", "headless_java_apply_signature_comment_tags_with_two_renames_two_custom_stack_comment_only_no_boundary_change"),
        "tracking": ("Wave627 hardened eleven adjacent CRT/FPU/printf-format helper rows", "next_attempt_id\": 20283"),
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
        print("Wave627 CRT/FPU/format probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave627 CRT/FPU/format probe: PASS")
    print("Verified 11 saved metadata rows, 11 tag rows, 63 xref rows, 979 instruction rows, 11 decompile rows, queue telemetry, backup summary, logs, and docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
