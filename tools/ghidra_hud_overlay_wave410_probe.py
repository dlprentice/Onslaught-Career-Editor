#!/usr/bin/env python3
"""Validate the Wave410 HUD overlay Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave410_target_indicator_overlay" / "current"

COMMON_TAGS = {"static-reaudit", "hud-overlay-wave410", "retail-binary-evidence"}


TARGETS: dict[str, dict[str, object]] = {
    "0x00487bc0": {
        "name": "CHud__RenderOverlay",
        "signature": "void __thiscall CHud__RenderOverlay(void * this)",
        "commentTokens": [
            "CHud::RenderOverlay",
            "CDXEngine__PostRender",
            "HUD singleton 0x8aa4e8",
            "source calls HUD.RenderOverlay",
            "runtime HUD overlay behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "CHud__RenderOverlayForViewpoint",
            "CGame__GetCamera",
            "RenderState_Set(0xe,1)",
            "D3DStateCache__SetMipFilterLinear",
        ],
        "tags": ["hud", "overlay", "source-parity", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x0053ecc0", "CDXEngine__PostRender"),
    },
    "0x004879e0": {
        "name": "CHud__RenderOverlayForViewpoint",
        "signature": "void __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float param_3)",
        "commentTokens": [
            "per-viewpoint CHud overlay renderer",
            "clips the overlay marker rectangle",
            "CHud fields +0x50/+0x54/+0x58",
            "target-indicator",
            "tactical radar overlay helpers",
            "runtime HUD overlay behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "CEngine__SelectViewpoint",
            "HudRenderState__ApplyOverlaySpriteState",
            "CHud__RenderTargetIndicatorOverlay",
            "CExplosionInitThing__RenderObjectiveStatusPanel",
            "CExplosionInitThing__RenderTacticalRadarContacts",
        ],
        "tags": ["hud", "overlay", "viewpoint", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x00487bc0", "CHud__RenderOverlay"),
    },
    "0x00482590": {
        "name": "CHud__RenderTargetIndicatorOverlay",
        "signature": "void __thiscall CHud__RenderTargetIndicatorOverlay(void * this)",
        "commentTokens": [
            "CHud target indicator overlay helper",
            "CHud__RenderOverlayForViewpoint",
            "active/last target reader",
            "CHud texture +0x168",
            "Thunderhead mesh-specific miniature path",
            "runtime HUD behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "CGenericActiveReader__SetReader",
            "CVBufTexture__DrawSpriteEx",
            "s_m_thunderhead_msh_0062d304",
            "D3DDevice__SetViewport",
            "CSphere__RenderAnimatedRecursive",
            "CSphere__GetRootSubtreeHealthIfAnyActive",
        ],
        "tags": ["hud", "overlay", "target-indicator", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint"),
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
        for key in ("address", "target_addr", "from_function_addr", "function_entry"):
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


def check_targets(base: Path) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags_rows = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    decompile_dir = base / "decompile_after"

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

        from_addr, from_function = expected["xref"]  # type: ignore[misc]
        matching_xrefs = [
            row
            for row in xrefs
            if row.get("target_addr") == normalize_address(address)
            and row.get("from_function_addr") == normalize_address(str(from_addr))
            and row.get("from_function") == from_function
            and row.get("ref_type") == "UNCONDITIONAL_CALL"
        ]
        if len(matching_xrefs) != 1:
            failures.append(f"{address} expected one xref from {from_function} at {from_addr}, found {len(matching_xrefs)}")

    post_render = decompile_text_for(base / "outer_caller_decompile_after", "0x0053ecc0")
    if not post_render:
        failures.append("missing CDXEngine__PostRender outer caller decompile")
    else:
        for token in ("CHud__RenderOverlay(&DAT_008aa4e8)", "CHud__PromotePendingHudComponent(&DAT_008aa4e8)"):
            if not token_present(post_render, token):
                failures.append(f"outer caller decompile missing token: {token}")

    return failures


def write_result(base: Path, status: str, failures: list[str]) -> None:
    out = base / "hud-overlay-wave410-result.json"
    out.write_text(
        json.dumps(
            {
                "status": status,
                "wave": "wave410",
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
