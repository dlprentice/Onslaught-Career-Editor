#!/usr/bin/env python3
"""Validate Wave591 DXCompass HUD-head Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave591-render-hud-head-0053bb50"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_dxcompass_hud_head_wave591_2026-05-19.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXCOMPASS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXCompass.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
BACKUP_SUMMARY = BASE / "wave591_backup_summary.json"

COMMON_TAGS = {
    "static-reaudit",
    "dxcompass-hud-head-wave591",
    "retail-binary-evidence",
    "dxcompass",
    "hud-render",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x0053bb50": (
        "CDXEngine__RenderOptionalFullscreenEffectPass",
        "void __fastcall CDXEngine__RenderOptionalFullscreenEffectPass(void * this)",
        {"cdxengine", "fullscreen-effect", "render-state", "ecx-only"},
        ("CDXEngine__Render", "render state 0x8f", "DAT_0063012c"),
    ),
    "0x0053bd60": (
        "CDXCompass__InitFields",
        "void * __fastcall CDXCompass__InitFields(void * this)",
        {"owner-corrected", "init-fields", "ring-texture", "ecx-only", "renamed"},
        ("CHud__Init", "CDXCompass__InitMarkerArrays", "this+0x3f10"),
    ),
    "0x0053bda0": (
        "CDXCompass__ReleaseDynamicResources",
        "void __fastcall CDXCompass__ReleaseDynamicResources(void * this)",
        {"owner-corrected", "resource-release", "ring-texture", "byte-sprite", "ecx-only", "renamed"},
        ("CHud__ShutDown", "CByteSprite", "this+0x3f10"),
    ),
    "0x0053c2e0": (
        "CDXCompass__BuildByteSpriteOverlayTexture",
        "void __thiscall CDXCompass__BuildByteSpriteOverlayTexture(void * this, void * battleEngineContext)",
        {"owner-corrected", "byte-sprite", "overlay-texture", "ring-texture", "ret-0x4", "renamed"},
        ("RET 0x4", "battle-engine context+0x2b8", "this+0x3c00"),
    ),
    "0x0053c510": (
        "CDXCompass__UpdateDynamicOverlayTexture",
        "void __thiscall CDXCompass__UpdateDynamicOverlayTexture(void * this, void * battleEngineContext)",
        {"owner-corrected", "dynamic-overlay", "overlay-texture", "ring-texture", "ret-0x4", "renamed"},
        ("RET 0x4", "CHud__ResolveOverlaySlotRenderMode", "this+0x3c14"),
    ),
    "0x0053cd30": (
        "CDXCompass__RenderWorldSpaceOverlay",
        "void __thiscall CDXCompass__RenderWorldSpaceOverlay(void * this, void * battleEngineContext)",
        {"owner-corrected", "world-space-overlay", "target-overlay", "compass-render", "ret-0x4", "renamed"},
        ("CHud__RenderTargetMarkers3D", "CDXCompass__Render", "RET 0x4"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully re'ed",
    "fully reverse-engineered",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value.startswith("<"):
        return value
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def read_tsv(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row[key]): row for row in rows}


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_count(path: Path) -> int:
    return len(read_tsv_rows(path))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    for token in tokens:
        if token not in text:
            failures.append(f"{label} missing token: {token}")


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(path)
    match = re.search(r"SUMMARY\s+([^\r\n]+)", text)
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
    for bad_token in ("FAIL:", "LockException", "Read-back mismatch", "Function not found", "Input file not found"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "logs" / "wave591_apply_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 5, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave591_apply.log",
        {"updated": 6, "skipped": 0, "renamed": 5, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "logs" / "wave591_apply_final_dry.log",
        {"updated": 0, "skipped": 6, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )


def check_post_exports(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post" / "metadata.tsv")
    tags = read_tsv(BASE / "post" / "tags.tsv")
    if len(metadata) != 6:
        failures.append(f"metadata row count mismatch: {len(metadata)}")
    if len(tags) != 6:
        failures.append(f"tag row count mismatch: {len(tags)}")

    for address, (name, signature, extra_tags, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        if row is None:
            failures.append(f"{address} missing from post metadata")
            continue
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        if row["status"] != "OK":
            failures.append(f"{address} metadata status mismatch: {row['status']}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address} comment overclaims: {token}")

        tag_row = tags.get(address)
        if tag_row is None:
            failures.append(f"{address} missing from post tags")
            continue
        actual_tags = set(filter(None, tag_row["tags"].split(";")))
        expected_tags = COMMON_TAGS | extra_tags
        missing = expected_tags - actual_tags
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")

    expected_counts = {
        "xrefs.tsv": row_count(BASE / "post" / "xrefs.tsv"),
        "instructions.tsv": row_count(BASE / "post" / "instructions.tsv"),
        "decompile/index.tsv": row_count(BASE / "post" / "decompile" / "index.tsv"),
        "decompile/callers/index.tsv": row_count(BASE / "post" / "decompile" / "callers" / "index.tsv"),
        "callsite_instructions.tsv": row_count(BASE / "post" / "callsite_instructions.tsv"),
        "proof_instructions.tsv": row_count(BASE / "post" / "proof_instructions.tsv"),
        "c510_ret_check.tsv": row_count(BASE / "post" / "c510_ret_check.tsv"),
    }
    expected = {
        "xrefs.tsv": 6,
        "instructions.tsv": 2046,
        "decompile/index.tsv": 6,
        "decompile/callers/index.tsv": 4,
        "callsite_instructions.tsv": 246,
        "proof_instructions.tsv": 726,
        "c510_ret_check.tsv": 1101,
    }
    for label, expected_value in expected.items():
        if expected_counts[label] != expected_value:
            failures.append(f"post {label} row count mismatch: {expected_counts[label]} != {expected_value}")


def check_xrefs(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post" / "xrefs.tsv")
    actual = {
        (
            normalize_address(row["target_addr"]),
            row["target_name"],
            normalize_address(row["from_addr"]),
            normalize_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in rows
    }
    expected = {
        ("0x0053bb50", "CDXEngine__RenderOptionalFullscreenEffectPass", "0x0053ec6a", "0x0053e2e0", "CDXEngine__Render", "UNCONDITIONAL_CALL"),
        ("0x0053bd60", "CDXCompass__InitFields", "0x0048149a", "0x00481450", "CHud__Init", "UNCONDITIONAL_CALL"),
        ("0x0053bda0", "CDXCompass__ReleaseDynamicResources", "0x00481b28", "0x00481b00", "CHud__ShutDown", "UNCONDITIONAL_CALL"),
        ("0x0053c2e0", "CDXCompass__BuildByteSpriteOverlayTexture", "0x0053cd5f", "0x0053cd30", "CDXCompass__RenderWorldSpaceOverlay", "UNCONDITIONAL_CALL"),
        ("0x0053c510", "CDXCompass__UpdateDynamicOverlayTexture", "0x0053cd67", "0x0053cd30", "CDXCompass__RenderWorldSpaceOverlay", "UNCONDITIONAL_CALL"),
        ("0x0053cd30", "CDXCompass__RenderWorldSpaceOverlay", "0x00484354", "0x00484340", "CHud__RenderTargetMarkers3D", "UNCONDITIONAL_CALL"),
    }
    missing = expected - actual
    if missing:
        failures.append(f"missing expected xrefs: {sorted(missing)}")


def check_instructions(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post" / "instructions.tsv")
    instructions = {
        (normalize_address(row["instruction_addr"]), row["function_name"], row["mnemonic"], row["operands"])
        for row in rows
    }
    expected = {
        ("0x0053bc27", "CDXEngine__RenderOptionalFullscreenEffectPass", "RET", ""),
        ("0x0053bd63", "CDXCompass__InitFields", "CALL", "0x00427200"),
        ("0x0053bd98", "CDXCompass__InitFields", "RET", ""),
        ("0x0053bdc0", "CDXCompass__ReleaseDynamicResources", "CALL", "0x004f27e0"),
        ("0x0053be03", "CDXCompass__ReleaseDynamicResources", "CALL", "0x00418480"),
        ("0x0053be33", "CDXCompass__ReleaseDynamicResources", "RET", ""),
        ("0x0053c50d", "CDXCompass__BuildByteSpriteOverlayTexture", "RET", "0x4"),
        ("0x0053cd5f", "CDXCompass__RenderWorldSpaceOverlay", "CALL", "0x0053c2e0"),
        ("0x0053cd67", "CDXCompass__RenderWorldSpaceOverlay", "CALL", "0x0053c510"),
        ("0x0053d0f3", "CDXCompass__RenderWorldSpaceOverlay", "CALL", "0x004881e0"),
        ("0x0053d1c1", "CDXCompass__RenderWorldSpaceOverlay", "CALL", "0x00427210"),
        ("0x0053d1e8", "CDXCompass__RenderWorldSpaceOverlay", "RET", "0x4"),
        ("0x0053d20f", "CDXCompass__RenderWorldSpaceOverlay", "RET", "0x4"),
    }
    missing = expected - instructions
    if missing:
        failures.append(f"missing expected instructions: {sorted(missing)}")

    c510_rows = read_tsv_rows(BASE / "post" / "c510_ret_check.tsv")
    c510 = {
        (normalize_address(row["instruction_addr"]), row["function_name"], row["mnemonic"], row["operands"])
        for row in c510_rows
    }
    if ("0x0053cd21", "CDXCompass__UpdateDynamicOverlayTexture", "RET", "0x4") not in c510:
        failures.append("missing CDXCompass__UpdateDynamicOverlayTexture RET 0x4 proof")


def check_queue_and_backup(failures: list[str]) -> None:
    queue = json.loads(read_text(QUEUE_JSON))
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 3066,
        "undefinedSignatureCount": 1347,
        "paramSignatureCount": 1106,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key, value in expected_quality.items():
        if quality.get(key) != value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {value}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0053d3a0" or head.get("name") != "CLTShell__ReleaseHudRefAndTargetHandle":
        failures.append(f"queue head mismatch: {head}")

    summary = json.loads(read_text(BACKUP_SUMMARY))
    if summary.get("BackupPath") != r"[maintainer-local-ghidra-backup-root]\BEA_20260519-130808_post_wave591_dxcompass_hud_head_verified":
        failures.append(f"backup path mismatch: {summary.get('BackupPath')}")
    expected_backup = {
        "FileCount": 19,
        "TotalBytes": 160959367,
        "MissingCount": 0,
        "ExtraCount": 0,
        "DiffCount": 0,
        "ManifestHash": "5713ad6ccec91519996a5c085677773276fc00bed3385be1e4f67fdf89bacb14",
    }
    for key, value in expected_backup.items():
        if summary.get(key) != value:
            failures.append(f"backup {key} mismatch: {summary.get(key)} != {value}")


def check_docs(failures: list[str]) -> None:
    docs = {
        "public note": read_text(PUBLIC_NOTE),
        "function index": read_text(FUNCTION_INDEX),
        "DXCompass doc": read_text(DXCOMPASS_DOC),
        "engine doc": read_text(ENGINE_DOC),
        "GHIDRA reference": read_text(GHIDRA_REFERENCE),
        "campaign": read_text(CAMPAIGN),
        "backlog": read_text(BACKLOG),
        "ledger": read_text(LEDGER),
        "attempt log": read_text(ATTEMPT_LOG),
    }
    for label, text in docs.items():
        require_tokens(
            label,
            text,
            (
                "Wave591",
                "CDXCompass__RenderWorldSpaceOverlay",
                "CDXCompass__BuildByteSpriteOverlayTexture",
                "CDXCompass__UpdateDynamicOverlayTexture",
                "0x0053d3a0 CLTShell__ReleaseHudRefAndTargetHandle",
            ),
            failures,
        )
    require_tokens(
        "DXCompass doc",
        docs["DXCompass doc"],
        (
            "CDXCompass__InitFields",
            "CDXCompass__ReleaseDynamicResources",
            "RET 0x4",
            "CHud+0x60",
        ),
        failures,
    )
    require_tokens(
        "engine doc",
        docs["engine doc"],
        ("CDXEngine__RenderOptionalFullscreenEffectPass", "render state 0x8f", "DAT_0063012c"),
        failures,
    )
    for label, text in docs.items():
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{label} overclaims: {token}")


def run_checks() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_post_exports(failures)
        check_xrefs(failures)
        check_instructions(failures)
        check_queue_and_backup(failures)
        check_docs(failures)
    except Exception as exc:  # noqa: BLE001 - CLI should report all unexpected proof failures.
        failures.append(f"unexpected error: {exc}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run checks")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    failures = run_checks()
    if failures:
        print("Wave591 DXCompass HUD-head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave591 DXCompass HUD-head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
