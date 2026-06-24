#!/usr/bin/env python3
"""Validate the Wave400 HUD-head Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "hud-head-wave400" / "current"

COMMON_TAGS = {"static-reaudit", "hud-head-wave400", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    instruction_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "instructionTokens": instruction_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00481400": target(
        "CHud__ctor_base",
        "void * __thiscall CHud__ctor_base(void * this)",
        ["CHud constructor/base init", "active-reader cells at +0x9c", "component/compass slots", "six HUD state flags", "CDXEngine owner label", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["eh_vector_constructor_iterator", "CGenericActiveReader__ctor_Zero", "this + 0x9c", "this + 0x1fc", "return"],
        ["LEA\tEAX, [ESI + 0x9c]", "MOV\tdword ptr [ESI + 0x1fc], EAX", "STOSD.REP"],
        ["hud", "constructor", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CDXEngine__InitLandscapeTextureTables"],
    ),
    "0x00481450": target(
        "CHud__Init",
        "void __thiscall CHud__Init(void * this)",
        ["allocates compass/BattleLine HUD subobjects", "loads text string ids", "sets initialized flag", "CGame__Init with the HUD singleton", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["OID__AllocObject(0x3f14", "CDXCompass__InitMarkerArrays", "CDXBattleLine__Constructor", "CText__GetStringById"],
        ["0x00481450", "PUSH\t0x5d2d2c", "MOV\tdword ptr FS:[0x0], ESP"],
        ["hud", "init", "signature-corrected", "comment-hardened"],
        ["CGame__Init"],
    ),
    "0x004815c0": target(
        "CHud__Reset",
        "void __thiscall CHud__Reset(void * this)",
        ["reseeds six HUD flags", "screen marker arrays", "objective/indicator state", "CGame__InitRestartLoop with the HUD singleton", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["this + 0x34", "0xc1200000", "0xc61c4000", "0x3f800000"],
        ["0x004815c0", "MOV\tEDX, ECX", "RET"],
        ["hud", "reset", "signature-corrected", "comment-hardened"],
        ["CGame__InitRestartLoop"],
    ),
    "0x00481650": target(
        "CHud__LoadTextures",
        "void __thiscall CHud__LoadTextures(void * this)",
        ["resolves crosshair/radar/weapon/objective/speaker HUD textures", "delegates compass and battleline texture loading", "CGame__RunLevel with the HUD singleton", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["s_hud_Crosshair_Outline_tga", "s_hud_speaker_1d_tga", "s_hud_v2_ObjectiveLeft_tga", "CDXCompass__LoadTextures", "CDXBattleLine__LoadTextures"],
        ["0x00481650", "PUSH\tESI", "RET"],
        ["hud", "textures", "signature-corrected", "comment-hardened"],
        ["CGame__RunLevel"],
    ),
    "0x00481af0": target(
        "CHud__PostLoadProcess",
        "int __thiscall CHud__PostLoadProcess(void * this)",
        ["tail-jumps through the BattleLine object at +0x30", "CDXBattleLine__Setup", "tests the EAX return", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["CDXBattleLine__Setup"],
        ["0x00481af0", "MOV\tECX, dword ptr [ECX + 0x30]", "JMP\t0x0053a280"],
        ["hud", "postload", "signature-corrected", "comment-hardened"],
        ["CGame__PostLoadProcess"],
    ),
    "0x00481b00": target(
        "CHud__ShutDown",
        "void __thiscall CHud__ShutDown(void * this)",
        ["clears the BattleLine object", "destroys compass textures", "frees compass/BattleLine allocations", "releases HUD texture refs and speaker array", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["CDXCompass__DestroyTextures", "CHud__FreeObjectIfPresent", "CHud__DecrementCounter9C", "this + 0x178"],
        ["0x00481b00", "PUSH\tESI", "RET"],
        ["hud", "shutdown", "signature-corrected", "comment-hardened"],
        ["0046c9ac"],
    ),
    "0x00481f40": target(
        "CHud__SetHudComponent",
        "void __thiscall CHud__SetHudComponent(void * this, char * component_name, byte slot_flag)",
        ["cutscene caller-driven HUD component swap", "destroys pending/current slots +0x200/+0x1fc", "allocates CHudComponent from component_name", "slot flag to select", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["CHudComponent__RequestDestroy", "CHudComponent__ctor", "slot_flag", "component_name"],
        ["MOV\tAL, byte ptr [ESP + 0x18]", "MOV\tdword ptr [ESI + 0x200], 0x0", "MOV\tdword ptr [ESI + 0x1fc], 0x0"],
        ["hud", "component-swap", "signature-corrected", "comment-hardened"],
        ["CCutscene__Start", "CCutscene__Stop", "CCutscene__Update"],
    ),
    "0x00482050": target(
        "CHud__PromotePendingHudComponent",
        "void __thiscall CHud__PromotePendingHudComponent(void * this)",
        ["CDXEngine owner label", "PostRender passes the HUD singleton", "requests current component destroy through vfunc", "promotes +0x200 pending component into +0x1fc active slot", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["this + 0x200", "this + 0x1fc", "+ 4) + 4", "return"],
        ["MOV\tdword ptr [ESI + 0x200], 0x0", "MOV\tdword ptr [ESI + 0x1fc], ECX", "RET"],
        ["hud", "component-swap", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CDXEngine__PostRender"],
    ),
    "0x00482090": target(
        "HudRenderState__ApplyOverlaySpriteState",
        "void __cdecl HudRenderState__ApplyOverlaySpriteState(void)",
        ["corrects overly narrow CExplosionInitThing owner label", "shared HUD/message/compass/battleline overlay render-state setup", "sets blend/texture-stage/mip/z/fog state", "applies pending render state", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["RenderState_Set(0x13,5)", "D3DStateCache__SetState114Raw", "D3DStateCache__SetMipFilterPoint", "CDXEngine__ApplyPendingRenderState"],
        ["MOV\tbyte ptr [0x009c68ac], 0x0", "MOV\tbyte ptr [0x009c690d], 0x1", "CALL\t0x00550d50"],
        ["hud-render-state", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CMessageLog__Render", "CDXCompass__Render", "CDXEngine__RenderBattleLineAndInfluenceOverlay"],
    ),
    "0x004821b0": target(
        "CDXCompass__ApplyRenderStateModulate",
        "void __cdecl CDXCompass__ApplyRenderStateModulate(void)",
        ["compass render helper", "sets render states 0x13/0x14 to 2/2", "applies pending render state", "runtime compass behavior", "rebuild parity remain unproven"],
        ["RenderState_Set(0x13,2)", "RenderState_Set(0x14,2)", "CDXEngine__ApplyPendingRenderState"],
        ["0x004821b0", "PUSH\t0x2", "CALL\t0x00550d50"],
        ["dxcompass", "render-state", "signature-corrected", "comment-hardened"],
        ["CDXCompass__Render"],
    ),
    "0x004821e0": target(
        "CDXCompass__ApplyRenderStateAdditive",
        "void __cdecl CDXCompass__ApplyRenderStateAdditive(void)",
        ["compass render helper", "sets render states 0x13/0x14 to 5/6", "applies pending render state", "runtime compass behavior", "rebuild parity remain unproven"],
        ["RenderState_Set(0x13,5)", "RenderState_Set(0x14,6)", "CDXEngine__ApplyPendingRenderState"],
        ["0x004821e0", "PUSH\t0x6", "CALL\t0x00550d50"],
        ["dxcompass", "render-state", "signature-corrected", "comment-hardened"],
        ["CDXCompass__Render"],
    ),
    "0x00482210": target(
        "CHud__RenderSegmentedMeterBar",
        "void __thiscall CHud__RenderSegmentedMeterBar(void * this, float x, float y, float width, float scale, float fill_fraction)",
        ["CDXEngine owner label", "draws segmented objective/message meter pieces", "CHud texture refs +0x154/+0x158/+0x160/+0x164", "controller slot status panel and message box overlay", "callers ignore return", "runtime HUD behavior", "rebuild parity remain unproven"],
        ["CVBufTexture__DrawSpriteEx", "this + 0x154", "this + 0x158", "this + 0x160", "this + 0x164"],
        ["MOV\tEDI, ECX", "FLD\tfloat ptr [ESP + 0x2c]", "MOV\tdword ptr [ESP + 0x2c], 0x41200000"],
        ["hud", "meter-render", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CExplosionInitThing__RenderControllerSlotStatusPanel", "CDXEngine__RenderMessageBoxOverlay"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 12, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 4, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 12, "skipped": 0, "created": 0, "would_create": 0, "renamed": 4, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime hud behavior proven",
    "runtime compass behavior proven",
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
        for key in ("address", "target_addr", "from_function_addr", "function_entry", "entry_addr"):
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
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "created": int(match.group(3)),
        "would_create": int(match.group(4)),
        "renamed": int(match.group(5)),
        "would_rename": int(match.group(6)),
        "missing": int(match.group(7)),
        "bad": int(match.group(8)),
    }


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    failures: list[str] = []
    metadata_rows = read_tsv(args.metadata)
    tags_rows = read_tsv(args.tags)
    xref_text = read_text(args.xrefs)
    instruction_text = read_text(args.instructions)
    public_note_text = read_text(args.public_note)

    if not metadata_rows:
        failures.append(f"missing or empty metadata: {args.metadata}")
    if not tags_rows:
        failures.append(f"missing or empty tags: {args.tags}")
    if not xref_text:
        failures.append(f"missing or empty xrefs: {args.xrefs}")
    if not instruction_text:
        failures.append(f"missing or empty instructions: {args.instructions}")
    if not public_note_text:
        failures.append(f"missing or empty public note: {args.public_note}")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: expected name {spec['name']}, got {row.get('name')}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: expected signature {spec['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present in comment: {token!r}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            tags = parse_tags(tag_row.get("tags", ""))
            for tag in spec["tags"]:  # type: ignore[index]
                if str(tag) not in tags:
                    failures.append(f"{address}: missing tag {tag!r}")

        decompile = decompile_text_for(args.decompile_dir, address)
        if not decompile:
            failures.append(f"{address}: missing decompile export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")
        for token in spec["instructionTokens"]:  # type: ignore[index]
            if not token_present(instruction_text, str(token)):
                failures.append(f"{address}: missing instruction token {token!r}")
        for token in spec["xrefTokens"]:  # type: ignore[index]
            if not token_present(xref_text, str(token)):
                failures.append(f"{address}: missing xref token {token!r}")

    for token in (
        "0x00481400",
        "0x00481450",
        "0x004815c0",
        "0x00481650",
        "0x00481af0",
        "0x00481b00",
        "0x00481f40",
        "0x00482050",
        "0x00482090",
        "0x004821b0",
        "0x004821e0",
        "0x00482210",
        "CHud__ctor_base",
        "CHud__Init",
        "CHud__Reset",
        "CHud__LoadTextures",
        "CHud__PostLoadProcess",
        "CHud__ShutDown",
        "CHud__SetHudComponent",
        "CHud__PromotePendingHudComponent",
        "HudRenderState__ApplyOverlaySpriteState",
        "CDXCompass__ApplyRenderStateModulate",
        "CDXCompass__ApplyRenderStateAdditive",
        "CHud__RenderSegmentedMeterBar",
        "does not prove runtime HUD behavior",
        "does not prove concrete CHud layout",
        "does not prove rebuild parity",
    ):
        if not token_present(public_note_text, token):
            failures.append(f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        if token_present(public_note_text, token):
            failures.append(f"public note overclaim token present: {token!r}")

    dry_summary = parse_summary(read_text(args.dry_log))
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, got {dry_summary}")
    apply_log_text = read_text(args.apply_log)
    apply_summary = parse_summary(apply_log_text)
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, got {apply_summary}")
    if "REPORT: Save succeeded" not in apply_log_text:
        failures.append("apply log missing REPORT: Save succeeded")

    report = {
        "schema": "ghidra-hud-head-wave400.v1",
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "targets": len(TARGETS),
        "failures": failures,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
    }
    return report, 0 if not failures else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_after.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_hud_head_wave400_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "hud-head-wave400.json")
    parser.add_argument("--check", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report, status = validate(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        print(f"status={report['status']} targets={report['targets']} failures={len(report['failures'])} out={args.out}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
