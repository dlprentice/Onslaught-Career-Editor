#!/usr/bin/env python3
"""Validate Wave598 CDXEngine/DXImposter Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave598-cdxengine-imposter-head-00542740"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxengine_imposter_head_wave598_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
DXIMPOSTER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXImposter.cpp" / "_index.md"
IMPOSTER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "imposter.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x00542740": (
        "CDXEngine__InitLandscapeTextureTables",
        "void * __fastcall CDXEngine__InitLandscapeTextureTables(void * texture_table_owner)",
    ),
    "0x005428d0": (
        "CDXImposter__InitGlobals",
        "int __cdecl CDXImposter__InitGlobals(void)",
    ),
    "0x00542990": (
        "CDXImposter__ShutdownAll",
        "void __cdecl CDXImposter__ShutdownAll(void)",
    ),
    "0x00542a30": (
        "CDXImposter__InitEntry",
        "void * __fastcall CDXImposter__InitEntry(void * imposter)",
    ),
    "0x00542a50": (
        "CDXEngine__BuildDirectionalSampleRing",
        "void __cdecl CDXEngine__BuildDirectionalSampleRing(float view_yaw_radians)",
    ),
    "0x00542ee0": (
        "CDXEngine__BuildZRotationMatrix",
        "void __thiscall CDXEngine__BuildZRotationMatrix(void * this, float angle_radians)",
    ),
    "0x00543300": (
        "CDXEngine__RenderImposterBillboardSet",
        "void __thiscall CDXEngine__RenderImposterBillboardSet(void * this, void * view_context, int alpha, int frame_index)",
    ),
    "0x005438c0": (
        "CDXImposter__RenderAll",
        "void __cdecl CDXImposter__RenderAll(void)",
    ),
}

EXPECTED_TAGS = {
    "0x00542740": {"cdxengine", "landscape-texture-table", "static-init", "returns-input"},
    "0x005428d0": {"cdximposter", "global-init", "cgame-init", "returns-one"},
    "0x00542990": {"cdximposter", "global-shutdown", "resource-release", "linked-list"},
    "0x00542a30": {"cdximposter", "entry-init", "cimposter", "returns-input"},
    "0x00542a50": {"cdxengine", "imposter", "sample-ring", "render-prep", "one-float-arg"},
    "0x00542ee0": {"cdxengine", "imposter", "z-rotation", "ret-0x4", "matrix-helper"},
    "0x00543300": {"cdxengine", "cdximposter", "billboard-render", "ret-0xc", "tree-imposter"},
    "0x005438c0": {"cdximposter", "render-all", "render-state", "cvbuftexture"},
}

COMMENT_TOKENS = {
    "0x00542740": ("0x008aa4e8", "0x00481400", "returns the same pointer"),
    "0x005428d0": ("CGame__Init", "0x00650848", "imposter list/count/texture-buffer globals", "returns 1"),
    "0x00542990": ("0x0067a678", "frame-data allocation", "CVBufTexture", "width/height globals"),
    "0x00542a30": ("CImposter__FindOrCreate", "0x4c imposter object", "+0x30/+0x38/+0x3c", "0x008aa8bc"),
    "0x00542a50": ("CDXEngine__Render", "0x0067a680", "0x008aa790", "CDXEngine__BuildZRotationMatrix"),
    "0x00542ee0": ("RET 0x4", "one stack parameter", "Z-rotation basis", "identity Z row"),
    "0x00543300": ("CRTTree", "RET 0xc", "view-context", "CDXImposter__BuildQuadGeometry"),
    "0x005438c0": ("CDXEngine__Render", "texture atlas", "CVBufTexture", "restores sampler/state-cache values"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxengine-imposter-head-wave598",
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
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}
    for key, expected_value in expected.items():
        actual = values.get(key)
        if actual != expected_value:
            failures.append(f"{path.name} {key} mismatch: {actual} != {expected_value}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(BASE / "apply_dry_corrected.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply_corrected.log", {"updated": 2, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 8, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    first_apply = read_text(BASE / "apply_apply.log")
    if "Read-back signature mismatch" not in first_apply or "bad=2" not in first_apply:
        failures.append("initial apply log should record the corrected thiscall read-back mismatch")


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
        "post/xrefs_after.tsv": 9,
        "post/instructions_after.tsv": 888,
        "post/decomp_after/index.tsv": 8,
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
        ("0x00542740", "CDXEngine__InitLandscapeTextureTables", "0x005426f5", "<none>", "<no_function>", "UNCONDITIONAL_CALL"),
        ("0x005428d0", "CDXImposter__InitGlobals", "0x0046c3aa", "0x0046c360", "CGame__Init", "UNCONDITIONAL_CALL"),
        ("0x00542a30", "CDXImposter__InitEntry", "0x0048899f", "0x004888f0", "CImposter__FindOrCreate", "UNCONDITIONAL_CALL"),
        ("0x00542a50", "CDXEngine__BuildDirectionalSampleRing", "0x0053e5ae", "0x0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
        ("0x00542ee0", "CDXEngine__BuildZRotationMatrix", "0x00542e47", "0x00542a50", "CDXEngine__BuildDirectionalSampleRing", "UNCONDITIONAL_CALL"),
        ("0x005438c0", "CDXImposter__RenderAll", "0x0053e7b7", "0x0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
    }
    missing = expected_xrefs - xrefs
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")

    instructions = {
        (
            normalize_address(row["instruction_addr"]),
            row["function_name"],
            row["mnemonic"],
            row["operands"],
        )
        for row in read_tsv_rows(POST / "instructions_after.tsv")
    }
    expected_instructions = {
        ("0x0054274b", "CDXEngine__InitLandscapeTextureTables", "RET", ""),
        ("0x00542a4a", "CDXImposter__InitEntry", "RET", ""),
        ("0x00542ee0", "CDXEngine__BuildZRotationMatrix", "SUB", "ESP, 0x10"),
        ("0x00542f87", "CDXEngine__BuildZRotationMatrix", "RET", "0x4"),
        ("0x00543300", "CDXEngine__RenderImposterBillboardSet", "MOV", "EAX, [0x0067a67c]"),
        ("0x005438b8", "CDXEngine__RenderImposterBillboardSet", "RET", "0xc"),
        ("0x005438c0", "CDXImposter__RenderAll", "MOV", "EAX, [0x0067a67c]"),
    }
    missing_instr = expected_instructions - instructions
    if missing_instr:
        failures.append(f"missing expected instructions: {sorted(missing_instr)}")


def check_docs_and_ledgers(failures: list[str]) -> None:
    texts = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "engine doc": read_text(ENGINE_DOC),
        "DXImposter doc": read_text(DXIMPOSTER_DOC),
        "imposter doc": read_text(IMPOSTER_DOC),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
    }
    required_tokens = (
        "Wave598",
        "0x00542740",
        "0x00542ee0",
        "0x00543300",
        "0x005438c0",
        "3072",
        "3021",
        "1333",
        "1080",
        "3027/6093 = 49.68%",
        "0x00543d90 CDXImposter__Deserialize",
        "BEA_20260519-164920_post_wave598_cdxengine_imposter_head_verified",
    )
    for label, text in texts.items():
        require_tokens(label, text, required_tokens[:5], failures)
        if label in {"public note", "function index", "campaign", "backlog", "ledger", "attempt log"}:
            require_tokens(label, text, required_tokens[5:], failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20254:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    counters = tracking.get("counters", {})
    if counters.get("ledger_rows") != 994 or counters.get("attempt_rows") != 20254 or counters.get("completed") != 985:
        failures.append(f"tracking counters mismatch: {counters}")


def check_backup_and_queue(failures: list[str]) -> None:
    summary = read_json(BACKUP_SUMMARY)
    expected_backup = "[maintainer-local-ghidra-backup-root]\\BEA_20260519-164920_post_wave598_cdxengine_imposter_head_verified"
    if summary.get("backupPath") != expected_backup:
        failures.append(f"backup path mismatch: {summary.get('backupPath')}")
    if summary.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {summary.get('fileCount')}")
    if int(summary.get("totalBytes", 0)) != 161155975:
        failures.append(f"backup totalBytes mismatch: {summary.get('totalBytes')}")
    for key in ("missingCount", "extraCount", "diffCount"):
        if summary.get(key) != 0:
            failures.append(f"backup {key} mismatch: {summary.get(key)}")
    if summary.get("manifestHash") != "d9ff83eb80ef21d63e7435740b015102f7f94ae98edc2e9e64b2ed58e2dd3c20":
        failures.append(f"backup manifestHash mismatch: {summary.get('manifestHash')}")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    expected_quality = {
        "commentlessFunctionCount": 3021,
        "undefinedSignatureCount": 1333,
        "paramSignatureCount": 1080,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00543d90" or head.get("name") != "CDXImposter__Deserialize":
        failures.append(f"queue head mismatch: {head}")


def run_check() -> list[str]:
    failures: list[str] = []
    check_logs(failures)
    check_post_exports(failures)
    check_xrefs_and_instructions(failures)
    check_docs_and_ledgers(failures)
    check_backup_and_queue(failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave598 CDXEngine/DXImposter probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave598 CDXEngine/DXImposter probe: PASS")
    print("Verified 8 saved signatures/comments/tags, read-back exports, docs, ledgers, queue telemetry, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
