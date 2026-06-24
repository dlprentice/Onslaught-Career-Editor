#!/usr/bin/env python3
"""Validate Wave604 CDXLandscape target/shadow Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave604-cdxlandscape-target-shadow-00546220"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxlandscape_target_shadow_wave604_2026-05-19.md"
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
    "0x00546220": (
        "CDXLandscape__SetRenderTarget",
        "bool __thiscall CDXLandscape__SetRenderTarget(void * this, void * target_surface)",
    ),
    "0x005463f0": (
        "CDXLandscape__ReleaseRenderTarget",
        "void __thiscall CDXLandscape__ReleaseRenderTarget(void * this)",
    ),
    "0x00546460": (
        "CDXLandscape__ReleaseSurfaces",
        "void __thiscall CDXLandscape__ReleaseSurfaces(void * this)",
    ),
    "0x00546490": (
        "CDXLandscape__RenderShadowMap",
        "bool __thiscall CDXLandscape__RenderShadowMap(void * this, int record_index)",
    ),
    "0x00546900": (
        "CDXLandscape__RenderTileRange",
        "void __thiscall CDXLandscape__RenderTileRange(void * this, int x_min, int x_max, int z_min, int z_max)",
    ),
}

EXPECTED_TAGS = {
    "0x00546220": {"cdxlandscape", "render-target", "ret-0x4", "surface-pair", "d3d-target"},
    "0x005463f0": {"cdxlandscape", "render-target-release", "ret-c3", "surface-pair", "d3d-restore"},
    "0x00546460": {"cdxlandscape", "surface-release", "ret-c3", "surface-pair", "unwind-cleanup"},
    "0x00546490": {"cdxlandscape", "shadow-map", "ret-0x4", "resource-record", "d3d-state"},
    "0x00546900": {"cdxlandscape", "tile-range", "ret-0x10", "static-shadows", "tile-records"},
}

COMMENT_TOKENS = {
    "0x00546220": ("RET 0x4", "implicit this/ECX", "target_surface", "vtable slot 0x48", "Failed SRT/Failed SDSS", "DAT_009c6480"),
    "0x005463f0": ("plain RET", "implicit this/ECX=&local_surface_pair", "D3D vtable slots 0x94/0x9c", "releases and nulls"),
    "0x00546460": ("plain RET", "final/unwind paths", "releases this[0] and this[1]", "does not issue the D3D restore calls"),
    "0x00546490": ("RET 0x4", "CDXLandscape__RenderTerrain pushes 0", "this+0x24 + record_index*0x34", "CDXLandscape__SetRenderTarget", "CWaterRenderSystem__RenderShadowPass"),
    "0x00546900": ("RET 0x10", "CDXEngine__RenderMultipassLayerA", "x_min/x_max", "CStaticShadows__SampleShadowHeightBilinear", "DAT_009c64dc", "DAT_009c7c58"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxlandscape-target-shadow-wave604",
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


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str], *, clean: bool = True) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    if clean:
        for bad_token in ("LockException", "Function not found", "Input file not found", "Read-back signature mismatch", "Save blocked"):
            if bad_token in text:
                failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_dry_retry.log", {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 3, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)

    failed_apply = BASE / "apply_apply_failed_thiscall.log"
    require_log_summary(failed_apply, {"updated": 2, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 3}, failures, clean=False)
    require_tokens("failed apply log", read_text(failed_apply), ("Read-back signature mismatch", "REPORT: Save blocked by bad/missing rows"), failures)


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
        "post/xrefs_after.tsv": 8,
        "post/instructions_after.tsv": 9045,
        "post/decomp_after/index.tsv": 5,
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
        ("0x00546220", "CDXLandscape__SetRenderTarget", "0x0046e4e2", "0x0046e460", "CGame__Render", "UNCONDITIONAL_CALL"),
        ("0x00546220", "CDXLandscape__SetRenderTarget", "0x0054664a", "0x00546490", "CDXLandscape__RenderShadowMap", "UNCONDITIONAL_CALL"),
        ("0x005463f0", "CDXLandscape__ReleaseRenderTarget", "0x0046e8dd", "0x0046e460", "CGame__Render", "UNCONDITIONAL_CALL"),
        ("0x00546460", "CDXLandscape__ReleaseSurfaces", "0x0046e8f3", "0x0046e460", "CGame__Render", "UNCONDITIONAL_CALL"),
        ("0x00546490", "CDXLandscape__RenderShadowMap", "0x005461f5", "0x00545590", "CDXLandscape__RenderTerrain", "UNCONDITIONAL_CALL"),
        ("0x00546900", "CDXLandscape__RenderTileRange", "0x00553f54", "0x00553960", "CDXEngine__RenderMultipassLayerA", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instruction_text = read_text(POST / "instructions_after.tsv")
    require_tokens(
        "instructions_after",
        instruction_text,
        (
            "CALL\t0x00546220",
            "RET\t0x4",
            "RET\t0x10",
            "RET\t",
        ),
        failures,
    )
    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (POST / "decomp_after").glob("*.c"))
    require_tokens(
        "decomp_after",
        decompile_text,
        (
            "CDXLandscape__SetRenderTarget",
            "CDXLandscape__ReleaseRenderTarget",
            "CDXLandscape__ReleaseSurfaces",
            "CDXLandscape__RenderShadowMap",
            "CDXLandscape__RenderTileRange",
            "CStaticShadows__SampleShadowHeightBilinear",
            "CWaterRenderSystem__RenderShadowPass",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("BackupPath") != "G:\\GhidraBackups\\BEA_20260519-194745_post_wave604_cdxlandscape_target_shadow_verified":
        failures.append(f"backup path mismatch: {backup.get('BackupPath')}")
    expected = {
        "FileCount": 19,
        "TotalBytes": 161287047,
        "MissingCount": 0,
        "ExtraCount": 0,
        "DiffCount": 0,
        "ManifestHash": "657b521f4bc34af239e3cd22b7a3fa0505bbe4fb8f1e0b92ccf6cccdc11299ed",
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
        "commentlessFunctionCount": 2994,
        "undefinedSignatureCount": 1313,
        "paramSignatureCount": 1073,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x00546b10":
        failures.append("queue head mismatch: expected 0x00546b10")

    rows = read_tsv_rows(QUALITY_TSV)
    strict = [
        row for row in rows
        if row["comment"].strip()
        and not row["signature"].startswith("undefined ")
        and not re.search(r"\bparam_[0-9]+", row["signature"])
    ]
    if len(strict) != 3054:
        failures.append(f"strict clean signature proxy mismatch: {len(strict)}")


def check_docs_and_logs(failures: list[str]) -> None:
    public_note = read_text(PUBLIC_NOTE)
    dx_doc = read_text(DXLANDSCAPE_DOC)
    fn_index = read_text(FUNCTION_INDEX)
    campaign = read_text(CAMPAIGN)
    backlog = read_text(BACKLOG)

    common_doc_tokens = (
        "Wave604",
        "CDXLandscape__SetRenderTarget",
        "CDXLandscape__ReleaseRenderTarget",
        "CDXLandscape__ReleaseSurfaces",
        "CDXLandscape__RenderShadowMap",
        "CDXLandscape__RenderTileRange",
        "0x00546b10 CDXLandscape__ResetCameraPosition",
        "2994",
        "commentless",
        "1313",
        "exact-undefined",
        "1073",
        "G:\\GhidraBackups\\BEA_20260519-194745_post_wave604_cdxlandscape_target_shadow_verified",
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

    require_tokens("public note", public_note, ("updated=3", "skipped=2", "9045", "DiffCount=0", "Strict clean-signature proxy"), failures)

    ledger_rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not any(row.get("task") == "Ghidra CDXLandscape target/shadow Wave604 signature/comment hardening" and row.get("status") == "completed" for row in ledger_rows):
        failures.append("ledger missing Wave604 completed row")

    attempt_rows = [json.loads(line) for line in ATTEMPT_LOG.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    wave_attempt = next((row for row in attempt_rows if row.get("attempt_id") == 20259), None)
    if not wave_attempt:
        failures.append("attempt log missing attempt_id 20259")
    else:
        require_tokens("attempt 20259 notes", wave_attempt.get("notes", ""), ("Wave604", "updated=3", "bad=3", "0x00546b10"), failures)

    tracking = read_json(TRACKING)
    expected_counters = {"ledger_rows": 1000, "attempt_rows": 20260, "completed": 991, "pending": 9}
    counters = tracking.get("counters", {})
    for key, expected in expected_counters.items():
        if counters.get(key) != expected:
            failures.append(f"tracking counter {key} mismatch: {counters.get(key)} != {expected}")
    if tracking.get("next_attempt_id") != 20260:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20260")
    require_tokens("tracking notes", "\n".join(tracking.get("notes", [])), ("Wave604", "0x00546b10", "CDXLandscape__ResetCameraPosition"), failures)


def run_check() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs_and_instructions(failures)
        check_backup_and_queue(failures)
        check_docs_and_logs(failures)
    except Exception as exc:  # noqa: BLE001 - probe should report all unexpected read failures.
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
        print("Wave604 CDXLandscape target/shadow probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave604 CDXLandscape target/shadow probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
