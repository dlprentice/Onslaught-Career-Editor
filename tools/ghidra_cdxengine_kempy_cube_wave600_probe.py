#!/usr/bin/env python3
"""Validate Wave600 CDXEngine Kempy cube Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave600-cdxengine-hud-kempy-00544040"
POST = BASE / "post"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxengine_kempy_cube_wave600_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
DXKEMPY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXKempyCube.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

EXPECTED_SIGNATURES = {
    "0x00544040": (
        "CDXEngine__ClearKempyCubeTextureSlots",
        "void * __fastcall CDXEngine__ClearKempyCubeTextureSlots(void * kempy_cube_resources)",
    ),
    "0x00544060": (
        "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer",
        "void __fastcall CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer(void * kempy_cube_resources)",
    ),
    "0x005440a0": (
        "CDXEngine__InitKempyCubeTexturesAndVertexBuffer",
        "void __thiscall CDXEngine__InitKempyCubeTexturesAndVertexBuffer(void * this, int cube_index)",
    ),
    "0x005441a0": (
        "CDXEngine__InitKempyCubeResources",
        "void __thiscall CDXEngine__InitKempyCubeResources(void * this, int cube_index)",
    ),
    "0x005441b0": (
        "CDXEngine__RenderKempyCubeFaces",
        "void __fastcall CDXEngine__RenderKempyCubeFaces(void * kempy_cube_resources)",
    ),
}

EXPECTED_TAGS = {
    "0x00544040": {"cdxengine", "kempy-cube", "texture-slots", "returns-input", "label-corrected"},
    "0x00544060": {"cdxengine", "kempy-cube", "texture-slots", "cvbuffer", "label-corrected"},
    "0x005440a0": {"cdxengine", "kempy-cube", "texture-load", "cvbuffer", "ret-0x4"},
    "0x005441a0": {"cdxengine", "kempy-cube", "set-kempy-cube", "wrapper", "ret-0x4"},
    "0x005441b0": {"cdxengine", "kempy-cube", "render", "texture-slots", "cvbuffer"},
}

COMMENT_TOKENS = {
    "0x00544040": ("0xa14", "engine+0x498", "+0x00..+0x10", "HudTextureSlots", "Static retail evidence only"),
    "0x00544060": ("CEngine__Shutdown", "engine+0x498", "CHud__DecrementCounter9C(texture+8)", "0x008aa908", "Static retail evidence only"),
    "0x005440a0": ("CEngine__SetKempyCube", "RET 0x4", "CDXEngine__FormatCubeTextureFilename", "CTexture__FindTexture", "0x008aa908", "20-vertex/20-byte/FVF 0x102", "0x006508f0"),
    "0x005441a0": ("CEngine__SetKempyCube", "RET 0x4", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer"),
    "0x005441b0": ("CDXEngine__Render", "engine+0x498", "0x008aa8d8", "0x008aa908", "CDXTexture__GetAnimatedFrame", "D3D draw"),
}

COMMON_TAGS = {
    "static-reaudit",
    "cdxengine-kempy-cube-wave600",
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
    require_log_summary(BASE / "apply_dry.log", {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_apply.log", {"updated": 5, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0}, failures)
    require_log_summary(BASE / "apply_final_dry.log", {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, failures)


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
        "post/xrefs_after.tsv": 5,
        "post/instructions_after.tsv": 1505,
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
        ("0x00544040", "CDXEngine__ClearKempyCubeTextureSlots", "0x00449c53", "0x004499d0", "CEngine__Init", "UNCONDITIONAL_CALL"),
        ("0x00544060", "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer", "0x00449975", "0x00449890", "CEngine__Shutdown", "UNCONDITIONAL_CALL"),
        ("0x005440a0", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "0x005441a5", "0x005441a0", "CDXEngine__InitKempyCubeResources", "UNCONDITIONAL_CALL"),
        ("0x005441a0", "CDXEngine__InitKempyCubeResources", "0x0044a2ab", "0x0044a2a0", "CEngine__SetKempyCube", "UNCONDITIONAL_CALL"),
        ("0x005441b0", "CDXEngine__RenderKempyCubeFaces", "0x0053e629", "0x0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
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
        ("0x00544046", "CDXEngine__ClearKempyCubeTextureSlots", "MOV", "dword ptr [EDX], ECX"),
        ("0x00544054", "CDXEngine__ClearKempyCubeTextureSlots", "RET", ""),
        ("0x00544072", "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer", "CALL", "0x004f27e0"),
        ("0x00544093", "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer", "CALL", "dword ptr [EAX]"),
        ("0x00544095", "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer", "MOV", "dword ptr [0x008aa908], 0x0"),
        ("0x005440c8", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "CALL", "0x0048de30"),
        ("0x005440d8", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "CALL", "0x004f27f0"),
        ("0x00544119", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "CALL", "0x005490e0"),
        ("0x0054414d", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "CALL", "0x005000c0"),
        ("0x0054415d", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "CALL", "0x005001b0"),
        ("0x00544174", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "MOVSD.REP", "ES:EDI, ESI"),
        ("0x0054417c", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "CALL", "0x005001e0"),
        ("0x00544193", "CDXEngine__InitKempyCubeTexturesAndVertexBuffer", "RET", "0x4"),
        ("0x005441a5", "CDXEngine__InitKempyCubeResources", "CALL", "0x005440a0"),
        ("0x005441aa", "CDXEngine__InitKempyCubeResources", "RET", "0x4"),
        ("0x00544287", "CDXEngine__RenderKempyCubeFaces", "CALL", "dword ptr [ECX + 0x190]"),
        ("0x005442c1", "CDXEngine__RenderKempyCubeFaces", "CALL", "0x00558690"),
        ("0x005442e0", "CDXEngine__RenderKempyCubeFaces", "CALL", "dword ptr [ECX + 0x144]"),
        ("0x00544350", "CDXEngine__RenderKempyCubeFaces", "RET", ""),
    }
    missing_instr = expected_instructions - instructions
    if missing_instr:
        failures.append(f"missing expected instructions: {sorted(missing_instr)}")


def check_docs_and_ledgers(failures: list[str]) -> None:
    texts = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "engine doc": read_text(ENGINE_DOC),
        "DXKempyCube doc": read_text(DXKEMPY_DOC),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
    }
    required_tokens = (
        "Wave600",
        "0x00544040",
        "0x00544060",
        "0x005440a0",
        "0x005441a0",
        "0x005441b0",
        "3079",
        "3014",
        "1331",
        "1075",
        "3034/6093 = 49.79%",
        "0x00544770 CDXLandscape__ReleaseOwnedResources",
        "BEA_20260519-174509_post_wave600_cdxengine_kempy_cube_verified",
    )
    for label, text in texts.items():
        require_tokens(label, text, required_tokens[:6], failures)
        if label in {"public note", "function index", "campaign", "backlog", "ledger", "attempt log"}:
            require_tokens(label, text, required_tokens[6:], failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20256:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    counters = tracking.get("counters", {})
    if counters.get("ledger_rows") != 996 or counters.get("attempt_rows") != 20256 or counters.get("completed") != 987:
        failures.append(f"tracking counters mismatch: {counters}")


def check_backup_and_queue(failures: list[str]) -> None:
    summary = read_json(BACKUP_SUMMARY)
    expected_backup = "[maintainer-local-ghidra-backup-root]\\BEA_20260519-174509_post_wave600_cdxengine_kempy_cube_verified"
    if summary.get("backupPath") != expected_backup:
        failures.append(f"backup path mismatch: {summary.get('backupPath')}")
    if summary.get("fileCount") != 19:
        failures.append(f"backup fileCount mismatch: {summary.get('fileCount')}")
    if int(summary.get("totalBytes", 0)) != 161188743:
        failures.append(f"backup totalBytes mismatch: {summary.get('totalBytes')}")
    for key in ("missingCount", "extraCount", "diffCount"):
        if summary.get(key) != 0:
            failures.append(f"backup {key} mismatch: {summary.get(key)}")
    if summary.get("manifestHash") != "d86b1630787846993bbd52f40f4821e89ecc5f13e8fa0afddccbe4feb8725247":
        failures.append(f"backup manifestHash mismatch: {summary.get('manifestHash')}")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    expected_quality = {
        "commentlessFunctionCount": 3014,
        "undefinedSignatureCount": 1331,
        "paramSignatureCount": 1075,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_quality.items():
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x00544770" or head.get("name") != "CDXLandscape__ReleaseOwnedResources":
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
        print("Wave600 CDXEngine Kempy cube probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave600 CDXEngine Kempy cube probe: PASS")
    print("Verified 5 saved signatures/comments/tags, read-back exports, docs, ledgers, queue telemetry, and backup summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
