#!/usr/bin/env python3
"""Validate the Wave411 HUD overlay helper Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave411_hud_overlay_helpers" / "current"

COMMON_TAGS = {"static-reaudit", "hud-overlay-helpers-wave411", "retail-binary-evidence"}

TARGETS: dict[str, dict[str, object]] = {
    "0x00483530": {
        "name": "CHud__RenderControllerSlotStatusPanel",
        "signature": "void __thiscall CHud__RenderControllerSlotStatusPanel(void * this)",
        "commentTokens": [
            "CHud overlay helper",
            "controller slot status panel",
            "CHud__RenderOverlayForViewpoint",
            "CHud__RenderSegmentedMeterBar",
            "HUD fields +0x68/+0x94/+0x98/+0xac",
            "runtime HUD behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "CHud__RenderSegmentedMeterBar",
            "CPlatform__Font",
            "CDXFont__DrawTextDynamic",
            "GetSlotTimerValueByMode",
        ],
        "tags": ["hud", "overlay", "controller-status", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint", 1),
    },
    "0x00484340": {
        "name": "CHud__RenderTargetMarkers3D",
        "signature": "void __thiscall CHud__RenderTargetMarkers3D(void * this)",
        "commentTokens": [
            "CHud overlay helper",
            "3D target marker sprites",
            "CHud__RenderOverlayForViewpoint",
            "CHud fields +0x50/+0x54/+0x58",
            "CBattleEngine__GetInterpolatedAutoAimPos",
            "runtime HUD behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "HudRenderState__ApplyOverlaySpriteState",
            "CDXBattleLine__RenderWorldSpaceOverlay",
            "CBattleEngine__GetInterpolatedAutoAimPos",
            "CVBufTexture__DrawSpriteEx",
        ],
        "tags": ["hud", "overlay", "target-markers", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint", 1),
    },
    "0x00484c50": {
        "name": "CHud__RenderTacticalRadarContacts",
        "signature": "void __thiscall CHud__RenderTacticalRadarContacts(void * this)",
        "commentTokens": [
            "CHud tactical radar overlay helper",
            "CHud__RenderOverlayForViewpoint",
            "partitions visible units into temporary pointer sets",
            "CHud__SelectMarkerTextureIndexByUnitFlags",
            "HudOverlay__DrawSpriteQuad",
            "runtime HUD behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "HudRenderState__ApplyOverlaySpriteState",
            "CGame__IsMultiplayer",
            "CBattleEngine__GetInterpolatedEulerOrientation",
            "CHud__SelectMarkerTextureIndexByUnitFlags",
            "HudOverlay__DrawSpriteQuad",
            "CSPtrSet__Clear",
        ],
        "tags": ["hud", "overlay", "tactical-radar", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint", 1),
    },
    "0x004857e0": {
        "name": "HudOverlay__DrawSpriteQuad",
        "signature": "void __cdecl HudOverlay__DrawSpriteQuad(float x, float y, void * texture, float argb_tint_bits)",
        "commentTokens": [
            "HUD overlay sprite helper",
            "owner-neutral",
            "CVBufTexture__DrawSpriteEx",
            "called repeatedly by CHud__RenderTacticalRadarContacts",
            "fixed depth 0.011",
            "exact tint semantics remain unproven",
        ],
        "decompileTokens": [
            "CVBufTexture__DrawSpriteEx",
            "argb_tint_bits",
            "0.011",
        ],
        "tags": ["hud", "overlay", "sprite-helper", "signature-hardened", "comment-hardened"],
        "xref": ("0x00484c50", "CHud__RenderTacticalRadarContacts", 7),
    },
    "0x00485830": {
        "name": "CHud__SelectMarkerTextureIndexByUnitFlags",
        "signature": "int __thiscall CHud__SelectMarkerTextureIndexByUnitFlags(void * this, void * unit)",
        "commentTokens": [
            "CHud tactical marker texture selector",
            "one stack argument",
            "RET 0x4",
            "unit flags at +0x34",
            "CHud texture slots +0x1a0/+0x1a4/+0x1a8",
            "exact unit layout",
            "runtime HUD behavior",
        ],
        "decompileTokens": [
            "unit",
            "0x34",
            "0x1a0",
            "0x1a4",
            "0x1a8",
        ],
        "tags": ["hud", "overlay", "marker-texture", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x00484c50", "CHud__RenderTacticalRadarContacts", 4),
    },
    "0x004858d0": {
        "name": "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
        "signature": "void __thiscall CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this)",
        "commentTokens": [
            "CHud overlay helper",
            "objective progress gauge",
            "heading needle",
            "CHud__RenderOverlayForViewpoint",
            "CBattleEngine__GetWeaponCharge",
            "CBattleEngine__GetInterpolatedEulerOrientation",
            "runtime HUD behavior",
        ],
        "decompileTokens": [
            "HudRenderState__ApplyOverlaySpriteState",
            "CBattleEngine__GetWeaponCharge",
            "CBattleEngine__GetInterpolatedEulerOrientation",
            "CVBufTexture__DrawSpriteEx",
        ],
        "tags": ["hud", "overlay", "objective", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint", 1),
    },
    "0x00485d50": {
        "name": "CHud__RenderObjectiveStatusPanel",
        "signature": "void __thiscall CHud__RenderObjectiveStatusPanel(void * this)",
        "commentTokens": [
            "CHud overlay helper",
            "objective and weapon status panel",
            "CHud__RenderOverlayForViewpoint",
            "CBattleEngine__CountFlag9CBySelectionMode",
            "CBattleEngine__GetWeaponIconName",
            "CBattleEngine__GetWeaponName",
            "runtime HUD behavior",
        ],
        "decompileTokens": [
            "HudRenderState__ApplyOverlaySpriteState",
            "CBattleEngine__CountFlag9CBySelectionMode",
            "CBattleEngine__GetWeaponIconName",
            "CBattleEngine__GetWeaponName",
            "CGame__GetPlayerLives",
            "CDXFont__DrawTextDynamic",
        ],
        "tags": ["hud", "overlay", "objective", "weapon-status", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint", 1),
    },
    "0x00486940": {
        "name": "CHud__RenderObjectiveSlotFillPanel",
        "signature": "void __thiscall CHud__RenderObjectiveSlotFillPanel(void * this)",
        "commentTokens": [
            "CHud overlay helper",
            "weapon energy/ammo slot fill panel",
            "CHud__RenderOverlayForViewpoint",
            "CBattleEngine__IsEnergyWeapon",
            "CBattleEngine__GetWeaponAmmoPercentage",
            "CBattleEngine__GetWeaponAmmoCount",
            "runtime HUD behavior",
        ],
        "decompileTokens": [
            "HudRenderState__ApplyOverlaySpriteState",
            "CBattleEngine__IsEnergyWeapon",
            "CBattleEngine__GetWeaponAmmoPercentage",
            "CBattleEngine__IsWeaponOverheated",
            "CBattleEngine__GetWeaponAmmoCount",
        ],
        "tags": ["hud", "overlay", "objective", "weapon-status", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint", 1),
    },
    "0x00486e00": {
        "name": "CHud__RenderWorldTargetSprites",
        "signature": "void __thiscall CHud__RenderWorldTargetSprites(void * this)",
        "commentTokens": [
            "CHud overlay helper",
            "world-space target and lock sprites",
            "CHud__RenderOverlayForViewpoint",
            "CHud fields +0x50/+0x54/+0x58",
            "CUnitAI__GetWorldPositionForTargeting",
            "runtime HUD behavior",
            "rebuild parity remain unproven",
        ],
        "decompileTokens": [
            "HudRenderState__ApplyOverlaySpriteState",
            "CUnitAI__GetWorldPositionForTargeting",
            "CLockInfo__GetLockPercentage",
            "CVBufTexture__DrawSpriteEx",
            "CDXEngine__PushTransformState",
        ],
        "tags": ["hud", "overlay", "world-targets", "owner-corrected", "signature-hardened", "comment-hardened"],
        "xref": ("0x004879e0", "CHud__RenderOverlayForViewpoint", 1),
    },
}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 9,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 9,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 9,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 9,
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


def matching_xrefs(xrefs: list[dict[str, str]], address: str, from_addr: str, from_function: str) -> list[dict[str, str]]:
    return [
        row
        for row in xrefs
        if row.get("target_addr") == normalize_address(address)
        and row.get("from_function_addr") == normalize_address(from_addr)
        and row.get("from_function") == from_function
        and row.get("ref_type") == "UNCONDITIONAL_CALL"
    ]


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

        from_addr, from_function, min_count = expected["xref"]  # type: ignore[misc]
        found = matching_xrefs(xrefs, address, str(from_addr), str(from_function))
        if len(found) < int(min_count):
            failures.append(f"{address} expected at least {min_count} xref(s) from {from_function} at {from_addr}, found {len(found)}")

    caller = decompile_text_for(base / "caller_decompile_after", "0x004879e0")
    if not caller:
        failures.append("missing CHud__RenderOverlayForViewpoint caller decompile")
    else:
        for token in (
            "CHud__RenderWorldTargetSprites",
            "CHud__RenderControllerSlotStatusPanel",
            "CHud__RenderTargetMarkers3D",
            "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
            "CHud__RenderObjectiveStatusPanel",
            "CHud__RenderObjectiveSlotFillPanel",
            "CHud__RenderTacticalRadarContacts",
        ):
            if not token_present(caller, token):
                failures.append(f"caller decompile missing token: {token}")

    tactical = decompile_text_for(base / "decompile_after", "0x00484c50")
    if tactical:
        for token in ("CHud__SelectMarkerTextureIndexByUnitFlags", "HudOverlay__DrawSpriteQuad"):
            if not token_present(tactical, token):
                failures.append(f"tactical radar decompile missing helper token: {token}")

    return failures


def write_result(base: Path, status: str, failures: list[str]) -> None:
    out = base / "hud-overlay-helpers-wave411-result.json"
    out.write_text(
        json.dumps(
            {
                "status": status,
                "wave": "wave411",
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
