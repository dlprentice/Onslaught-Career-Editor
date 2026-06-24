#!/usr/bin/env python3
"""Validate Wave613 CDXPatch/CDXPatchManager Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave613-cdxpatch-manager-00550380-00550750"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxpatch_manager_wave613_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXPATCH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXPatchManager.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

SIGNATURES = {
    "0x00550380": "void * __thiscall CDXPatch__Constructor(void * this)",
    "0x005503a0": "void __thiscall CDXPatch__Destructor_thunk(void * this)",
    "0x005503b0": "void __fastcall CDXPatchManager__ReleasePatches(void * patch_pool_entry)",
    "0x005503d0": "void __fastcall CDXPatchManager__ResetPatchSlots(void * patch_pool)",
    "0x00550400": "void * __thiscall CDXPatchManager__AllocatePatchSlot(void * this, short slot_id)",
    "0x00550430": "void __thiscall CDXPatchManager__Init(void * this, int lod2_patch_count, int lod4_patch_count, int lod8_patch_count)",
    "0x005506e0": "void __thiscall CDXPatchManager__Destroy(void * this)",
    "0x00550730": "void __thiscall CDXPatch__FreeData(void * this)",
    "0x00550750": "void __thiscall CDXPatch__LoadFromFile(void * this, void * chunk_reader)",
}

NAMES = {
    "0x00550380": "CDXPatch__Constructor",
    "0x005503a0": "CDXPatch__Destructor_thunk",
    "0x005503b0": "CDXPatchManager__ReleasePatches",
    "0x005503d0": "CDXPatchManager__ResetPatchSlots",
    "0x00550400": "CDXPatchManager__AllocatePatchSlot",
    "0x00550430": "CDXPatchManager__Init",
    "0x005506e0": "CDXPatchManager__Destroy",
    "0x00550730": "CDXPatch__FreeData",
    "0x00550750": "CDXPatch__LoadFromFile",
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxpatch-wave613",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "callsite-verified",
}

OVERCLAIM_TOKENS = (
    "runtime terrain rendering proven",
    "runtime lod behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
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
        "Function not found",
        "Input file not found",
        "BADADDR",
        "MISSING:",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back signature mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-wave613-dry.log",
        {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave613-apply.log",
        {"updated": 9, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave613-final-dry.log",
        {"updated": 0, "skipped": 9, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_log_tokens = {
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "rows=9 missing=0",
        "post-xrefs.log": "Wrote 16 rows",
        "post-instructions.log": "targets=9 missing=0",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-callsite-instructions.log": "targets=16 missing=0",
        "post-vtable-slots.log": "targets=1 rows=10",
        "queue-snapshot-refresh.log": "total_functions=6093 commented_functions=3156",
    }
    for log_name, token in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, (token,), failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-metadata.tsv")
    if len(rows) != len(SIGNATURES):
        failures.append(f"post-metadata row count mismatch: {len(rows)} != {len(SIGNATURES)}")
        return
    for row in rows:
        address = normalize_address(row["address"])
        if address not in SIGNATURES:
            failures.append(f"unexpected metadata address: {row['address']}")
            continue
        if row["name"] != NAMES[address]:
            failures.append(f"metadata name mismatch for {address}: {row['name']} != {NAMES[address]}")
        if row["signature"] != SIGNATURES[address]:
            failures.append(f"metadata signature mismatch for {address}: {row['signature']} != {SIGNATURES[address]}")
        if row["status"] != "OK":
            failures.append(f"metadata status mismatch for {address}: {row['status']}")
        require_tokens("metadata comment", row["comment"], ("Wave613", "Static retail", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"metadata comment overclaims for {address}: {token}")

    tag_rows = read_tsv_rows(BASE / "post-tags.tsv")
    if len(tag_rows) != len(SIGNATURES):
        failures.append(f"post-tags row count mismatch: {len(tag_rows)} != {len(SIGNATURES)}")
        return
    for row in tag_rows:
        address = normalize_address(row["address"])
        tags = set(filter(None, row["tags"].split(";")))
        missing = COMMON_TAGS - tags
        if missing:
            failures.append(f"missing common tags for {address}: {sorted(missing)}")
        if address in ("0x00550380", "0x005503a0", "0x00550730", "0x00550750") and "cdxpatch" not in tags:
            failures.append(f"missing cdxpatch tag for {address}")
        if address in ("0x005503b0", "0x005503d0", "0x00550400", "0x00550430", "0x005506e0") and "cdxpatch-manager" not in tags:
            failures.append(f"missing cdxpatch-manager tag for {address}")
        if address == "0x00550380" and "vtable-005e5114" not in tags:
            failures.append("missing vtable-005e5114 tag for 0x00550380")
        if address == "0x00550400" and "ret-0004" not in tags:
            failures.append("missing ret-0004 tag for 0x00550400")


def check_exports(failures: list[str]) -> None:
    counts = {
        "post-xrefs.tsv": (len(read_tsv_rows(BASE / "post-xrefs.tsv")), 16),
        "post-instructions.tsv": (len(read_tsv_rows(BASE / "post-instructions.tsv")), 2349),
        "post-decompile/index.tsv": (len(read_tsv_rows(BASE / "post-decompile" / "index.tsv")), 9),
        "post-callsite-instructions.tsv": (len(read_tsv_rows(BASE / "post-callsite-instructions.tsv")), 464),
        "post-vtable-slots.tsv": (len(read_tsv_rows(BASE / "post-vtable-slots.tsv")), 10),
    }
    for label, (actual, expected) in counts.items():
        if actual != expected:
            failures.append(f"{label} row count mismatch: {actual} != {expected}")

    require_tokens(
        "post-xrefs.tsv",
        read_text(BASE / "post-xrefs.tsv"),
        ("005504ab", "0055052a", "005505ad", "0053d6c3", "004d7875", "005120cb"),
        failures,
    )
    require_tokens(
        "post-instructions.tsv",
        read_text(BASE / "post-instructions.tsv"),
        ("CALL\t0x004fff00", "MOV\tword ptr [EDX], 0xffff", "RET\t0x4", "CALL\t0x005490e0", "CALL\t0x0048f1e0"),
        failures,
    )
    require_tokens(
        "post-callsite-instructions.tsv",
        read_text(BASE / "post-callsite-instructions.tsv"),
        ("0x0053d6c3", "PUSH\t0x5a", "PUSH\t0x12c", "PUSH\t0x320", "CALL\t0x00550430", "CALL\t0x005506e0", "CALL\t0x00550750"),
        failures,
    )
    require_tokens(
        "post-vtable-slots.tsv",
        read_text(BASE / "post-vtable-slots.tsv"),
        ("005e5114", "0x00550320", "NO_FUNCTION_AT_POINTER", "CDXPatch__RestoreAndRebuildIfDirty", "CRenderQueue__scalar_deleting_dtor"),
        failures,
    )
    decompile_blob = "\n".join(path.read_text(encoding="utf-8-sig") for path in sorted((BASE / "post-decompile").glob("005*.c")))
    require_tokens(
        "post-decompile",
        decompile_blob,
        ("CVBuffer__ctor_base", "PTR_LAB_005e5114", "CDXMemoryManager__Alloc", "CLandscapeTexture__SetupMipLevel", "CDXPatch__LoadFromFile"),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "G:\\GhidraBackups\\BEA_20260520-001229_post_wave613_cdxpatch_manager_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161614727,
        "destBytes": 161614727,
        "diffCount": 0,
    }
    for key, expected_value in expected_backup.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2937,
        "undefinedSignatureCount": 1275,
        "paramSignatureCount": 1056,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x00552060" or head.get("name") != "CDXShadows__Destructor":
        failures.append(f"queue head mismatch: {head}")


def check_public_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, PACKAGE_JSON, FUNCTION_INDEX, DXPATCH_DOC, CAMPAIGN, BACKLOG, LEDGER, ATTEMPT_LOG, TRACKING):
        if not path.is_file():
            failures.append(f"missing expected file: {path}")
            return

    note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        note,
        (
            "Ghidra CDXPatch Manager Wave613",
            "CDXPatchManager__Init",
            "`9` metadata rows",
            "`16` xref rows",
            "`2349` instruction rows",
            "`464` callsite instruction rows",
            "`10` vtable-slot rows",
            "G:\\GhidraBackups\\BEA_20260520-001229_post_wave613_cdxpatch_manager_verified",
            "Next queue head: `0x00552060 CDXShadows__Destructor`",
            "vtable slot 0 still points to `0x00550320`",
            "rebuild parity remain unproven",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in note.lower():
            failures.append(f"public note overclaims: {token}")

    package_text = read_text(PACKAGE_JSON)
    require_tokens(
        "package.json",
        package_text,
        ("test:ghidra-cdxpatch-manager-wave613", "tools\\ghidra_cdxpatch_manager_wave613_probe.py --check"),
        failures,
    )

    for label, path in (
        ("functions index", FUNCTION_INDEX),
        ("DXPatchManager doc", DXPATCH_DOC),
        ("campaign", CAMPAIGN),
        ("backlog", BACKLOG),
        ("ledger", LEDGER),
        ("attempt log", ATTEMPT_LOG),
    ):
        text = read_text(path)
        require_tokens(
            label,
            text,
            (
                "Wave613",
                "CDXPatchManager__Init",
                "CDXPatch__LoadFromFile",
                "2937",
                "1275",
                "CDXShadows__Destructor",
                "G:\\GhidraBackups\\BEA_20260520-001229_post_wave613_cdxpatch_manager_verified",
            ),
            failures,
        )

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20269:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20269")
    counters = tracking.get("counters", {})
    if counters.get("attempt_rows") != 20269:
        failures.append(f"tracking attempt_rows mismatch: {counters.get('attempt_rows')} != 20269")
    if counters.get("ledger_rows") != 1009:
        failures.append(f"tracking ledger_rows mismatch: {counters.get('ledger_rows')} != 1009")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_metadata_and_tags(failures)
    check_exports(failures)
    check_backup_and_queue(failures)
    check_public_docs(failures)

    if failures:
        print("Wave613 CDXPatch manager probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave613 CDXPatch manager probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
