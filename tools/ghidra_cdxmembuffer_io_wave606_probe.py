#!/usr/bin/env python3
"""Validate Wave606 CDXMemBuffer IO Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave606-dxmembuffer-io-00547d40"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxmembuffer_io_wave606_2026-05-19.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXMEMBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMemBuffer.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

EXPECTED_SIGNATURES = {
    "0x00547d40": ("CDXMemBuffer__SetBufferSize", "void __cdecl CDXMemBuffer__SetBufferSize(uint requested_size)"),
    "0x00547dc0": ("CDXMemBuffer__OpenWrite", "bool __thiscall CDXMemBuffer__OpenWrite(void * this, char * filename, int mem_type)"),
    "0x005482c0": ("CDXMemBuffer__GetFileSize", "uint __fastcall CDXMemBuffer__GetFileSize(void * this)"),
    "0x00548820": ("CDXMemBuffer__ReadLine", "void __thiscall CDXMemBuffer__ReadLine(void * this, char * output, int max_chars)"),
    "0x00548a70": ("CDXMemBuffer__WriteBytes", "void __thiscall CDXMemBuffer__WriteBytes(void * this, void * data, uint size)"),
    "0x00548d30": ("CDXMemBuffer__IsEOF", "bool __fastcall CDXMemBuffer__IsEOF(void * this)"),
}

EXPECTED_TAGS = {
    "0x00547d40": {"buffer-size", "global-read-buffer", "ret-c3"},
    "0x00547dc0": {"open-write", "ret-0x8", "createfile", "write-buffer"},
    "0x005482c0": {"file-size", "ret-c3", "win32-file"},
    "0x00548820": {"read-line", "ret-0x8", "compressed-buffer", "crc-check"},
    "0x00548a70": {"write-bytes", "ret-0x8", "compressed-buffer", "writefile"},
    "0x00548d30": {"eof", "ret-c3", "read-state"},
}

COMMENT_TOKENS = {
    "0x00547d40": ("plain RET", "caller-popped", "DAT_00650f6c", "0x100000", "1 MiB", "SetNextReadBufferSize", "retail body differs"),
    "0x00547dc0": ("RET 0x8", "filename and mem_type", "0x100000-byte", "OID__AllocObject", "DXMemBuffer.cpp line 0xe3", "CreateFileA", ".crc"),
    "0x005482c0": ("plain RET", "CText__Init", "ECX", "GetFileSize(this[0], NULL)", "EAX"),
    "0x00548820": ("RET 0x8", "output and max_chars", "CRLF", "this+0x12c", "this+0x24", "DAT_006318a0", "DAT_008c029c", "uncompress", "ReadString"),
    "0x00548a70": ("RET 0x8", "data and size", "compress", "DAT_008c029c", "WriteFile", "Write failed", "Write helper"),
    "0x00548d30": ("plain RET", "CEffect__LoadSFXFile", "CConsole__ExecScript", "CPCController__ReadControllerState", "this+0x24", "EndOfFile"),
}

COMMON_TAGS = {
    "static-reaudit",
    "dxmembuffer-io-wave606",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "owner-corrected",
    "cdxmembuffer",
}
OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "rebuild parity proven", "fully recovered", "fully reverse-engineered")


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
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
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "Function not found", "Input file not found", "Read-back signature mismatch", "Save blocked"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 6, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 6, "skipped": 0, "renamed": 6, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)

    for log_name in (
        "ExportFunctionMetadataByAddress-targets-rerun.log",
        "ExportFunctionTagsByAddress-targets-rerun.log",
        "ExportXrefsForAddresses-targets-rerun.log",
        "ExportInstructionsAroundAddresses-targets-rerun.log",
        "ExportFunctionsByAddressDecompile-targets-rerun.log",
    ):
        text = read_text(POST / log_name)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_post_exports(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "metadata_after.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(POST / "tags_after.tsv")}
    if set(metadata_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"metadata address set mismatch: {sorted(metadata_rows)}")
    if set(tag_rows) != set(EXPECTED_SIGNATURES):
        failures.append(f"tag address set mismatch: {sorted(tag_rows)}")

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata_rows.get(address)
        if not row:
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], COMMENT_TOKENS[address], failures)
        require_tokens(f"{address} comment", row["comment"], ("Static retail evidence only", "BEA patching", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tag_rows.get(address)
        if not tag_row:
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        missing = (COMMON_TAGS | EXPECTED_TAGS[address]) - actual_tags
        if tag_row["name"] != name:
            failures.append(f"{address} tag name mismatch: {tag_row['name']} != {name}")
        if tag_row["status"] != "OK":
            failures.append(f"{address} tag status mismatch: {tag_row['status']}")
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "post/xrefs_after.tsv": 70,
        "post/instructions_after.tsv": 222,
        "post/decomp_after/index.tsv": 6,
    }
    actual_counts = {
        "post/xrefs_after.tsv": row_count(POST / "xrefs_after.tsv"),
        "post/instructions_after.tsv": row_count(POST / "instructions_after.tsv"),
        "post/decomp_after/index.tsv": row_count(POST / "decomp_after" / "index.tsv"),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")


def check_xrefs_and_instructions(failures: list[str]) -> None:
    xref_text = read_text(POST / "xrefs_after.tsv")
    require_tokens(
        "xrefs_after",
        xref_text,
        (
            "CDXMemBuffer__SetBufferSize",
            "CMissionScriptObjectCode__LoadAsync",
            "CDXMemBuffer__OpenWrite",
            "CMemoryManager__DumpMemory",
            "CController__StartRecording",
            "CMemoryHeap__OutputStats",
            "CDXMemBuffer__GetFileSize",
            "CText__Init",
            "CDXMemBuffer__ReadLine",
            "CEffect__LoadSFXFile",
            "CTokenArchive__ReadLine",
            "CDXMemBuffer__WriteBytes",
            "CPCController__RecordControllerState",
            "CDXMemBuffer__IsEOF",
            "CConsole__ExecScript",
            "CPCController__ReadControllerState",
        ),
        failures,
    )
    instruction_text = read_text(POST / "instructions_after.tsv")
    require_tokens("instructions_after", instruction_text, ("RET\t", "RET\t0x8", "PUSH\t0x100000", "CALL\t0x005490e0", "CALL\tdword ptr [0x005d8164]"), failures)
    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (POST / "decomp_after").glob("*.c"))
    require_tokens(
        "decomp_after",
        decompile_text,
        (
            "CDXMemBuffer__SetBufferSize",
            "DAT_00650f6c = 0x100000",
            "requested_size + 0xfffff & 0xfff00000",
            "CDXMemBuffer__OpenWrite",
            "OID__AllocObject(0x100000",
            "CreateFileA",
            "CDXMemBuffer__GetFileSize",
            "GetFileSize",
            "CDXMemBuffer__ReadLine",
            "DAT_006318a0",
            "DAT_008c029c",
            "uncompress",
            "CDXMemBuffer__WriteBytes",
            "compress",
            "WriteFile",
            "CDXMemBuffer__IsEOF",
            "this + 0x24",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("BackupPath") != "[maintainer-local-ghidra-backup-root]\\BEA_20260519-204906_post_wave606_dxmembuffer_io_verified":
        failures.append(f"backup path mismatch: {backup.get('BackupPath')}")
    expected_backup = {"FileCount": 19, "TotalBytes": 161352583, "MissingCount": 0, "ExtraCount": 0, "DiffCount": 0}
    for key, expected_value in expected_backup.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2984,
        "undefinedSignatureCount": 1305,
        "paramSignatureCount": 1071,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x00548ec0":
        failures.append("queue head mismatch: expected 0x00548ec0")

    rows = read_tsv_rows(QUALITY_TSV)
    strict = [
        row for row in rows
        if row["comment"].strip()
        and not row["signature"].startswith("undefined ")
        and not re.search(r"\bparam_[0-9]+", row["signature"])
    ]
    if len(rows) != 6093:
        failures.append(f"quality row count mismatch: {len(rows)} != 6093")
    if len(strict) != 3064:
        failures.append(f"strict clean signature proxy mismatch: {len(strict)} != 3064")


def check_docs_and_logs(failures: list[str]) -> None:
    package_json = read_text(PACKAGE_JSON)
    public_note = read_text(PUBLIC_NOTE)
    dx_doc = read_text(DXMEMBUFFER_DOC)
    fn_index = read_text(FUNCTION_INDEX)
    campaign = read_text(CAMPAIGN)
    backlog = read_text(BACKLOG)

    require_tokens(
        "package.json",
        package_json,
        ("test:ghidra-cdxmembuffer-io-wave606", "tools\\ghidra_cdxmembuffer_io_wave606_probe.py --check"),
        failures,
    )

    common_doc_tokens = (
        "Wave606",
        "CDXMemBuffer__SetBufferSize",
        "CDXMemBuffer__OpenWrite",
        "CDXMemBuffer__GetFileSize",
        "CDXMemBuffer__ReadLine",
        "CDXMemBuffer__WriteBytes",
        "CDXMemBuffer__IsEOF",
        "0x00548ec0 CDXEngine__FreeLandscapeCellList_Debug",
        "2984",
        "commentless",
        "1305",
        "exact-undefined",
        "1071",
        "[maintainer-local-ghidra-backup-root]\\BEA_20260519-204906_post_wave606_dxmembuffer_io_verified",
    )
    for label, text in {
        "public note": public_note,
        "DXMemBuffer doc": dx_doc,
        "function index": fn_index,
        "campaign": campaign,
        "backlog": backlog,
    }.items():
        require_tokens(label, text, common_doc_tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    require_tokens("public note", public_note, ("updated=6", "renamed=6", "70 xref rows", "222 instruction rows", "DiffCount=0", "Strict clean-signature proxy"), failures)

    ledger_rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not any(row.get("task") == "Ghidra CDXMemBuffer IO Wave606 signature/comment/owner hardening" and row.get("status") == "completed" for row in ledger_rows):
        failures.append("ledger missing Wave606 completed row")

    attempt_rows = [json.loads(line) for line in ATTEMPT_LOG.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    wave_attempt = next((row for row in attempt_rows if row.get("attempt_id") == 20261), None)
    if not wave_attempt:
        failures.append("attempt log missing attempt_id 20261")
    else:
        require_tokens("attempt 20261 notes", wave_attempt.get("notes", ""), ("Wave606", "renamed=6", "0x00548ec0"), failures)

    tracking = read_json(TRACKING)
    expected_counters = {"ledger_rows": 1002, "attempt_rows": 20262, "completed": 993, "pending": 9}
    counters = tracking.get("counters", {})
    for key, expected in expected_counters.items():
        if counters.get(key) != expected:
            failures.append(f"tracking counter {key} mismatch: {counters.get(key)} != {expected}")
    if tracking.get("next_attempt_id") != 20262:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20262")
    require_tokens("tracking notes", "\n".join(tracking.get("notes", [])), ("Wave606", "0x00548ec0", "CDXEngine__FreeLandscapeCellList_Debug"), failures)


def run_check() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs_and_instructions(failures)
        check_backup_and_queue(failures)
        check_docs_and_logs(failures)
    except Exception as exc:  # noqa: BLE001 - probe should report unexpected read failures.
        failures.append(f"probe exception: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave606 CDXMemBuffer IO probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave606 CDXMemBuffer IO probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
