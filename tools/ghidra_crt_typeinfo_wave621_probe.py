#!/usr/bin/env python3
"""Validate Wave621 CRT/type_info Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave621-crt-typeinfo-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_crt_typeinfo_wave621_2026-05-20.md"
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
    "0x0055dac5": (
        "type_info__dtor",
        "void __fastcall type_info__dtor(void * typeInfo)",
        ("type_info::vftable", "CRT index 0x1b", "CRT__FreeBase"),
        ("crt-typeinfo-wave621", "type-info", "type-info-dtor", "name-corrected"),
    ),
    "0x0055daee": (
        "type_info__scalar_deleting_dtor",
        "void * __thiscall type_info__scalar_deleting_dtor(void * this, uint deleteFlags)",
        ("deleteFlags bit 0", "OID__FreeObject_Callback", "ret 0x4"),
        ("crt-typeinfo-wave621", "type-info", "scalar-deleting-dtor", "name-corrected"),
    ),
    "0x0055db0a": (
        "CRT__EhVectorDestructorIterator_WithUnwind",
        "void __stdcall CRT__EhVectorDestructorIterator_WithUnwind(void * array, int elemSize, int count, void * dtor)",
        ("owner correction", "array + elemSize*count", "CRT__EhVectorDestructorIterator_IfNoException"),
        ("crt-typeinfo-wave621", "crt-runtime", "eh-vector-destructor", "owner-correction", "name-corrected"),
    ),
    "0x0055dccd": (
        "CRT__Acos",
        "double __cdecl CRT__Acos(int lowWord, uint highWord)",
        ("FPU control-word", "OID__AcosWrapper", "math error"),
        ("crt-typeinfo-wave621", "crt-runtime", "math-helper", "fpu-control"),
    ),
    "0x0055dda8": (
        "CRT__CExit",
        "void __cdecl CRT__CExit(int exitCode)",
        ("CRT__DoExit", "exitCode", "CFastVB__ParserContext_Shutdown"),
        ("crt-typeinfo-wave621", "crt-runtime", "exit-helper"),
    ),
    "0x0055ddca": (
        "CRT__DoExit",
        "void __cdecl CRT__DoExit(uint exitCode, int skipOnexitCallbacks, int returnToCaller)",
        ("onexit table", "ExitProcess", "0x00622b2c-0x00622b38"),
        ("crt-typeinfo-wave621", "crt-runtime", "exit-helper", "onexit-table"),
    ),
    "0x0055de81": (
        "CRT__InvokeFunctionPointerRange",
        "void __cdecl CRT__InvokeFunctionPointerRange(void * begin, void * end)",
        ("4-byte function-pointer slots", "begin to end", "non-null"),
        ("crt-typeinfo-wave621", "crt-runtime", "function-pointer-range"),
    ),
    "0x0055df28": (
        "CRT__OnexitTablePush",
        "int __cdecl CRT__OnexitTablePush(int callback)",
        ("DAT_009d4610", "CRT__ReallocBase", "allocation failure"),
        ("crt-typeinfo-wave621", "crt-runtime", "onexit-table", "crt-lock"),
    ),
    "0x0055dfa6": (
        "CRT__RegisterOnexitFunction",
        "int __cdecl CRT__RegisterOnexitFunction(int callback)",
        ("CRT__OnexitTablePush", "success 0", "failure to -1"),
        ("crt-typeinfo-wave621", "crt-runtime", "onexit-table"),
    ),
    "0x0055dfe7": (
        "CRT__RoundDoubleWithFpuChecks",
        "double __cdecl CRT__RoundDoubleWithFpuChecks(double value)",
        ("FPU control word", "FRNDINT", "math handlers"),
        ("crt-typeinfo-wave621", "crt-runtime", "math-helper", "fpu-control"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "msvc crt version proven",
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
        "Read-back",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    expectations = {
        "apply-wave621-dry.log": {"updated": 0, "skipped": 10, "renamed": 0, "would_rename": 3, "missing": 0, "bad": 0},
        "apply-wave621-apply.log": {"updated": 10, "skipped": 0, "renamed": 3, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave621-final-dry.log": {"updated": 0, "skipped": 10, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    }
    for name, expected in expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "post-context-metadata.log": ("targets=10 found=10 missing=0",),
        "post-context-tags.log": ("rows=10 missing=0",),
        "post-context-xrefs.log": ("Wrote 246 rows",),
        "post-context-instructions.log": ("Wrote 490 instruction rows", "targets=10 missing=0"),
        "post-context-decompile.log": ("targets=10 dumped=10 missing=0 failed=0",),
        "post-function-quality.log": ("total_functions=6093 commented_functions=3234",),
        "queue-probe.log": ("Status: PASS", "Commentless functions: 2859", "Param signatures: 1046"),
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
        "0055dac5\ttype_info__dtor\t0055daf1\t0055daee\ttype_info__scalar_deleting_dtor",
        "0055daee\ttype_info__scalar_deleting_dtor\t005e5aa4\t<none>\t<no_function>\tDATA",
        "0055db0a\tCRT__EhVectorDestructorIterator_WithUnwind\t005506f9\t005506e0\tCDXPatchManager__Destroy",
        "0055dccd\tCRT__Acos\t0055dcbb\t0055dcb0\tOID__AcosWrapper",
        "0055ddca\tCRT__DoExit\t0055ddb0\t0055dda8\tCRT__CExit",
        "0055de81\tCRT__InvokeFunctionPointerRange\t0055de39\t0055ddca\tCRT__DoExit",
        "0055df28\tCRT__OnexitTablePush\t0055dfaa\t0055dfa6\tCRT__RegisterOnexitFunction",
    ):
        require_tokens("post-context-xrefs.tsv", xrefs, (token,), failures)

    instructions = read_text(BASE / "post-context-instructions.tsv")
    for token in (
        "0x0055daee\t0x0055daee\tAFTER\t11\t0x0055db0a\t0x0055db0a\tCRT__EhVectorDestructorIterator_WithUnwind\tPUSH\tEBP",
        "0x0055db0a\t0x0055db0a\tAFTER\t22\t0x0055db4c\t0x0055db0a\tCRT__EhVectorDestructorIterator_WithUnwind\tCALL\tdword ptr [EBP + 0x14]",
        "0x0055db0a\t0x0055db0a\tAFTER\t26\t0x0055db5c\t0x0055db0a\tCRT__EhVectorDestructorIterator_WithUnwind\tCALL\t0x0055db72",
        "0x0055dda8\t0x0055dda8\tAFTER\t3\t0x0055ddb0\t0x0055dda8\tCRT__CExit\tCALL\t0x0055ddca",
        "0x0055ddca\t0x0055ddca\tAFTER\t27\t0x0055de21\t0x0055ddca\tCRT__DoExit\tCALL\tEAX",
        "0x0055ddca\t0x0055ddca\tAFTER\t34\t0x0055de39\t0x0055ddca\tCRT__DoExit\tCALL\t0x0055de81",
        "0x0055de81\t0x0055de81\tAFTER\t7\t0x0055de92\t0x0055de81\tCRT__InvokeFunctionPointerRange\tCALL\tEAX",
        "0x0055dfe7\t0x0055dfe7\tAFTER\t9\t0x0055dffa\t0x0055dfe7\tCRT__RoundDoubleWithFpuChecks\tCALL\t0x00562c76",
        "0x0055dfe7\t0x0055dfe7\tAFTER\t21\t0x0055e018\t0x0055dfe7\tCRT__RoundDoubleWithFpuChecks\tCALL\t0x00562b3e",
        "0x0055dfe7\t0x0055dfe7\tAFTER\t36\t0x0055e038\t0x0055dfe7\tCRT__RoundDoubleWithFpuChecks\tCALL\t0x0056244b",
    ):
        require_tokens("post-context-instructions.tsv", instructions, (token,), failures)


def check_decompiles(failures: list[str]) -> None:
    decomp_dir = BASE / "post-context-decompile"
    expected_files = {
        "0055dac5_type_info__dtor.c": ("CRT__LockByIndex(0x1b)", "CRT__FreeBase", "CRT__UnlockByIndex"),
        "0055daee_type_info__scalar_deleting_dtor.c": ("type_info__dtor(this)", "deleteFlags", "OID__FreeObject_Callback"),
        "0055db0a_CRT__EhVectorDestructorIterator_WithUnwind.c": ("CRT__EhVectorDestructorIterator_IfNoException", "elemSize", "dtor"),
        "0055dccd_CRT__Acos.c": ("fpatan", "SQRT", "__math_exit"),
        "0055ddca_CRT__DoExit.c": ("ExitProcess", "CRT__InvokeFunctionPointerRange", "DAT_009d4610"),
        "0055de81_CRT__InvokeFunctionPointerRange.c": ("begin < end", "begin = (void *)((int)begin + 4)", "(**(code **)begin)()"),
        "0055df28_CRT__OnexitTablePush.c": ("CRT__ReallocBase", "DAT_009d4610", "DAT_009d460c"),
        "0055dfe7_CRT__RoundDoubleWithFpuChecks.c": ("__frnd", "CRT__HandleFloatingPointExceptionByFlags", "CRT__GetFpuControlWord"),
    }
    for name, tokens in expected_files.items():
        require_tokens(name, read_text(decomp_dir / name), tokens, failures)


def check_docs_and_state(failures: list[str]) -> None:
    doc_tokens = {
        PUBLIC_NOTE: (
            "Ghidra CRT/type_info Wave621 Readiness Note",
            "CRT__EhVectorDestructorIterator_WithUnwind",
            "3234/6093 = 53.08%",
            "0x0055e14f CLIParams__ScanFormatFromString",
            "runtime unwind/math/exit behavior",
        ),
        FUNCTION_INDEX: ("type_info__dtor", "CRT__EhVectorDestructorIterator_WithUnwind", "CRT__RoundDoubleWithFpuChecks"),
        CRT_DOC: ("Wave621 Static Read-Back Note", "0x0055db0a", "3234` commented"),
        GHIDRA_REFERENCE: ("0x0055db0a | CRT__EhVectorDestructorIterator_WithUnwind", "0x0055dfe7 | CRT__RoundDoubleWithFpuChecks"),
        CAMPAIGN: ("after Wave621", "ghidra_crt_typeinfo_wave621_2026-05-20.md", "1046` `param_N`"),
        BACKLOG: ("Ghidra CRT/type_info Wave621 signature/comment hardening", "updated=10 skipped=0 renamed=3"),
        LEDGER: ("Ghidra CRT/type_info Wave621 signature/comment hardening", "strict clean-signature proxy 3182/6093 = 52.22%"),
        ATTEMPT_LOG: ("attempt_id\":20276", "headless_java_apply_signature_comment_tags_with_three_renames_no_boundary_change"),
        TRACKING: ("Wave621 hardened ten CRT/type_info/runtime helper rows", "next_attempt_id\": 20277"),
        PACKAGE_JSON: ("test:ghidra-crt-typeinfo-wave621", "tools\\\\ghidra_crt_typeinfo_wave621_probe.py --check"),
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
        "commentlessFunctionCount": 2859,
        "undefinedSignatureCount": 1218,
        "paramSignatureCount": 1046,
    }
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0055e14f" or head.get("name") != "CLIParams__ScanFormatFromString":
        failures.append(f"queue head mismatch: {head}")

    backup = read_json(BACKUP_SUMMARY)
    if backup.get("DiffCount") != 0:
        failures.append(f"backup DiffCount mismatch: {backup.get('DiffCount')}")
    if backup.get("SourceFileCount") != 19 or backup.get("BackupFileCount") != 19:
        failures.append("backup file count mismatch")
    if int(backup.get("SourceBytes", 0)) != 161844103 or int(backup.get("BackupBytes", 0)) != 161844103:
        failures.append("backup byte count mismatch")
    require_tokens("backup path", backup.get("BackupPath", ""), ("BEA_20260520-042315_post_wave621_crt_typeinfo_verified",), failures)


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
        print("Wave621 CRT/type_info probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave621 CRT/type_info probe: PASS")
    print("Verified 10 saved metadata rows, tags, xrefs, instructions, decompiles, queue telemetry, docs, logs, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
