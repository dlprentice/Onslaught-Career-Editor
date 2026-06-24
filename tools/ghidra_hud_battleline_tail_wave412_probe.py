#!/usr/bin/env python3
"""Validate the Wave412 HUD battleline/render-tail Ghidra correction tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave412_render_overlay_tail" / "current"

COMMON_TAGS = {"static-reaudit", "hud-battleline-tail-wave412", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x00487d10": {
        "name": "CHud__RenderBattleline",
        "signature": "void __thiscall CHud__RenderBattleline(void * this, void * viewport)",
        "commentTokens": [
            "CHud::RenderBattleline(viewport)",
            "CDXEngine__PostRender",
            "HUD singleton 0x8aa4e8",
            "one viewport stack argument",
            "CDXEngine__RenderBattleLinePulseSprites",
            "CDXBattleLine influence-overlay",
            "runtime HUD behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "HudRenderState__ApplyOverlaySpriteState",
            "CDXEngine__RenderMessageBoxOverlay",
            "CDXEngine__RenderBattleLinePulseSprites",
            "CInfluenceMapManager__IsEmpty",
            "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices",
            "CDXBattleLine__Render",
        ],
        "tags": ["hud", "battleline", "source-parity", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xrefs": [("0x0053ecc0", "CDXEngine__PostRender", 1)],
    },
    "0x00488090": {
        "name": "CHud__RenderActiveHudComponentPass",
        "signature": "void __thiscall CHud__RenderActiveHudComponentPass(void * this)",
        "commentTokens": [
            "CHud active component render pass",
            "CDXEngine__PostRender",
            "HUD singleton 0x8aa4e8",
            "active component slot +0x1fc",
            "CHudComponent__RenderPass",
            "+0x64 done flag",
            "runtime overlay behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite",
            "CHudComponent__RenderPass",
            "this + 0x1fc",
            "0x64",
        ],
        "tags": ["hud", "overlay", "hud-component", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xrefs": [("0x0053ecc0", "CDXEngine__PostRender", 1)],
    },
    "0x004881e0": {
        "name": "CHud__ResolveOverlaySlotRenderMode",
        "signature": "int __thiscall CHud__ResolveOverlaySlotRenderMode(void * this, int slot_index)",
        "commentTokens": [
            "CHud overlay slot render-mode helper",
            "CDXBattleLine__RenderWorldSpaceOverlay",
            "CDXCompass__Render",
            "CVBufTexture__UpdateDynamicOverlayTexture",
            "HUD singleton 0x8aa4e8",
            "one slot_index stack argument",
            "+0x34 + slot_index*4",
            "+0x4c",
            "runtime render behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "slot_index",
            "0x34",
            "0x4c",
            "return 1",
            "return 0",
        ],
        "tags": ["hud", "overlay", "render-mode", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xrefs": [
            ("0x0053cd30", "CDXBattleLine__RenderWorldSpaceOverlay", 1),
            ("0x00427210", "CDXCompass__Render", 2),
            ("0x0053c510", "CVBufTexture__UpdateDynamicOverlayTexture", 4),
        ],
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 3,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 3,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 3,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime hud behavior proven",
    "runtime overlay behavior proven",
    "runtime render behavior proven",
    "source identity proven",
    "concrete chud layout proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_function_addr", "function_entry", "instruction_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {
            "updated": -1,
            "skipped": -1,
            "created": -1,
            "would_create": -1,
            "renamed": -1,
            "would_rename": -1,
            "missing": -1,
            "bad": -1,
        }
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def compare_summary(failures: list[str], label: str, actual: dict[str, int], expected: dict[str, int]) -> None:
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            failures.append(f"{label} summary {key}: expected {expected_value}, got {actual_value}")


def instruction_rows_for(rows: list[dict[str, str]], target_addr: str) -> list[dict[str, str]]:
    wanted = normalize_address(target_addr)
    return [row for row in rows if row.get("target_addr") == wanted]


def has_callsite_shape(rows: list[dict[str, str]], target_addr: str, call_target: str, required_push: str | None) -> bool:
    target_rows = instruction_rows_for(rows, target_addr)
    has_ecx_hud = any(row.get("mnemonic") == "MOV" and token_present(row.get("operands", ""), "ECX, 0x8aa4e8") for row in target_rows)
    has_call = any(row.get("role") == "TARGET" and row.get("mnemonic") == "CALL" and token_present(row.get("operands", ""), call_target) for row in target_rows)
    has_push = True
    if required_push is not None:
        has_push = any(row.get("mnemonic") == "PUSH" and token_present(row.get("operands", ""), required_push) for row in target_rows)
    return has_ecx_hud and has_call and has_push


def check_xrefs(failures: list[str], address: str, expected: dict[str, object], xrefs: list[dict[str, str]]) -> None:
    for from_addr, from_function, expected_count in expected["xrefs"]:  # type: ignore[index]
        matches = [
            row
            for row in xrefs
            if row.get("target_addr") == normalize_address(address)
            and row.get("from_function_addr") == normalize_address(str(from_addr))
            and row.get("from_function") == from_function
            and row.get("ref_type") == "UNCONDITIONAL_CALL"
        ]
        if len(matches) != expected_count:
            failures.append(f"{address} expected {expected_count} xref(s) from {from_function} at {from_addr}, found {len(matches)}")


def check_targets(base: Path) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags_rows = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    decompile_dir = base / "decompile_after"
    post_render_callsites = read_tsv(base / "callsite_instructions_after.tsv")
    blend_callsites = read_tsv(base / "vbuf_blend_callsite_instructions_after.tsv")

    compare_summary(failures, "dry", parse_summary(read_text(base / "apply_dry.log")), EXPECTED_DRY)
    compare_summary(failures, "apply", parse_summary(read_text(base / "apply_apply.log")), EXPECTED_APPLY)

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address} missing metadata_after row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address} name expected {expected['name']}, got {row.get('name')}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address} signature expected {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} comment overclaims with token: {token}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address} missing tags_after row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing_tags = sorted(expected_tags - actual_tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {', '.join(missing_tags)}")

        decompile = decompile_text_for(decompile_dir, address)
        if not decompile:
            failures.append(f"{address} missing decompile_after text")
        else:
            for token in expected["decompileTokens"]:  # type: ignore[index]
                if not token_present(decompile, str(token)):
                    failures.append(f"{address} decompile missing token: {token}")

        check_xrefs(failures, address, expected, xrefs)

    if not has_callsite_shape(post_render_callsites, "0x0053ed79", "0x00487d10", "ESI"):
        failures.append("0x00487d10 callsite missing HUD singleton, call target, or viewport push evidence")
    if not has_callsite_shape(post_render_callsites, "0x0053ef26", "0x00488090", None):
        failures.append("0x00488090 callsite missing HUD singleton or call target evidence")
    for callsite, pushed in (("0x0053d0f3", "0x2"), ("0x004276b3", "EBP"), ("0x0053c7d4", "0x0")):
        if not has_callsite_shape(blend_callsites, callsite, "0x004881e0", pushed):
            failures.append(f"0x004881e0 callsite {callsite} missing HUD singleton, target call, or one-stack-arg evidence")

    return failures


def write_result(base: Path, status: str, failures: list[str]) -> None:
    out = base / "hud-battleline-tail-wave412-result.json"
    out.write_text(
        json.dumps(
            {
                "status": status,
                "wave": "wave412",
                "targets": sorted(TARGETS),
                "failures": failures,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    failures = check_targets(args.base)
    status = "PASS" if not failures else "FAIL"
    write_result(args.base, status, failures)
    print(status)
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
