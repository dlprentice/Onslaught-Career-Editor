#!/usr/bin/env python3
"""Validate Wave609 CDXMeshVB head Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave609-cdxmeshvb-head-0054bf80"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxmeshvb_head_wave609_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x0054bf80": {
        "name": "CDXMeshVB__ctor",
        "signature": "void * __thiscall CDXMeshVB__ctor(void * this)",
        "tags": {"cdxmeshvb", "constructor", "vtable-005e50fc", "ret-c3"},
        "comment_tokens": (
            "constructor installs vtable 0x005e50fc",
            "+0x108/+0x10c/+0x110/+0x120/+0x124",
            "64 group-pointer slots",
        ),
        "decompile_file": "0054bf80_CDXMeshVB__ctor.c",
        "decompile_tokens": (
            "void * __thiscall CDXMeshVB__ctor(void *this)",
            "PTR_CDXMeshVB__scalar_deleting_dtor_005e50fc",
        ),
    },
    "0x0054bff0": {
        "name": "CDXMeshVB__scalar_deleting_dtor",
        "signature": "void * __thiscall CDXMeshVB__scalar_deleting_dtor(void * this, byte flags)",
        "tags": {"cdxmeshvb", "scalar-deleting-dtor", "vtable-slot-0", "ret-0x4"},
        "comment_tokens": (
            "vtable slot 0",
            "RET 0x4",
            "flags&1",
            "CDXMemoryManager__Free",
        ),
        "decompile_file": "0054bff0_CDXMeshVB__scalar_deleting_dtor.c",
        "decompile_tokens": (
            "void * __thiscall CDXMeshVB__scalar_deleting_dtor(void *this,byte flags)",
            "CDXMeshVB__dtor_base(this);",
            "CDXMemoryManager__Free(&DAT_009c3df0,this);",
        ),
    },
    "0x0054c010": {
        "name": "CDXMeshVB__dtor_base",
        "signature": "void __thiscall CDXMeshVB__dtor_base(void * this)",
        "tags": {"cdxmeshvb", "destructor-base", "resource-release", "ret-c3"},
        "comment_tokens": (
            "calls CDXMeshVB__ReleaseResources",
            "frees the name pointer at +0x124",
            "base device-object teardown",
        ),
        "decompile_file": "0054c010_CDXMeshVB__dtor_base.c",
        "decompile_tokens": (
            "void __thiscall CDXMeshVB__dtor_base(void *this)",
            "CDXMeshVB__ReleaseResources(this);",
            "CDXMemoryManager__Free(&DAT_009c3df0,*(void **)((int)this + 0x124));",
        ),
    },
    "0x0054c0a0": {
        "name": "CDXMeshVB__BuildStaticVB",
        "signature": "int __thiscall CDXMeshVB__BuildStaticVB(void * this)",
        "tags": {"cdxmeshvb", "build-static-vb", "vertex-stride-0x24", "fvf-0x152", "hresult-style"},
        "comment_tokens": (
            "0x24-byte static vertices",
            "FVF 0x152",
            "+0x114/+0x118/+0x11c as 0x24/0x152/4",
            "S_OK or 0x80004005-style failure",
        ),
        "decompile_file": "0054c0a0_CDXMeshVB__BuildStaticVB.c",
        "decompile_tokens": (
            "int __thiscall CDXMeshVB__BuildStaticVB(void *this)",
            "CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer",
            "*(undefined4 *)((int)this + 0x114) = 0x24;",
            "*(undefined4 *)((int)this + 0x118) = 0x152;",
        ),
    },
    "0x0054c920": {
        "name": "CDXMeshVB__BuildSkeletalVB",
        "signature": "int __thiscall CDXMeshVB__BuildSkeletalVB(void * this)",
        "tags": {"cdxmeshvb", "build-skeletal-vb", "vertex-stride-0x30", "vertex-shader-gate", "hresult-style"},
        "comment_tokens": (
            "Building skeletal VB",
            "0x30-byte skeletal vertices",
            "DAT_00854e6c",
            "+0x114/+0x118/+0x11c as 0x30/0/4",
        ),
        "decompile_file": "0054c920_CDXMeshVB__BuildSkeletalVB.c",
        "decompile_tokens": (
            "int __thiscall CDXMeshVB__BuildSkeletalVB(void *this)",
            "DAT_00854e6c",
            "*(undefined4 *)((int)this + 0x114) = 0x30;",
        ),
    },
    "0x0054d3f0": {
        "name": "CDXMeshVB__ReleaseResources",
        "signature": "int __thiscall CDXMeshVB__ReleaseResources(void * this)",
        "tags": {"cdxmeshvb", "resource-release", "vtable-slot-4", "ret-c3"},
        "comment_tokens": (
            "vtable slot 4",
            "+0x108",
            "+0x110",
            "returns 0",
        ),
        "decompile_file": "0054d3f0_CDXMeshVB__ReleaseResources.c",
        "decompile_tokens": (
            "int __thiscall CDXMeshVB__ReleaseResources(void *this)",
            "CDXMemoryManager__Free(&DAT_009c3df0",
            "return 0;",
        ),
    },
    "0x0054e160": {
        "name": "CDXMeshVB__Load",
        "signature": "void __thiscall CDXMeshVB__Load(void * this, void * reader, int use_hardware_shader)",
        "tags": {"cdxmeshvb", "load", "ret-0x8", "chunk-reader", "vertex-shader-gate"},
        "comment_tokens": (
            "RET 0x8",
            "CMeshPart__LoadFromStream",
            "0x128-byte serialized header",
            "DAT_00854e6c && use_hardware_shader",
        ),
        "decompile_file": "0054e160_CDXMeshVB__Load.c",
        "decompile_tokens": (
            "void __thiscall CDXMeshVB__Load(void *this,void *reader,int use_hardware_shader)",
            "CChunkReader__Read(this_00,this,0x128,1);",
            "DAT_00854e6c",
            "use_hardware_shader",
        ),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxmeshvb-head-wave609",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
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
        "Read-back signature mismatch",
        "Save blocked",
        "BAD:",
        "BADNAME:",
        "MISSING:",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-dry.log",
        {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 4, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply.log",
        {"updated": 7, "skipped": 0, "renamed": 4, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-final-dry.log",
        {"updated": 0, "skipped": 7, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    for log_name in (
        "post-metadata.log",
        "post-tags.log",
        "post-xrefs.log",
        "post-instructions.log",
        "post-decompile.log",
        "post-vtable-slots.log",
    ):
        text = read_text(BASE / log_name)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")
    if "targets=7 missing=0" not in read_text(BASE / "post-instructions.log"):
        failures.append("post-instructions.log missing clean target summary")
    if "targets=7 dumped=7 missing=0 failed=0" not in read_text(BASE / "post-decompile.log"):
        failures.append("post-decompile.log missing clean decompile summary")
    if "targets=1 rows=16" not in read_text(BASE / "post-vtable-slots.log"):
        failures.append("post-vtable-slots.log missing clean vtable summary")


def check_metadata_and_tags(failures: list[str]) -> None:
    metadata_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-metadata.tsv")}
    tag_rows = {normalize_address(row["address"]): row for row in read_tsv_rows(BASE / "post-tags.tsv")}
    expected_addresses = set(TARGETS)
    if set(metadata_rows) != expected_addresses:
        failures.append(f"metadata address set mismatch: {sorted(metadata_rows)}")
    if set(tag_rows) != expected_addresses:
        failures.append(f"tag address set mismatch: {sorted(tag_rows)}")

    for address, spec in TARGETS.items():
        row = metadata_rows.get(address)
        if row:
            if row["name"] != spec["name"]:
                failures.append(f"{address} name mismatch: {row['name']} != {spec['name']}")
            if row["signature"] != spec["signature"]:
                failures.append(f"{address} signature mismatch: {row['signature']} != {spec['signature']}")
            if row["status"] != "OK":
                failures.append(f"{address} metadata status mismatch: {row['status']}")
            require_tokens(f"{address} metadata comment", row["comment"], spec["comment_tokens"], failures)
            lowered = row["comment"].lower()
            for token in OVERCLAIM_TOKENS:
                if token in lowered:
                    failures.append(f"{address} metadata comment overclaims: {token}")

        tag_row = tag_rows.get(address)
        if tag_row:
            actual_tags = set(filter(None, tag_row["tags"].split(";")))
            expected_tags = COMMON_TAGS | spec["tags"]
            missing = expected_tags - actual_tags
            if tag_row["name"] != spec["name"]:
                failures.append(f"{address} tag name mismatch: {tag_row['name']} != {spec['name']}")
            if tag_row["status"] != "OK":
                failures.append(f"{address} tag status mismatch: {tag_row['status']}")
            if missing:
                failures.append(f"{address} missing tags: {sorted(missing)}")


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 791,
        "post-decompile/index.tsv": 7,
        "post-vtable-slots.tsv": 16,
    }
    actual_counts = {
        "post-xrefs.tsv": len(read_tsv_rows(BASE / "post-xrefs.tsv")),
        "post-instructions.tsv": len(read_tsv_rows(BASE / "post-instructions.tsv")),
        "post-decompile/index.tsv": len(read_tsv_rows(BASE / "post-decompile" / "index.tsv")),
        "post-vtable-slots.tsv": len(read_tsv_rows(BASE / "post-vtable-slots.tsv")),
    }
    for label, expected in expected_counts.items():
        if actual_counts[label] != expected:
            failures.append(f"{label} row count mismatch: {actual_counts[label]} != {expected}")

    xref_text = read_text(BASE / "post-xrefs.tsv")
    require_tokens(
        "post-xrefs.tsv",
        xref_text,
        (
            "004ae616",
            "CMeshPart__Init",
            "005e50fc",
            "CDXMeshVB__scalar_deleting_dtor",
            "CDXMeshVB__ReleaseResources",
            "004b3159",
            "CMeshPart__LoadFromStream",
        ),
        failures,
    )

    instruction_text = read_text(BASE / "post-instructions.tsv")
    require_tokens(
        "post-instructions.tsv",
        instruction_text,
        (
            "0x0054bf80",
            "0x0054bff0",
            "0x0054c010",
            "0x0054c0a0",
            "0x0054c920",
            "0x0054d3f0",
            "0x0054e160",
            "RET\t0x4",
            "RET\t0x10",
        ),
        failures,
    )

    vtable_rows = read_tsv_rows(BASE / "post-vtable-slots.tsv")
    by_slot = {row["slot_index"]: row for row in vtable_rows if normalize_address(row["vtable"]) == "0x005e50fc"}
    if by_slot.get("0", {}).get("function_name") != "CDXMeshVB__scalar_deleting_dtor":
        failures.append(f"vtable slot 0 mismatch: {by_slot.get('0')}")
    if by_slot.get("4", {}).get("function_name") != "CDXMeshVB__ReleaseResources":
        failures.append(f"vtable slot 4 mismatch: {by_slot.get('4')}")

    for address, spec in TARGETS.items():
        decompile_text = read_text(BASE / "post-decompile" / str(spec["decompile_file"]))
        require_tokens(f"{address} decompile", decompile_text, spec["decompile_tokens"], failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "G:\\GhidraBackups\\BEA_20260519-221542_post_wave609_cdxmeshvb_head_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161418119,
        "destBytes": 161418119,
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
        "commentlessFunctionCount": 2969,
        "undefinedSignatureCount": 1301,
        "paramSignatureCount": 1060,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x0054d530" or head.get("name") != "CMeshRenderer__RenderMeshWithLayerPasses":
        failures.append(f"queue head mismatch: {head}")


def check_public_docs(failures: list[str]) -> None:
    expected_paths = (
        PUBLIC_NOTE,
        PACKAGE_JSON,
        FUNCTION_INDEX,
        DXMESHVB_DOC,
        CAMPAIGN,
        BACKLOG,
        LEDGER,
        ATTEMPT_LOG,
        TRACKING,
    )
    for path in expected_paths:
        if not path.is_file():
            failures.append(f"missing expected file: {path}")
            return

    public_note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        public_note,
        (
            "Ghidra CDXMeshVB Head Wave609",
            "CDXMeshVB__ctor",
            "CDXMeshVB__BuildStaticVB",
            "CDXMeshVB__BuildSkeletalVB",
            "CDXMeshVB__Load",
            "`791` instruction rows",
            "`16` vtable-slot rows",
            "G:\\GhidraBackups\\BEA_20260519-221542_post_wave609_cdxmeshvb_head_verified",
            "Next queue head: `0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses`",
            "runtime render behavior",
            "rebuild parity remain unproven",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in public_note.lower():
            failures.append(f"public note overclaims: {token}")

    package_text = read_text(PACKAGE_JSON)
    require_tokens(
        "package.json",
        package_text,
        ("test:ghidra-cdxmeshvb-head-wave609", "tools\\ghidra_cdxmeshvb_head_wave609_probe.py --check"),
        failures,
    )

    for label, path in (
        ("functions index", FUNCTION_INDEX),
        ("DXMeshVB doc", DXMESHVB_DOC),
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
                "Wave609",
                "CDXMeshVB__ctor",
                "CDXMeshVB__scalar_deleting_dtor",
                "CDXMeshVB__ReleaseResources",
                "0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses",
                "2969",
                "commentless",
                "1060",
            ),
            failures,
        )

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20265:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20265")
    if tracking.get("counters", {}).get("attempt_rows") != 20265:
        failures.append(f"tracking attempt_rows mismatch: {tracking.get('counters', {}).get('attempt_rows')} != 20265")


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
        print("Wave609 CDXMeshVB head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave609 CDXMeshVB head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
