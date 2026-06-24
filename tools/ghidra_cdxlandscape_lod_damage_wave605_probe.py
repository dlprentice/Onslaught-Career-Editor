#!/usr/bin/env python3
"""Validate Wave605 CDXLandscape LOD/damage Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave605-cdxlandscape-lod-damage-00546b10"
PRE = BASE / "pre"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxlandscape_lod_damage_wave605_2026-05-19.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

EXPECTED_SIGNATURES = {
    "0x00546b10": (
        "CDXLandscape__ResetCameraPosition",
        "void __fastcall CDXLandscape__ResetCameraPosition(void * this)",
    ),
    "0x00546b40": (
        "CDXLandscape__UpdateLOD",
        "void __thiscall CDXLandscape__UpdateLOD(void * this, void * engine_context_470, int record_index)",
    ),
    "0x005475d0": (
        "CDXEngine__ApplyLandscapeDamageStamp",
        "void __stdcall CDXEngine__ApplyLandscapeDamageStamp(float world_x, float world_z, int stamp_value)",
    ),
    "0x00547a60": (
        "CDXEngine__ComputeLandscapeTileComplexityScore",
        "double __stdcall CDXEngine__ComputeLandscapeTileComplexityScore(uint tile_index)",
    ),
}

EXPECTED_TAGS = {
    "0x00546b10": {"cdxlandscape", "camera-reset", "ret-c3", "resource-record", "multiplayer"},
    "0x00546b40": {"cdxlandscape", "update-lod", "ret-0x8", "tile-records", "patch-slots", "texture-update-queue"},
    "0x005475d0": {"cdxlandscape", "damage-stamp", "ret-0xc", "damage-cells", "tile-refresh"},
    "0x00547a60": {"cdxlandscape", "tile-complexity", "ret-0x4", "heightfield", "reset-helper"},
}

COMMENT_TOKENS = {
    "0x00546b10": ("plain RET", "DAT_0089c9b0", "0x4996b438", "1234567.0f", "+0x14", "+0x48", "CGame__IsMultiplayer"),
    "0x00546b40": ("RET 0x8", "engine+0x470", "engine+0x10", "record_index*0x34", "1234567.0f", "CDXPatchManager__AllocatePatchSlot", "CLandscapeTexture", "64x64"),
    "0x005475d0": ("RET 0xc", "world_x/world_z", "1 << abs(stamp_value)", "CDamage__RemoveCellEntryByCoords", "CDamage__InsertCellEntry", "DAT_0089c9b0", "orphan 0x004da4fd"),
    "0x00547a60": ("RET 0x4", "tile_index", "global heightfield", "0x9 by 0x9", "three subdivision levels", "DAT_006fbdf4", "double return", "casts the result to float"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxlandscape-lod-damage-wave605",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
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
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 4, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


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
        require_tokens(f"{address} comment", row["comment"], ("BEA patching", "rebuild parity remain unproven"), failures)
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
        "post/xrefs_after.tsv": 13,
        "post/instructions_after.tsv": 36004,
        "post/decomp_after/index.tsv": 4,
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
    xrefs = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv_rows(POST / "xrefs_after.tsv")
    }
    expected_xrefs = {
        ("0x00546b10", "CDXLandscape__ResetCameraPosition", "0x0046c459", "0x0046c430", "CGame__InitRestartLoop", "UNCONDITIONAL_CALL"),
        ("0x00546b10", "CDXLandscape__ResetCameraPosition", "0x0046edee", "0x0046e910", "CGame__Update", "UNCONDITIONAL_CALL"),
        ("0x00546b10", "CDXLandscape__ResetCameraPosition", "0x0046f5f7", "0x0046f550", "CGame__DeclarePlayerDead", "UNCONDITIONAL_CALL"),
        ("0x00546b10", "CDXLandscape__ResetCameraPosition", "0x0046f8a8", "0x0046f7e0", "CGame__ReceiveButtonAction", "UNCONDITIONAL_CALL"),
        ("0x00546b10", "CDXLandscape__ResetCameraPosition", "0x00470133", "0x00470120", "CGame__RespawnPlayer", "UNCONDITIONAL_CALL"),
        ("0x00546b40", "CDXLandscape__UpdateLOD", "0x0053e49f", "0x0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
        ("0x00546b40", "CDXLandscape__UpdateLOD", "0x0053e4bf", "0x0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
        ("0x00546b40", "CDXLandscape__UpdateLOD", "0x00545435", "0x00545410", "CDXLandscape__Render", "UNCONDITIONAL_CALL"),
        ("0x005475d0", "CDXEngine__ApplyLandscapeDamageStamp", "0x0044a186", "0x0044a130", "CEngine__InitDamageSystem", "UNCONDITIONAL_CALL"),
        ("0x005475d0", "CDXEngine__ApplyLandscapeDamageStamp", "0x0050d11e", "0x0050b9c0", "CWorld__LoadWorld", "UNCONDITIONAL_CALL"),
        ("0x005475d0", "CDXEngine__ApplyLandscapeDamageStamp", "0x004431c4", "0x00442f60", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects", "UNCONDITIONAL_CALL"),
        ("0x005475d0", "CDXEngine__ApplyLandscapeDamageStamp", "0x004da4fd", "<none>", "<no_function>", "UNCONDITIONAL_CALL"),
        ("0x00547a60", "CDXEngine__ComputeLandscapeTileComplexityScore", "0x005452fc", "0x00545070", "CDXLandscape__Reset", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    callsite_text = read_text(PRE / "instructions_callsites_before.tsv")
    require_tokens(
        "instructions_callsites_before",
        callsite_text,
        (
            "CALL\t0x00546b10",
            "CALL\t0x00546b40",
            "CALL\t0x005475d0",
            "CALL\t0x00547a60",
            "MOV\tECX, dword ptr [0x0089c9b0]",
            "MOV\tECX, EBP",
            "PUSH\t0x6",
            "PUSH\tEDI",
        ),
        failures,
    )
    instruction_text = read_text(POST / "instructions_after.tsv")
    require_tokens("instructions_after", instruction_text, ("RET\t0x8", "RET\t0xc", "RET\t0x4", "RET\t"), failures)
    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (POST / "decomp_after").glob("*.c"))
    require_tokens(
        "decomp_after",
        decompile_text,
        (
            "CDXLandscape__ResetCameraPosition",
            "CDXLandscape__UpdateLOD",
            "CDXEngine__ApplyLandscapeDamageStamp",
            "CDXEngine__ComputeLandscapeTileComplexityScore",
            "CDXPatchManager__AllocatePatchSlot",
            "CDamage__InsertCellEntry",
            "CDamage__RemoveCellEntryByCoords",
            "DAT_006fbdf0",
            "DAT_006fbdf4",
        ),
        failures,
    )
    caller_decompile = "\n".join(path.read_text(encoding="utf-8-sig") for path in (PRE / "decomp_callers_before").glob("*.c"))
    require_tokens("caller decompile", caller_decompile, ("CDXEngine__ComputeLandscapeTileComplexityScore", "(float)dVar12"), failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("BackupPath") != "G:\\GhidraBackups\\BEA_20260519-201654_post_wave605_cdxlandscape_lod_damage_verified":
        failures.append(f"backup path mismatch: {backup.get('BackupPath')}")
    expected = {
        "FileCount": 19,
        "TotalBytes": 161319815,
        "MissingCount": 0,
        "ExtraCount": 0,
        "DiffCount": 0,
        "ManifestHash": "fa146228213520868a20790fe8b99cd58adf5bb9bc89b9e22b3aa1c36b6900d5",
    }
    for key, expected_value in expected.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2990,
        "undefinedSignatureCount": 1311,
        "paramSignatureCount": 1071,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x00547d40":
        failures.append("queue head mismatch: expected 0x00547d40")

    rows = read_tsv_rows(QUALITY_TSV)
    strict = [
        row for row in rows
        if row["comment"].strip()
        and not row["signature"].startswith("undefined ")
        and not re.search(r"\bparam_[0-9]+", row["signature"])
    ]
    if len(rows) != 6093:
        failures.append(f"quality row count mismatch: {len(rows)} != 6093")
    if len(strict) != 3058:
        failures.append(f"strict clean signature proxy mismatch: {len(strict)}")


def check_docs_and_logs(failures: list[str]) -> None:
    package_json = read_text(PACKAGE_JSON)
    public_note = read_text(PUBLIC_NOTE)
    dx_doc = read_text(DXLANDSCAPE_DOC)
    fn_index = read_text(FUNCTION_INDEX)
    campaign = read_text(CAMPAIGN)
    backlog = read_text(BACKLOG)

    require_tokens(
        "package.json",
        package_json,
        ("test:ghidra-cdxlandscape-lod-damage-wave605", "tools\\ghidra_cdxlandscape_lod_damage_wave605_probe.py --check"),
        failures,
    )

    common_doc_tokens = (
        "Wave605",
        "CDXLandscape__ResetCameraPosition",
        "CDXLandscape__UpdateLOD",
        "CDXEngine__ApplyLandscapeDamageStamp",
        "CDXEngine__ComputeLandscapeTileComplexityScore",
        "0x00547d40 DXMemBuffer__SetBufferSize",
        "2990",
        "commentless",
        "1311",
        "exact-undefined",
        "1071",
        "G:\\GhidraBackups\\BEA_20260519-201654_post_wave605_cdxlandscape_lod_damage_verified",
    )
    for label, text in {
        "public note": public_note,
        "DXLandscape doc": dx_doc,
        "function index": fn_index,
        "campaign": campaign,
        "backlog": backlog,
    }.items():
        require_tokens(label, text, common_doc_tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    require_tokens("public note", public_note, ("updated=4", "skipped=0", "36004", "DiffCount=0", "Strict clean-signature proxy"), failures)

    ledger_rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not any(row.get("task") == "Ghidra CDXLandscape LOD/damage Wave605 signature/comment hardening" and row.get("status") == "completed" for row in ledger_rows):
        failures.append("ledger missing Wave605 completed row")

    attempt_rows = [json.loads(line) for line in ATTEMPT_LOG.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    wave_attempt = next((row for row in attempt_rows if row.get("attempt_id") == 20260), None)
    if not wave_attempt:
        failures.append("attempt log missing attempt_id 20260")
    else:
        require_tokens("attempt 20260 notes", wave_attempt.get("notes", ""), ("Wave605", "updated=4", "0x00547d40"), failures)

    tracking = read_json(TRACKING)
    expected_counters = {"ledger_rows": 1001, "attempt_rows": 20261, "completed": 992, "pending": 9}
    counters = tracking.get("counters", {})
    for key, expected in expected_counters.items():
        if counters.get(key) != expected:
            failures.append(f"tracking counter {key} mismatch: {counters.get(key)} != {expected}")
    if tracking.get("next_attempt_id") != 20261:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20261")
    require_tokens("tracking notes", "\n".join(tracking.get("notes", [])), ("Wave605", "0x00547d40", "DXMemBuffer__SetBufferSize"), failures)


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
        print("Wave605 CDXLandscape LOD/damage probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave605 CDXLandscape LOD/damage probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
